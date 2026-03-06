"use client";
/* eslint-disable @typescript-eslint/no-explicit-any */

import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';

interface Node extends d3.SimulationNodeDatum {
    id: string;
    name: string;
    description?: string;
    sonic_dna?: any;
    childCount?: number;
}

interface Link extends d3.SimulationLinkDatum<Node> {
    source: string | Node;
    target: string | Node;
    type: string;
    weight: number;
}

interface GraphData {
    nodes: Node[];
    links: Link[];
}

export default function ForceGraph() {
    const containerRef = useRef<HTMLDivElement>(null);

    // D3 Refs to store selections and simulation for stable updates
    const nodeSelectionRef = useRef<any>(null);
    const linkSelectionRef = useRef<any>(null);
    const labelSelectionRef = useRef<any>(null);
    const simulationRef = useRef<any>(null);

    const [data, setData] = useState<GraphData | null>(null);
    const [loading, setLoading] = useState(true);

    // Interaction States
    const [hoveredNode, setHoveredNode] = useState<Node | null>(null);
    const [highlightMode, setHighlightMode] = useState<'ancestry' | 'neighborhood'>('ancestry');

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

    // SETUP EFFECT: Runs only when data changes
    useEffect(() => {
        if (!data || !containerRef.current) return;

        const width = containerRef.current.clientWidth;
        const height = containerRef.current.clientHeight;

        // Reset Container
        d3.select(containerRef.current).selectAll("*").remove();

        const svg = d3.select(containerRef.current)
            .append("svg")
            .attr("width", "100%")
            .attr("height", "100%")
            .attr("viewBox", `0 0 ${width} ${height}`)
            .style("background-color", "#0f0f13")
            .call(d3.zoom<SVGSVGElement, unknown>().on("zoom", (e) => {
                g.attr("transform", e.transform);
            }))
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

        // Prep Data
        const nodes: Node[] = data.nodes.map(d => Object.create(d));
        const links: Link[] = data.links.map(d => Object.create(d));

        const childCountMap: Record<string, number> = {};
        links.forEach((l: any) => {
            const parentId = typeof l.target === 'string' ? l.target : l.target.id;
            childCountMap[parentId] = (childCountMap[parentId] || 0) + 1;
        });

        nodes.forEach((n: any) => {
            n.childCount = childCountMap[n.id] || 0;
        });

        // Initialize Simulation
        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id((d: any) => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collide", d3.forceCollide().radius((d: any) => getRadius(d) + 10).iterations(2));

        simulationRef.current = simulation;

        // 1. Draw Links
        const link = g.append("g")
            .selectAll("line")
            .data(links)
            .join("line")
            .attr("stroke", d => d.type === 'parent' ? "#6366f1" : "#10b981")
            .attr("stroke-width", d => Math.max(0.5, d.weight * 2))
            .attr("marker-end", d => `url(#${d.type})`)
            .style("stroke-opacity", d => (d.type === 'parent' ? 0.6 : 0));

        linkSelectionRef.current = link;

        // 2. Draw Nodes
        const node = g.append("g")
            .attr("stroke", "#fff")
            .attr("stroke-width", 1.5)
            .selectAll("circle")
            .data(nodes)
            .join("circle")
            .attr("r", d => getRadius(d))
            .attr("fill", "#a855f7")
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
                })
            );

        nodeSelectionRef.current = node;

        // 3. Draw Labels
        const label = g.append("g")
            .selectAll("text")
            .data(nodes)
            .join("text")
            .text(d => d.name)
            .attr("font-size", "10px")
            .attr("dx", d => getRadius(d) + 4)
            .attr("dy", 4)
            .attr("fill", "#e2e8f0")
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
            // Reset to default state
            node.attr("fill", "#a855f7").attr("r", (d: any) => getRadius(d)).style("opacity", 1);
            link.style("stroke-opacity", (l: any) => l.type === 'parent' ? 0.6 : 0).style("stroke-width", (l: any) => Math.max(0.5, l.weight * 2));
            label.style("opacity", 1);
            return;
        }

        // Identify highlighting set
        const highlightedNodeIds = new Set<string>();
        const highlightedLinks = new Set<any>();
        highlightedNodeIds.add(hoveredNode.id);

        if (highlightMode === 'ancestry') {
            const findAncestors = (nodeId: string) => {
                link.each(function (l: any) {
                    const sourceId = typeof l.source === 'string' ? l.source : l.source.id;
                    const targetId = typeof l.target === 'string' ? l.target : l.target.id;
                    if (sourceId === nodeId && !highlightedNodeIds.has(targetId)) {
                        highlightedNodeIds.add(targetId);
                        highlightedLinks.add(l);
                        findAncestors(targetId);
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
            .attr("fill", (n: any) => n.id === hoveredNode.id ? "#fbbf24" : "#a855f7")
            .attr("r", (n: any) => getRadius(n) + (n.id === hoveredNode.id ? 4 : 0))
            .style("opacity", (n: any) => highlightedNodeIds.has(n.id) ? 1 : 0.1);

        link
            .style("stroke-opacity", (l: any) => highlightedLinks.has(l) ? 1 : (l.type === 'parent' ? 0.05 : 0))
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

            {/* Legend / Mode Indicator */}
            <div className="absolute top-6 left-6 pointer-events-none">
                <div className="bg-black/40 backdrop-blur-md border border-white/10 rounded-lg p-3 text-[10px] text-gray-300">
                    <div className="flex items-center gap-2 mb-2">
                        <span className="font-bold uppercase tracking-widest text-white/80">Interaction Mode</span>
                    </div>
                    <div className="flex flex-col gap-1">
                        <div className={`flex items-center gap-2 transition-opacity duration-300 ${highlightMode === 'ancestry' ? 'text-purple-400' : 'opacity-30'}`}>
                            <div className="w-1.5 h-1.5 rounded-sm bg-purple-500" />
                            <span>LINEAGE (Ancestors)</span>
                        </div>
                        <div className={`flex items-center gap-2 transition-opacity duration-300 ${highlightMode === 'neighborhood' ? 'text-emerald-400' : 'opacity-30'}`}>
                            <div className="w-1.5 h-1.5 rounded-sm bg-emerald-500" />
                            <span>NEIGHBORHOOD (Children/Influences)</span>
                        </div>
                    </div>
                    <div className="mt-2 text-gray-500 italic">Click any node to toggle mode</div>
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
