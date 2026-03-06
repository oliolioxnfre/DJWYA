"use client";
/* eslint-disable @typescript-eslint/no-explicit-any */

import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';

interface Node extends d3.SimulationNodeDatum {
    id: string;
    name: string;
    sonic_dna?: any;
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

        // Interactivity: Hover to highlight connections
        node.on("mouseover", (event, d) => {
            // Highlight Node
            d3.select(event.currentTarget).attr("fill", "#fbbf24").attr("r", getRadius(d) + 4);

            // Filter linked nodes
            const linkedNodeIds = new Set<string>();
            linkedNodeIds.add(d.id);

            link
                .style("stroke-opacity", l => {
                    if (l.source.id === d.id || l.target.id === d.id) {
                        linkedNodeIds.add(l.source.id);
                        linkedNodeIds.add(l.target.id);
                        return 1;
                    }
                    return (l.type === 'parent' ? 0.1 : 0);
                })
                .style("stroke-width", l => ((l.source.id === d.id || l.target.id === d.id) ? l.weight * 3 : l.weight));

            node.style("opacity", n => linkedNodeIds.has(n.id) ? 1 : 0.2);
            label.style("opacity", n => linkedNodeIds.has(n.id) ? 1 : 0.2);

            // Tooltip
            tooltip
                .style("visibility", "visible")
                .html(`<strong>${d.name}</strong>`);
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
                .attr("y", d => d.y);
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

    return <div ref={containerRef} className="w-full h-full" />;
}
