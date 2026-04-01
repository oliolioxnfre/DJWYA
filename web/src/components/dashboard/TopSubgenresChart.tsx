"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { supabase } from "@/lib/supabaseClient";

interface TopSubgenresChartProps {
    subgenres: Record<string, number> | null;
}

export const TopSubgenresChart: React.FC<TopSubgenresChartProps> = ({ subgenres }) => {
    const [hoveredGenre, setHoveredGenre] = useState<string | null>(null);
    const [selectedGenre, setSelectedGenre] = useState<string | null>(null);
    const [genreDetails, setGenreDetails] = useState<Record<string, { name: string; description: string }>>({});

    const entries = Object.entries(subgenres || {})
        .filter(([genre]) => genre !== "electronic" && genre !== "rave")
        .sort((a, b) => b[1] - a[1])
        .slice(0, 25);

    useEffect(() => {
        if (entries.length === 0) return;

        const fetchDescriptions = async () => {
            const slugs = entries.map(([slug]) => slug);
            const { data, error } = await supabase
                .from("genres")
                .select("slug, name, description")
                .in("slug", slugs);

            if (data && !error) {
                const mapping = data.reduce((acc, curr) => ({
                    ...acc,
                    [curr.slug]: { name: curr.name, description: curr.description }
                }), {});
                setGenreDetails(mapping);
            }
        };

        fetchDescriptions();
    }, [subgenres]);

    if (!subgenres) {
        return (
            <div className="h-64 flex items-center justify-center text-zinc-500 text-sm italic">
                No subgenre data found.
            </div>
        );
    }

    // Entries already calculated above for the useEffect

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

    const effectiveGenre = hoveredGenre || selectedGenre;
    const activeSector = effectiveGenre 
        ? allSectors.find(s => s.genre === effectiveGenre) 
        : allSectors[0];

    return (
        <div className="flex flex-col md:flex-row items-center md:items-start justify-center py-6 w-full gap-8 md:gap-16">
            {/* Chart Column */}
            <div className="relative w-72 h-72 md:w-[450px] md:h-[450px] group flex-shrink-0">
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

                <svg 
                    viewBox="-1.1 -1.1 2.2 2.2" 
                    className="transform -rotate-90 w-full h-full relative z-10 filter drop-shadow-[0_0_20px_rgba(0,0,0,0.5)] cursor-default"
                    onClick={() => setSelectedGenre(null)}
                >
                    {allSectors.map((sector) => {
                        const isHovered = hoveredGenre === sector.genre;
                        const isSelected = selectedGenre === sector.genre;
                        const isActive = isHovered || isSelected;
                        
                        const anyActive = hoveredGenre || selectedGenre;
                        const opacity = anyActive ? (isActive ? 1 : 0.25) : 0.9;
                        
                        const innerRadius = isActive ? sector.innerRadBase - 0.02 : sector.innerRadBase;
                        const outerRadius = isActive ? sector.outerRadBase + 0.02 : sector.outerRadBase;

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
                                onClick={(e) => {
                                    e.stopPropagation();
                                    setSelectedGenre(selectedGenre === sector.genre ? null : sector.genre);
                                }}
                                className="cursor-pointer transition-all duration-300 pointer-events-auto"
                            />
                        );
                    })}
                </svg>
            </div>

            {/* Description Panel */}
            <div className="flex-1 flex flex-col justify-center min-h-[300px] md:pt-12">
                <AnimatePresence mode="wait">
                    {effectiveGenre ? (
                        <motion.div
                            key={effectiveGenre}
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            transition={{ duration: 0.3 }}
                            className="space-y-6"
                        >
                            <div className="space-y-1">
                                <h3 className="text-5xl md:text-7xl font-black italic uppercase tracking-tighter text-white">
                                    {genreDetails[effectiveGenre]?.name || effectiveGenre}
                                </h3>
                                <div className="flex items-center gap-3">
                                    <div className="h-1 w-12 bg-brand-purple rounded-full" />
                                    <span className="text-zinc-500 font-bold uppercase tracking-widest text-xs">
                                        Subgenre Insight
                                    </span>
                                </div>
                            </div>

                            <p className="text-zinc-400 text-lg md:text-xl leading-relaxed max-w-2xl font-medium italic">
                                {genreDetails[effectiveGenre]?.description || 
                                 `Exploring the sonic landscape of ${effectiveGenre}. This profile represents a significant pillar of your musical DNA, characterized by its unique rhythmic patterns and cultural impact within the electronic scene.`}
                            </p>
                            
                            <div className="pt-4 flex gap-8">
                                <div className="flex flex-col">
                                    <span className="text-[10px] font-bold text-zinc-600 uppercase tracking-widest">Weight</span>
                                    <span className="text-2xl font-black text-white">{subgenres[effectiveGenre]}</span>
                                </div>
                                <div className="flex flex-col">
                                    <span className="text-[10px] font-bold text-zinc-600 uppercase tracking-widest">Global Pct</span>
                                    <span className="text-2xl font-black text-white">
                                        {((subgenres[effectiveGenre] / globalTotal) * 100).toFixed(1)}%
                                    </span>
                                </div>
                            </div>
                        </motion.div>
                    ) : (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="flex flex-col space-y-4"
                        >
                            <h3 className="text-4xl md:text-6xl font-black italic uppercase tracking-tighter text-zinc-800">
                                Select a Genre
                            </h3>
                            <p className="text-zinc-600 text-lg italic max-w-md">
                                Hover or click segments of your Sonic Universe to dive deep into the specific subgenres that define your taste.
                            </p>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
};

