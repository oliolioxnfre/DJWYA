"use client";
/* eslint-disable @typescript-eslint/no-explicit-any */

import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';

interface GraphNode extends d3.SimulationNodeDatum {
    id: string;
    name: string;
    slug?: string;
    description?: string;
    sonic_dna?: any;
    color?: string;
    childCount?: number;
    computedColor?: string; // Adding this to avoid 'any' casting later
}

interface Link extends d3.SimulationLinkDatum<GraphNode> {
    source: string | GraphNode;
    target: string | GraphNode;
    type: string;
    weight: number;
}

interface GraphData {
    nodes: GraphNode[];
    links: Link[];
}

export default function ForceGraph() {
    const containerRef = useRef<HTMLDivElement>(null);

    // D3 Refs to store selections and simulation for stable updates
    const nodeSelectionRef = useRef<any>(null);
    const linkSelectionRef = useRef<any>(null);
    const labelSelectionRef = useRef<any>(null);
    const simulationRef = useRef<any>(null);
    const zoomBehaviorRef = useRef<any>(null);

    const [data, setData] = useState<GraphData | null>(null);
    const [loading, setLoading] = useState(true);

    // Interaction States
    const [hoveredNode, setHoveredNode] = useState<GraphNode | null>(null);
    const [highlightMode, setHighlightMode] = useState<'ancestry' | 'neighborhood'>('ancestry');

    // Search States
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState<GraphNode[]>([]);
    const [isSearchFocused, setIsSearchFocused] = useState(false);
    const searchRef = useRef<HTMLDivElement>(null);

    // Load Data
    useEffect(() => {
        fetch('/api/graph')
            .then(res => res.json())
            .then((json: GraphData) => {
                setData(json);
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to load graph data", err);
                setLoading(false);
            });
    }, []);

    // Helper to calculate radius
    const getRadius = (d: any) => {
        const baseRadius = 8;
        const extraRadius = Math.sqrt(d.childCount || 0) * 4;
        return baseRadius + extraRadius;
    };

    // Search Logic
    useEffect(() => {
        if (!searchQuery.trim() || !data) {
            setSearchResults([]);
            return;
        }
        const query = searchQuery.toLowerCase();
        const filtered = data.nodes.filter(n =>
            n.name.toLowerCase().includes(query) ||
            (n.slug && n.slug.toLowerCase().includes(query))
        ).slice(0, 10);
        setSearchResults(filtered);
    }, [searchQuery, data]);

    // Handle clicking outside search
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
                setIsSearchFocused(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const zoomToNode = (nodeId: string) => {
        if (!containerRef.current || !data) return;

        const targetNode = simulationRef.current.nodes().find((n: any) => n.id === nodeId);
        if (!targetNode) return;

        const svg = d3.select(containerRef.current).select("svg");
        const width = containerRef.current.clientWidth;
        const height = containerRef.current.clientHeight;

        const transform = d3.zoomIdentity
            .translate(width / 2, height / 2)
            .scale(2)
            .translate(-targetNode.x, -targetNode.y);

        svg.transition()
            .duration(750)
            .call(zoomBehaviorRef.current.transform, transform);

        // Highlight the node temporarily
        setHoveredNode(targetNode);
        setIsSearchFocused(false);
        setSearchQuery(targetNode.name);
    };

    // SETUP EFFECT: Runs only when data changes
    useEffect(() => {
        if (!data || !containerRef.current) return;

        const width = containerRef.current.clientWidth;
        const height = containerRef.current.clientHeight;

        // Reset Container
        d3.select(containerRef.current).selectAll("*").remove();

        const zoom = d3.zoom<SVGSVGElement, unknown>().on("zoom", (e) => {
            g.attr("transform", e.transform);
        });
        zoomBehaviorRef.current = zoom;

        const svg = d3.select(containerRef.current)
            .append("svg")
            .attr("width", "100%")
            .attr("height", "100%")
            .attr("viewBox", `0 0 ${width} ${height}`)
            .style("background-color", "#0f0f13")
            .call(zoom)
            .on("dblclick.zoom", null);

        const g = svg.append("g");

        // Arrowheads
        svg.append("defs").selectAll("marker")
            .data(["parent", "influence"])
            .enter().append("marker")
            .attr("id", String)
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 15)
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr("fill", d => d === 'parent' ? "#6366f1" : "#10b981")
            .attr("opacity", 0.6);

        // Prep Data - Use spread for own properties, safer for D3/React
        const nodes: GraphNode[] = data.nodes.map(d => ({ ...d }));
        const links: Link[] = data.links.map(d => ({ ...d }));

        const childCountMap: Record<string, number> = {};
        links.forEach((l: any) => {
            const parentId = typeof l.target === 'string' ? l.target : (l.target as any).id;
            childCountMap[parentId] = (childCountMap[parentId] || 0) + 1;
        });

        nodes.forEach((n: any) => {
            n.childCount = childCountMap[n.id] || 0;
        });

        const GHOST_ROOT_COLOR = '#888888';

        // Build adjacency list (child_id -> [parent_ids])
        const parentMap: Record<string, string[]> = {};
        links.forEach((l: any) => {
            if (l.type === 'parent') {
                const sourceId = typeof l.source === 'string' ? l.source : (l.source as any).id;
                const targetId = typeof l.target === 'string' ? l.target : (l.target as any).id;

                if (!parentMap[sourceId]) parentMap[sourceId] = [];
                parentMap[sourceId].push(targetId);
            }
        });

        // Memoized Color & Depth Computation (DFS)
        const colorCache: Record<string, { color: string, depth: number }> = {};

        const computeNodeAppearance = (nodeId: string, visited = new Set<string>()): { color: string, depth: number } => {
            if (colorCache[nodeId]) return colorCache[nodeId];

            if (visited.has(nodeId)) return { color: GHOST_ROOT_COLOR, depth: 10 };
            visited.add(nodeId);

            const thisNode = nodes.find(n => n.id === nodeId);
            const parentIds = parentMap[nodeId] || [];

            // Case A: Hardcoded Pillar in DB (Any node with a 'color' set in Supabase)
            if (thisNode?.color) {
                const result = { color: thisNode.color, depth: 0 };
                colorCache[nodeId] = result;
                return result;
            }

            // Case B: Ghost Root (No parents and no color assigned)
            if (parentIds.length === 0) {
                const result = { color: GHOST_ROOT_COLOR, depth: 0 };
                colorCache[nodeId] = result;
                return result;
            }

            // Case C: Inheritance
            const parentResults = parentIds.map(pId => computeNodeAppearance(pId, new Set(visited)));

            // Filter out Ghost Roots for mixing unless ONLY ghost roots exist
            const coloredParents = parentResults.filter(r => r.color !== GHOST_ROOT_COLOR);
            const mixSources = coloredParents.length > 0 ? coloredParents : parentResults;

            // Depth is minimum distance to a root
            const depth = Math.min(...mixSources.map(r => r.depth)) + 1;

            // Blend colors in LAB space
            let finalColor = mixSources[0].color;
            if (mixSources.length > 1) {
                const labs = mixSources.map(s => d3.lab(s.color));
                const mixed = d3.lab(
                    labs.reduce((sum, l) => sum + l.l, 0) / labs.length,
                    labs.reduce((sum, l) => sum + l.a, 0) / labs.length,
                    labs.reduce((sum, l) => sum + l.b, 0) / labs.length
                );
                finalColor = mixed.formatHex();
            }

            const result = { color: finalColor, depth };
            colorCache[nodeId] = result;
            return result;
        };

        // Apply computation to all nodes
        nodes.forEach((n: any) => {
            const { color, depth } = computeNodeAppearance(n.id);

            // 5. Hierarchical Fading (The Depth Rule)
            // Roots = 100% saturation/luminance. Deeper = desaturated/darker.
            if (color !== GHOST_ROOT_COLOR) {
                const hsl = d3.hsl(color);
                // Cap depth effect so it doesn't go totally black (max depth effect = 5)
                const depthFactor = Math.min(depth, 5);

                // Reduce Luminance slightly (from ~0.5 down to ~0.3)
                hsl.l = Math.max(0.3, hsl.l - (depthFactor * 0.04));
                // Reduce Saturation slightly
                hsl.s = Math.max(0.4, hsl.s - (depthFactor * 0.08));

                n.computedColor = hsl.formatHex();
            } else {
                n.computedColor = GHOST_ROOT_COLOR;
            }
        });

        // Initialize Simulation
        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id((d: any) => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collide", d3.forceCollide().radius((d: any) => getRadius(d) + 12).iterations(3)); // increased padding

        simulationRef.current = simulation;

        // 1. Draw Links
        const link = g.append("g")
            .selectAll("line")
            .data(links)
            .join("line")
            .attr("stroke", d => d.type === 'parent' ? "#6366f1" : "#10b981")
            .attr("stroke-width", d => Math.max(0.5, d.weight * 2))
            .attr("marker-end", d => `url(#${d.type})`)
            .style("stroke-opacity", d => (d.type === 'parent' ? 0.3 : 0)); // Lower baseline opacity for links

        linkSelectionRef.current = link;

        // 2. Draw Nodes
        const node = g.append("g")
            .attr("stroke", "#0f0f13") // Dark stroke matches bg
            .attr("stroke-width", 2)
            .selectAll("circle")
            .data(nodes)
            .join("circle")
            .attr("r", d => getRadius(d))
            .attr("fill", (d: any) => d.computedColor)
            .style("cursor", "pointer")
            .call(d3.drag<SVGCircleElement, any>()
                .on("start", (event, d) => {
                    if (!event.active) simulation.alphaTarget(0.3).restart();
                    d.fx = d.x;
                    d.fy = d.y;
                })
                .on("drag", (event, d) => {
                    d.fx = event.x;
                    d.fy = event.y;
                })
                .on("end", (event, d) => {
                    if (!event.active) simulation.alphaTarget(0);
                    d.fx = null;
                    d.fy = null;
                }) as any
            );

        nodeSelectionRef.current = node;

        // 3. Draw Labels
        const label = g.append("g")
            .selectAll("text")
            .data(nodes)
            .join("text")
            .text(d => d.name)
            .attr("font-size", (d: any) => d.childCount > 5 ? "12px" : "9px") // Dynamic font size based on importance
            .attr("font-weight", (d: any) => d.childCount > 5 ? "bold" : "normal")
            .attr("dx", d => getRadius(d) + 5)
            .attr("dy", 4)
            .attr("fill", (d: any) => d.computedColor) // Text matches node color for cohesion
            .style("opacity", 0.8)
            .attr("pointer-events", "none");

        labelSelectionRef.current = label;

        // Events
        node
            .on("mouseover", (event, d) => setHoveredNode(d))
            .on("mouseout", () => setHoveredNode(null))
            .on("click", (event) => {
                event.stopPropagation();
                setHighlightMode(prev => prev === 'ancestry' ? 'neighborhood' : 'ancestry');
            });

        // Simulation Tick
        simulation.on("tick", () => {
            link
                .attr("x1", d => (d.source as any).x)
                .attr("y1", d => (d.source as any).y)
                .attr("x2", d => (d.target as any).x)
                .attr("y2", d => (d.target as any).y);

            node
                .attr("cx", d => (d as any).x)
                .attr("cy", d => (d as any).y);

            label
                .attr("x", d => (d as any).x)
                .attr("y", d => (d as any).y);
        });

        return () => {
            simulation.stop();
        };
    }, [data]);

    // UPDATE EFFECT: Handles visual highlights without restarting simulation
    useEffect(() => {
        if (!nodeSelectionRef.current || !linkSelectionRef.current || !labelSelectionRef.current) return;

        const node = nodeSelectionRef.current;
        const link = linkSelectionRef.current;
        const label = labelSelectionRef.current;

        if (!hoveredNode) {
            // Reset to default state - USE COMPUTED COLORS
            node.attr("fill", (n: any) => n.computedColor).attr("r", (d: any) => getRadius(d)).style("opacity", 1);
        link.style("stroke-opacity", (l: any) => l.type === 'parent' ? 0.3 : 0).style("stroke-width", (l: any) => Math.max(0.5, l.weight * 2));
            label.style("opacity", 1).attr("fill", (n: any) => n.computedColor);
            return;
        }

        // Identify highlighting set
        const highlightedNodeIds = new Set<string>();
        const highlightedLinks = new Set<any>();
        highlightedNodeIds.add(hoveredNode.id);

        if (highlightMode === 'ancestry') {
            const findAncestors = (nodeId: string, parentsOnly = false) => {
                link.each(function (l: any) {
                    const sourceId = typeof l.source === 'string' ? l.source : (l.source as any).id;
                    const targetId = typeof l.target === 'string' ? l.target : (l.target as any).id;
                    if (sourceId === nodeId) {
                        if (l.type === 'parent') {
                            if (!highlightedNodeIds.has(targetId)) {
                                highlightedNodeIds.add(targetId);
                                highlightedLinks.add(l);
                                findAncestors(targetId, true); // Continue recursion for parents
                            }
                        } else if (l.type === 'influence' && !parentsOnly) {
                            // Only highlight direct influences of the hovered node, do NOT recurse
                            if (!highlightedNodeIds.has(targetId)) {
                                highlightedNodeIds.add(targetId);
                                highlightedLinks.add(l);
                            }
                        }
                    }
                });
            };
            findAncestors(hoveredNode.id);
        } else {
            // Neighborhood Mode (Children/Influences)
            link.each(function (l: any) {
                const sourceId = typeof l.source === 'string' ? l.source : l.source.id;
                const targetId = typeof l.target === 'string' ? l.target : l.target.id;
                if (targetId === hoveredNode.id) {
                    highlightedNodeIds.add(sourceId);
                    highlightedLinks.add(l);
                }
            });
        }

        // Apply visual changes to selections
        node
            .attr("fill", (n: any) => n.id === hoveredNode.id ? "#fbbf24" : n.computedColor)
            .attr("r", (n: any) => getRadius(n) + (n.id === hoveredNode.id ? 4 : 0))
            .style("opacity", (n: any) => highlightedNodeIds.has(n.id) ? 1 : 0.15); // slightly higher opacity for non-highlighted

        link
            .style("stroke-opacity", (l: any) => highlightedLinks.has(l) ? 0.8 : (l.type === 'parent' ? 0.05 : 0))
            .style("stroke-width", (l: any) => highlightedLinks.has(l) ? Math.max(2, l.weight * 4) : Math.max(0.5, l.weight * 2));

        label.style("opacity", (n: any) => highlightedNodeIds.has(n.id) ? 1 : 0.1);

    }, [hoveredNode, highlightMode]);

    if (loading) {
        return (
            <div className="w-full h-full flex flex-col items-center justify-center bg-[#0f0f13] text-white">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500 mb-4"></div>
                <p className="text-gray-400 font-medium tracking-widest text-sm uppercase">Mapping the Sonic Universe...</p>
            </div>
        );
    }

    return (
        <div className="relative w-full h-full overflow-hidden">
            <div ref={containerRef} className="w-full h-full" />

            {/* Search Bar Overlay - Moved to Left */}
            <div ref={searchRef} className="absolute top-24 left-8 z-20 w-80">
                <div className="relative group">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <svg className="h-4 w-4 text-gray-400 group-focus-within:text-purple-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                    </div>
                    <input
                        type="text"
                        placeholder="Search for a genre..."
                        className="block w-full pl-10 pr-10 py-2.5 bg-[#1a1a24]/80 backdrop-blur-xl border border-white/10 rounded-xl text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 transition-all shadow-2xl"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        onFocus={() => setIsSearchFocused(true)}
                    />
                    {searchQuery && (
                        <button
                            onClick={() => {
                                setSearchQuery('');
                                setSearchResults([]);
                            }}
                            className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-500 hover:text-white transition-colors"
                        >
                            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    )}
                </div>

                {/* Search Results Dropdown */}
                {isSearchFocused && searchResults.length > 0 && (
                    <div className="absolute mt-2 w-full bg-[#1a1a24]/95 backdrop-blur-2xl border border-white/10 rounded-xl shadow-2xl overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
                        {searchResults.map((result) => (
                            <button
                                key={result.id}
                                className="w-full text-left px-4 py-3 hover:bg-purple-500/10 flex items-center gap-3 transition-colors border-b border-white/5 last:border-0"
                                onClick={() => zoomToNode(result.id)}
                            >
                                <div
                                    className="w-2 h-2 rounded-full shrink-0 shadow-[0_0_8px_rgba(168,85,247,0.5)]"
                                    style={{ backgroundColor: (result as any).computedColor || '#6366f1' }}
                                />
                                <div className="flex flex-col">
                                    <span className="text-sm font-medium text-gray-200">{result.name}</span>
                                    {result.slug && (
                                        <span className="text-[10px] text-gray-500 uppercase tracking-wider">{result.slug}</span>
                                    )}
                                </div>
                            </button>
                        ))}
                    </div>
                )}
            </div>

            {/* Unified Legend Overlay - Combined in Bottom Right */}
            <div className="absolute bottom-6 right-6 z-10 pointer-events-none bg-[#0f0f13]/80 backdrop-blur-md p-5 rounded-2xl border border-white/10 shadow-2xl min-w-[200px]">
                <div className="space-y-6">
                    {/* Interaction Mode Section */}
                    <div>
                        <h3 className="text-[10px] font-bold text-white/40 uppercase tracking-[0.2em] mb-3">Interaction Mode</h3>
                        <div className="flex flex-col gap-2">
                            <div className={`flex items-center gap-3 transition-all duration-300 ${highlightMode === 'ancestry' ? 'text-purple-400 scale-105 origin-left' : 'opacity-30'}`}>
                                <div className="w-2 h-2 rounded-full bg-purple-500 shadow-[0_0_8px_rgba(168,85,247,0.8)]" />
                                <span className="text-[11px] font-semibold tracking-wide">LINEAGE (Ancestors)</span>
                            </div>
                            <div className={`flex items-center gap-3 transition-all duration-300 ${highlightMode === 'neighborhood' ? 'text-emerald-400 scale-105 origin-left' : 'opacity-30'}`}>
                                <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]" />
                                <span className="text-[11px] font-semibold tracking-wide">NEIGHBORHOOD (Influence)</span>
                            </div>
                        </div>
                        <p className="mt-2 text-[10px] text-gray-500 italic font-light italic">Click any node to toggle mode</p>
                    </div>

                    <div className="h-px bg-white/5 w-full" />

                    {/* Edge Logic Section */}
                    <div>
                        <h3 className="text-[10px] font-bold text-white/40 uppercase tracking-[0.2em] mb-3">Relationship Types</h3>
                        <div className="space-y-3">
                            <div className="flex items-center gap-3">
                                <div className="w-8 h-[2px] bg-indigo-500 shadow-[0_0_8px_rgba(99,102,241,0.6)] rounded-full" />
                                <span className="text-[11px] text-gray-300 font-medium tracking-wide">Direct Parent</span>
                            </div>
                            <div className="flex items-center gap-3">
                                <div className="w-8 h-[2px] bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.6)] rounded-full" />
                                <span className="text-[11px] text-gray-300 font-medium tracking-wide">Influence</span>
                            </div>
                        </div>
                    </div>

                    <div className="h-px bg-white/5 w-full" />

                    {/* Nodes Section */}
                    <div>
                        <h3 className="text-[10px] font-bold text-white/40 uppercase tracking-[0.2em] mb-3">Nodes</h3>
                        <div className="flex items-center gap-3">
                            <div className="w-3 h-3 bg-purple-600 rounded-full shadow-[0_0_10px_rgba(168,85,247,0.4)]" />
                            <span className="text-[11px] text-gray-300 font-medium tracking-wide">Genre Node</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Translucent Info Card */}
            {hoveredNode && (
                <div
                    className="absolute top-6 right-6 w-80 max-h-[80%] overflow-y-auto animate-in fade-in slide-in-from-right-4 duration-300 pointer-events-none"
                >
                    <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-6 shadow-2xl text-white">
                        <div className="mb-4">
                            <h2 className="text-2xl font-bold text-purple-400 tracking-tight">{hoveredNode.name}</h2>
                        </div>

                        {hoveredNode.childCount !== undefined && (
                            <div className="mb-4 inline-block px-3 py-1 bg-purple-500/20 border border-purple-500/30 rounded-full">
                                <span className="text-xs font-semibold text-purple-300 uppercase tracking-wider">
                                    {hoveredNode.childCount} Subgenres
                                </span>
                            </div>
                        )}

                        <div className="space-y-4">
                            <div>
                                <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Description</h3>
                                <p className="text-sm text-gray-200 leading-relaxed font-light">
                                    {hoveredNode.description || "No description available for this genre."}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
