"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface TopSubgenresChartProps {
    subgenres: Record<string, number> | null;
}

export const TopSubgenresChart: React.FC<TopSubgenresChartProps> = ({ subgenres }) => {
    const [hoveredGenre, setHoveredGenre] = useState<string | null>(null);

    if (!subgenres) {
        return (
            <div className="h-64 flex items-center justify-center text-zinc-500 text-sm italic">
                No subgenre data found.
            </div>
        );
    }

    const entries = Object.entries(subgenres)
        .filter(([genre]) => genre !== "electronic" && genre !== "rave")
        .sort((a, b) => b[1] - a[1])
        .slice(0, 25);

    if (entries.length === 0) {
        return (
            <div className="h-64 flex items-center justify-center text-zinc-500 text-sm italic">
                No genres found in profile.
            </div>
        );
    }

    const globalTotal = entries.reduce((acc, current) => acc + current[1], 0);

    const getCoordinatesForPercent = (percent: number, radius: number = 1) => {
        const x = radius * Math.cos(2 * Math.PI * percent);
        const y = radius * Math.sin(2 * Math.PI * percent);
        return [x, y];
    };

    const colors = [
        "#8b5cf6", "#ec4899", "#3b82f6", "#10b981", "#f59e0b", 
        "#ef4444", "#6366f1", "#a855f7", "#ec4899", "#d946ef",
        "#0ea5e9", "#14b8a6", "#84cc16", "#eab308", "#f97316",
        "#a8a29e", "#fb7185", "#c084fc", "#818cf8", "#2dd4bf",
        "#f472b6", "#a78bfa", "#60a5fa", "#34d399", "#fbbf24"
    ];

    // Split into 3 rings (Top 5, Next 8, Remaining up to 12)
    const ring1Entries = entries.slice(0, 5);
    const ring2Entries = entries.slice(5, 13);
    const ring3Entries = entries.slice(13, 25);

    const createRingSectors = (ringEntries: [string, number][], innerRadBase: number, outerRadBase: number, startIndexOffset: number) => {
        if (ringEntries.length === 0) return [];
        const ringTotal = ringEntries.reduce((acc, current) => acc + current[1], 0);
        
        const { sectors } = ringEntries.reduce<{ cumulative: number; sectors: any[] }>(
            (acc, [genre, value], i) => {
                const start = acc.cumulative;
                // Local percentage for physical drawing slice size
                const localPercentage = ringTotal > 0 ? value / ringTotal : 0; 
                const end = start + localPercentage;
                // Global percentage for text display
                const globalPercentage = globalTotal > 0 ? value / globalTotal : 0;
                
                return {
                    cumulative: end,
                    sectors: [...acc.sectors, { 
                        genre, 
                        value, 
                        start, 
                        end, 
                        localPercentage,
                        globalPercentage,
                        colorIndex: startIndexOffset + i,
                        innerRadBase,
                        outerRadBase
                    }]
                };
            },
            { cumulative: 0, sectors: [] }
        );
        return sectors;
    };

    const allSectors = [
        ...createRingSectors(ring1Entries, 0.45, 0.60, 0),
        ...createRingSectors(ring2Entries, 0.65, 0.80, ring1Entries.length),
        ...createRingSectors(ring3Entries, 0.85, 1.00, ring1Entries.length + ring2Entries.length)
    ];

    const activeSector = hoveredGenre 
        ? allSectors.find(s => s.genre === hoveredGenre) 
        : allSectors[0];

    return (
        <div className="flex flex-col items-center justify-center py-6 w-full">
            <div className="relative w-72 h-72 md:w-96 md:h-96 group mb-8">
                <div className="absolute inset-0 rounded-full bg-brand-purple/20 blur-3xl opacity-0 group-hover:opacity-60 transition-opacity duration-700" />
                
                <div className="absolute inset-0 flex flex-col items-center justify-center z-20 pointer-events-none">
                    <AnimatePresence mode="wait">
                        {activeSector && (
                            <motion.div 
                                key={activeSector.genre}
                                initial={{ opacity: 0, scale: 0.9, y: 5 }}
                                animate={{ opacity: 1, scale: 1, y: 0 }}
                                exit={{ opacity: 0, scale: 0.9, y: -5 }}
                                transition={{ duration: 0.2 }}
                                className="flex flex-col items-center justify-center p-4 text-center max-w-[60%]"
                            >
                                <span className="text-[10px] sm:text-xs font-black uppercase tracking-[0.2em] mb-2 truncate w-full shadow-black drop-shadow-md" style={{ color: colors[activeSector.colorIndex % colors.length] }}>
                                    {activeSector.genre}
                                </span>
                                <span className="text-3xl sm:text-5xl font-black text-white drop-shadow-[0_0_15px_rgba(255,255,255,0.3)]">
                                    {(activeSector.globalPercentage * 100).toFixed(1)}%
                                </span>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>

                <svg viewBox="-1.1 -1.1 2.2 2.2" className="transform -rotate-90 w-full h-full relative z-10 filter drop-shadow-[0_0_20px_rgba(0,0,0,0.5)]">
                    {allSectors.map((sector) => {
                        const isHovered = hoveredGenre === sector.genre;
                        const opacity = hoveredGenre ? (isHovered ? 1 : 0.25) : 0.9;
                        
                        const innerRadius = isHovered ? sector.innerRadBase - 0.02 : sector.innerRadBase;
                        const outerRadius = isHovered ? sector.outerRadBase + 0.02 : sector.outerRadBase;

                        const [startX, startY] = getCoordinatesForPercent(sector.start, outerRadius);
                        const [endX, endY] = getCoordinatesForPercent(sector.end, outerRadius);
                        const [innerStartX, innerStartY] = getCoordinatesForPercent(sector.start, innerRadius);
                        const [innerEndX, innerEndY] = getCoordinatesForPercent(sector.end, innerRadius);
                        
                        const isFullCircle = sector.localPercentage >= 0.9999;
                        let pathData = "";

                        if (isFullCircle) {
                            pathData = `
                                M 0 -${outerRadius}
                                A ${outerRadius} ${outerRadius} 0 1 1 0 ${outerRadius}
                                A ${outerRadius} ${outerRadius} 0 1 1 0 -${outerRadius}
                                Z
                                M 0 -${innerRadius}
                                A ${innerRadius} ${innerRadius} 0 1 0 0 ${innerRadius}
                                A ${innerRadius} ${innerRadius} 0 1 0 0 -${innerRadius}
                                Z
                            `;
                        } else {
                            const largeArcFlag = sector.localPercentage > 0.5 ? 1 : 0;
                            pathData = [
                                `M ${startX} ${startY}`,
                                `A ${outerRadius} ${outerRadius} 0 ${largeArcFlag} 1 ${endX} ${endY}`,
                                `L ${innerEndX} ${innerEndY}`,
                                `A ${innerRadius} ${innerRadius} 0 ${largeArcFlag} 0 ${innerStartX} ${innerStartY}`,
                                "Z"
                            ].join(" ");
                        }
                        
                        return (
                            <motion.path 
                                key={sector.genre} 
                                d={pathData} 
                                fill={colors[sector.colorIndex % colors.length]} 
                                stroke="#09090b" 
                                strokeWidth="0.012"
                                initial={{ opacity: 0, scale: 0.8 }}
                                animate={{ opacity, scale: 1 }}
                                transition={{ delay: sector.colorIndex * 0.015, duration: 0.4 }}
                                onMouseEnter={() => setHoveredGenre(sector.genre)}
                                onMouseLeave={() => setHoveredGenre(null)}
                                className="cursor-pointer transition-all duration-300 pointer-events-auto"
                            />
                        );
                    })}
                </svg>
            </div>
        </div>
    );
};

