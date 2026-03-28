"use client";

import React from "react";
import { motion } from "framer-motion";

interface Artist {
    name: string;
    count: number;
}

interface TopArtistsBarChartProps {
    artists: Artist[];
}

export const TopArtistsBarChart: React.FC<TopArtistsBarChartProps> = ({ artists }) => {
    // Determine max count for percentage calculation
    const maxCount = Math.max(...artists.map(a => a.count), 1);

    return (
        <div className="w-full h-full overflow-y-auto overflow-x-hidden custom-scrollbar pr-2">
            <div className="w-full pl-1 space-y-6">
                {artists.map((artist, i) => {
                    const percentage = (artist.count / maxCount) * 100;
                    
                    return (
                        <motion.div 
                            key={`${artist.name}-${i}`} 
                            className="relative group w-full hover:z-50 transition-all duration-300"
                            initial="initial"
                            whileHover="hover"
                        >
                            <div className="flex justify-between items-center mb-1">
                                <span className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-500 group-hover:text-brand-purple transition-colors truncate pr-2">
                                    {artist.name}
                                </span>
                            </div>
                            
                            <div className="relative h-1.5 w-full bg-white/5 rounded-full border border-white/5">
                                {/* The Bar */}
                                <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${percentage}%` }}
                                    transition={{ delay: i * 0.05, duration: 0.8, ease: "easeOut" }}
                                    className="absolute top-0 left-0 h-full bg-gradient-to-r from-brand-purple to-pink-500 rounded-full shadow-[0_0_15px_rgba(139,92,246,0.3)]"
                                />

                                {/* Tooltip-like value bubble - HOVER ONLY */}
                                <motion.div
                                    variants={{
                                        initial: { opacity: 0, scale: 0.8, y: 0 },
                                        hover: { opacity: 1, scale: 1, y: -25 }
                                    }}
                                    transition={{ type: "spring", damping: 15, stiffness: 300 }}
                                    style={{ left: `${percentage}%` }}
                                    className="absolute -top-4 -translate-x-1/2 px-2 py-1 bg-zinc-900 border border-brand-purple/30 rounded-lg text-[9px] font-black text-white whitespace-nowrap shadow-2xl z-[100] pointer-events-none"
                                >
                                    {artist.count} Plays
                                    <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-1.5 h-1.5 bg-zinc-900 border-r border-b border-brand-purple/30 rotate-45" />
                                </motion.div>
                            </div>
                        </motion.div>
                    );
                })}
                
                {artists.length === 0 && (
                    <div className="h-48 flex items-center justify-center text-zinc-500 text-sm italic">
                        No library data found.
                    </div>
                )}
            </div>
        </div>
    );
};
