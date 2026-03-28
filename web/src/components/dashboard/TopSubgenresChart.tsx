"use client";

import React from "react";
import { motion } from "framer-motion";

interface TopSubgenresChartProps {
    subgenres: Record<string, number> | null;
}

export const TopSubgenresChart: React.FC<TopSubgenresChartProps> = ({ subgenres }) => {
    if (!subgenres) {
        return (
            <div className="h-64 flex items-center justify-center text-zinc-500 text-sm italic">
                No subgenre data found.
            </div>
        );
    }

    const entries = Object.entries(subgenres)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10); // Show top 10

    const total = entries.reduce((acc, current) => acc + current[1], 0);

    const getCoordinatesForPercent = (percent: number) => {
        const x = Math.cos(2 * Math.PI * percent);
        const y = Math.sin(2 * Math.PI * percent);
        return [x, y];
    };

    const colors = [
        "#8b5cf6", "#ec4899", "#3b82f6", "#10b981", "#f59e0b", 
        "#ef4444", "#6366f1", "#a855f7", "#ec4899", "#d946ef"
    ];

    const { sectors } = entries.reduce<{ cumulative: number; sectors: Array<{ genre: string; value: number; start: number; end: number }> }>(
        (acc, [genre, value]) => {
            const start = acc.cumulative;
            const end = start + (value / total);
            return {
                cumulative: end,
                sectors: [...acc.sectors, { genre, value, start, end }]
            };
        },
        { cumulative: 0, sectors: [] }
    );

    return (
        <div className="flex flex-col md:flex-row items-center justify-between gap-12 py-6">
            <div className="relative w-64 h-64 md:w-80 md:h-80 group">
                {/* Glow effect */}
                <div className="absolute inset-0 rounded-full bg-brand-purple/20 blur-3xl opacity-0 group-hover:opacity-100 transition-opacity" />
                
                <svg viewBox="-1 -1 2 2" className="transform -rotate-90 w-full h-full relative z-10 filter drop-shadow-[0_0_20px_rgba(0,0,0,0.5)]">
                    {sectors.map((sector, index) => {
                        const [startX, startY] = getCoordinatesForPercent(sector.start);
                        const [endX, endY] = getCoordinatesForPercent(sector.end);
                        const largeArcFlag = sector.value / total > 0.5 ? 1 : 0;
                        const pathData = [
                            `M ${startX} ${startY}`,
                            `A 1 1 0 ${largeArcFlag} 1 ${endX} ${endY}`,
                            "L 0 0",
                        ].join(" ");
                        
                        return (
                            <motion.path 
                                key={sector.genre} 
                                d={pathData} 
                                fill={colors[index % colors.length]} 
                                stroke="rgba(0,0,0,0.3)" 
                                strokeWidth="0.005"
                                initial={{ opacity: 0, scale: 0.8 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ delay: index * 0.05, duration: 0.5 }}
                                whileHover={{ scale: 1.05, strokeWidth: "0.02" }}
                            />
                        );
                    })}
                </svg>
            </div>

            <div className="flex-1 grid grid-cols-2 gap-x-8 gap-y-4 max-w-lg">
                {entries.map(([genre, value], index) => (
                    <motion.div 
                        key={genre} 
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.3 + (index * 0.05) }}
                        className="flex items-center justify-between space-x-4 p-2 rounded-xl hover:bg-white/5 transition-colors border border-transparent hover:border-white/5"
                    >
                        <div className="flex items-center space-x-3">
                            <div className="w-3 h-3 rounded-full shadow-[0_0_10px_rgba(255,255,255,0.2)]" style={{ backgroundColor: colors[index % colors.length] }} />
                            <span className="text-xs font-bold text-zinc-300 uppercase tracking-widest truncate max-w-[120px]">{genre}</span>
                        </div>
                        <span className="text-sm font-black text-white">{((value / total) * 100).toFixed(0)}%</span>
                    </motion.div>
                ))}
            </div>
        </div>
    );
};
