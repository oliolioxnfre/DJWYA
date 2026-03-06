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
    const [data, setData] = useState<GraphData | null>(null);
    const [loading, setLoading] = useState(true);
    const [selectedNode, setSelectedNode] = useState<Node | null>(null);

    useEffect(() => {
        // Fetch Graph Data
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

    useEffect(() => {
        if (!data || !containerRef.current) return;

        const width = containerRef.current.clientWidth;
        const height = containerRef.current.clientHeight;

        // Clear previous SVG
        d3.select(containerRef.current).selectAll("*").remove();

        const svg = d3.select(containerRef.current)
            .append("svg")
            .attr("width", "100%")
            .attr("height", "100%")
            .attr("viewBox", `0 0 ${width} ${height}`)
            .style("background-color", "#0f0f13") // Dark background matching DJWYA theme
            .call(d3.zoom<SVGSVGElement, unknown>().on("zoom", (e) => {
                g.attr("transform", e.transform);
            }))
            .on("dblclick.zoom", null);

        const g = svg.append("g");

        // Defs for arrowheads
        svg.append("defs").selectAll("marker")
            .data(["parent", "influence"])
            .enter().append("marker")
            .attr("id", String)
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 15) // Adjust based on node radius
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr("fill", d => d === 'parent' ? "#6366f1" : "#10b981") // Indigo for parent, Emerald for influence
            .attr("opacity", 0.6);

        // Deep copy data so simulation doesn't mutate original state
        const nodes = data.nodes.map(d => Object.create(d));
        const links = data.links.map(d => Object.create(d));

        // Calculate children count for each node
        const childCountMap: Record<string, number> = {};
        links.forEach((l: any) => {
            const parentId = typeof l.target === 'string' ? l.target : l.target.id;
            childCountMap[parentId] = (childCountMap[parentId] || 0) + 1;
        });

        // Add childCount to nodes for easier access
        nodes.forEach((n: any) => {
            n.childCount = childCountMap[n.id] || 0;
        });

        // Base Forces
        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id((d: any) => d.id).distance(100)) // Increased from 60
            .force("charge", d3.forceManyBody().strength(-300)) // Increased repulsion from -150
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collide", d3.forceCollide().radius((d: any) => {
                const baseRadius = 8;
                const extraRadius = Math.sqrt(d.childCount || 0) * 4;
                return baseRadius + extraRadius + 10; // Extra padding for separation
            }).iterations(2)); // Prevent overlap

        // Draw Links
        const link = g.append("g")
            .selectAll("line")
            .data(links)
            .join("line")
            .attr("stroke", d => d.type === 'parent' ? "#6366f1" : "#10b981") // Indigo vs Emerald
            .attr("stroke-width", d => Math.max(0.5, d.weight * 2))
            .attr("marker-end", d => `url(#${d.type})`)
            .style("stroke-opacity", d => (d.type === 'parent' ? 0.6 : 0)); // Hide influences by default

        // Helper to calculate radius
        const getRadius = (d: any) => {
            const baseRadius = 8;
            const extraRadius = Math.sqrt(d.childCount || 0) * 4;
            return baseRadius + extraRadius;
        };

        // Draw Nodes
        const node = g.append("g")
            .attr("stroke", "#fff")
            .attr("stroke-width", 1.5)
            .selectAll("circle")
            .data(nodes)
            .join("circle")
            .attr("r", d => getRadius(d))
            .attr("fill", "#a855f7") // Purple nodes
            .call(drag(simulation) as any);

        // Node Labels
        const label = g.append("g")
            .selectAll("text")
            .data(nodes)
            .join("text")
            .text(d => d.name)
            .attr("font-size", "10px")
            .attr("dx", (d: any) => getRadius(d) + 4)
            .attr("dy", 4)
            .attr("fill", "#e2e8f0") // Slate 200 text
            .attr("pointer-events", "none"); // Don't block hover events on nodes

        // Dynamic Tooltip Setup
        const tooltip = d3.select("body").append("div")
            .attr("class", "graph-tooltip")
            .style("position", "absolute")
            .style("visibility", "hidden")
            .style("background-color", "rgba(15, 15, 19, 0.9)")
            .style("color", "#fff")
            .style("padding", "8px 12px")
            .style("border-radius", "6px")
            .style("border", "1px solid #333")
            .style("font-size", "12px")
            .style("pointer-events", "none")
            .style("z-index", "10");

        // Interactivity: Hover to highlight recursive ancestry path
        node.on("mouseover", (event, d) => {
            // Highlight Node
            d3.select(event.currentTarget).attr("fill", "#fbbf24").attr("r", getRadius(d) + 4);

            const ancestralNodeIds = new Set<string>();
            const ancestralLinks = new Set<any>();

            // Recursive function to find all ancestors
            const findAncestors = (nodeId: string) => {
                ancestralNodeIds.add(nodeId);
                links.forEach((l: any) => {
                    const sourceId = typeof l.source === 'string' ? l.source : l.source.id;
                    const targetId = typeof l.target === 'string' ? l.target : l.target.id;

                    if (sourceId === nodeId && !ancestralNodeIds.has(targetId)) {
                        ancestralLinks.add(l);
                        findAncestors(targetId);
                    }
                });
            };

            findAncestors(d.id);

            link
                .style("stroke-opacity", l => ancestralLinks.has(l) ? 1 : (l.type === 'parent' ? 0.05 : 0))
                .style("stroke-width", l => ancestralLinks.has(l) ? Math.max(2, l.weight * 4) : Math.max(0.5, l.weight * 2));

            node.style("opacity", n => ancestralNodeIds.has(n.id) ? 1 : 0.1);
            label.style("opacity", n => ancestralNodeIds.has(n.id) ? 1 : 0.1);

            // Tooltip
            tooltip
                .style("visibility", "visible")
                .html(`<strong>${d.name}</strong>${d.childCount > 0 ? `<br/><span style="font-size: 10px; color: #a855f7;">${d.childCount} subgenres</span>` : ''}`);
        })
            .on("mousemove", (event) => {
                tooltip
                    .style("top", (event.pageY - 10) + "px")
                    .style("left", (event.pageX + 10) + "px");
            })
            .on("mouseout", (event, d) => {
                // Reset
                d3.select(event.currentTarget).attr("fill", "#a855f7").attr("r", getRadius(d));
                link.style("stroke-opacity", l => (l.type === 'parent' ? 0.6 : 0)).style("stroke-width", l => Math.max(0.5, l.weight * 2));
                node.style("opacity", 1);
                label.style("opacity", 1);
                tooltip.style("visibility", "hidden");
            });


        // Interactivity: Click to show Info Card
        node.on("click", (event, d) => {
            event.stopPropagation();
            setSelectedNode(d);
        });

        // Click on background to deselect
        svg.on("click", () => {
            setSelectedNode(null);
        });


        // Simulation Tick
        simulation.on("tick", () => {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);

            label
                .attr("x", d => d.x)
                .attr("y", n => n.y);
        });

        // Cleanup
        return () => {
            simulation.stop();
            d3.select("body").selectAll(".graph-tooltip").remove();
        };
    }, [data]);

    // Drag function
    const drag = (simulation: any) => {
        function dragstarted(event: any) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }

        function dragged(event: any) {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }

        function dragended(event: any) {
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }

        return d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended);
    }

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

            {/* Translucent Info Card */}
            {selectedNode && (
                <div
                    className="absolute top-6 right-6 w-80 max-h-[80%] overflow-y-auto animate-in fade-in slide-in-from-right-4 duration-300"
                    onClick={(e) => e.stopPropagation()}
                >
                    <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-6 shadow-2xl text-white">
                        <div className="flex justify-between items-start mb-4">
                            <h2 className="text-2xl font-bold text-purple-400 tracking-tight">{selectedNode.name}</h2>
                            <button
                                onClick={() => setSelectedNode(null)}
                                className="text-gray-400 hover:text-white transition-colors"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>

                        {selectedNode.childCount !== undefined && (
                            <div className="mb-4 inline-block px-3 py-1 bg-purple-500/20 border border-purple-500/30 rounded-full">
                                <span className="text-xs font-semibold text-purple-300 uppercase tracking-wider">
                                    {selectedNode.childCount} Subgenres
                                </span>
                            </div>
                        )}

                        <div className="space-y-4">
                            <div>
                                <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Description</h3>
                                <p className="text-sm text-gray-200 leading-relaxed font-light">
                                    {selectedNode.description || "No description available for this genre."}
                                </p>
                            </div>

                            {/* Potential for sonic DNA visual here later */}
                            {selectedNode.sonic_dna && (
                                <div className="pt-2">
                                    <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">Sonic DNA</h3>
                                    <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                                        <div className="h-full bg-gradient-to-right from-purple-500 to-indigo-500 w-full opacity-50" />
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
