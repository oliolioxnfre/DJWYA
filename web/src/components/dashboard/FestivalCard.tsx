"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronLeft, ChevronRight, X, MapPin, Music, Star, Navigation } from "lucide-react";

export interface FestivalData {
    festival: string;
    total_match: number;
    artist_score: number;
    artist_perc: number;
    synergy_match: number;
    matched_count: number;
    total_artists: number;
    shared_artists: string[];
    lat: number | null;
    lng: number | null;
    location?: string;
    date?: string;
    size?: number | string;
    type?: string;
    fest_subgenres?: Record<string, number>;
}

interface FestivalCardProps {
    festival: FestivalData;
    onNext: () => void;
    onPrev: () => void;
    onClose: () => void;
    onExpandChange?: (isExpanded: boolean) => void;
    hasNext: boolean;
    hasPrev: boolean;
    isOpen: boolean;
}

const SubgenrePieChart = ({ subgenres }: { subgenres?: Record<string, number> }) => {
    if (!subgenres) return null;

    const entries = Object.entries(subgenres)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 8); // Top 8 for clarity

    const total = entries.reduce((acc, current) => acc + current[1], 0);

    const getCoordinatesForPercent = (percent: number) => {
        const x = Math.cos(2 * Math.PI * percent);
        const y = Math.sin(2 * Math.PI * percent);
        return [x, y];
    };

    const colors = ["#8b5cf6", "#ec4899", "#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#6366f1", "#a855f7"];

    // Functional calculation of sectors to avoid reassignment in render
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
        <div className="flex items-center space-x-6">
            <div className="relative w-32 h-32">
                <svg viewBox="-1 -1 2 2" className="transform -rotate-90 w-full h-full">
                    {sectors.map((sector, index) => {
                        const [startX, startY] = getCoordinatesForPercent(sector.start);
                        const [endX, endY] = getCoordinatesForPercent(sector.end);
                        const largeArcFlag = sector.value / total > 0.5 ? 1 : 0;
                        const pathData = [
                            `M ${startX} ${startY}`,
                            `A 1 1 0 ${largeArcFlag} 1 ${endX} ${endY}`,
                            "L 0 0",
                        ].join(" ");
                        return <path key={sector.genre} d={pathData} fill={colors[index % colors.length]} stroke="rgba(0,0,0,0.2)" strokeWidth="0.01" />;
                    })}
                </svg>
            </div>
            <div className="flex-1 grid grid-cols-2 gap-x-4 gap-y-1">
                {entries.map(([genre, value], index) => (
                    <div key={genre} className="flex items-center space-x-2">
                        <div className="w-2 h-2 rounded-full" style={{ backgroundColor: colors[index % colors.length] }} />
                        <span className="text-[10px] text-gray-400 capitalize truncate">{genre}</span>
                        <span className="text-[10px] text-gray-500">{((value / total) * 100).toFixed(0)}%</span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default function FestivalCard({
    festival,
    onNext,
    onPrev,
    onClose,
    onExpandChange,
    hasNext,
    hasPrev,
    isOpen,
}: FestivalCardProps) {
    const [isExpanded, setIsExpanded] = useState(false);

    useEffect(() => {
        onExpandChange?.(isExpanded);
    }, [isExpanded, onExpandChange]);

    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    initial={{ opacity: 0, y: 20, scale: 0.95 }}
                    animate={{
                        opacity: 1,
                        y: isExpanded ? "-50%" : "0%",
                        scale: 1,
                        top: isExpanded ? "50%" : "auto",
                        bottom: isExpanded ? "auto" : "2rem",
                        left: "50%",
                        x: "-50%",
                        width: isExpanded ? "90%" : "100%",
                        maxWidth: isExpanded ? "36rem" : "28rem",
                    }}
                    exit={{ opacity: 0, y: 20, scale: 0.95 }}
                    transition={{ duration: 0.4, type: "spring", damping: 25, stiffness: 200 }}
                    className="fixed z-[1000] px-4 sm:px-0"
                >
                    {/* Glassmorphic Container */}
                    <div className={`relative overflow-hidden rounded-[2.5rem] bg-black/60 backdrop-blur-2xl border border-white/10 shadow-2xl text-white transition-all duration-500 flex flex-col ${isExpanded ? 'h-[85vh]' : 'max-h-none'}`}>

                        {/* Top Bar (Stationary) */}
                        <div className="p-8 pb-4 shrink-0 border-b border-white/5 bg-black/20">
                            <div className="flex justify-between items-start">
                                <div className="flex-1">
                                    <h2 className={`font-bold tracking-tight bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent transition-all duration-300 ${isExpanded ? 'text-4xl' : 'text-2xl'}`}>
                                        {festival.festival}
                                    </h2>
                                    <div className="flex justify-between items-center text-gray-400 text-sm mt-2 font-medium bg-white/5 py-1 px-3 rounded-lg border border-white/5">
                                        <div className="flex items-center">
                                            <MapPin className="w-3.5 h-3.5 mr-1.5 text-purple-400" />
                                            {festival.location || "Location Unknown"}
                                        </div>
                                        {festival.date && (
                                            <div className="flex items-center text-pink-400">
                                                <span className="text-gray-500 mr-2 opacity-50">|</span>
                                                {festival.date}
                                            </div>
                                        )}
                                    </div>
                                </div>
                                <button
                                    onClick={onClose}
                                    className="ml-6 p-2 rounded-full bg-white/5 hover:bg-white/10 transition-colors shrink-0"
                                >
                                    <X className="w-5 h-5 text-gray-300" />
                                </button>
                            </div>
                        </div>

                        {/* Content Switcher (Scrollable) */}
                        <div className={`flex-1 p-8 space-y-6 ${isExpanded ? 'overflow-y-auto custom-scrollbar' : ''}`}>
                            {/* Match Stats */}
                            <div className="grid grid-cols-2 gap-4">
                                <div className="bg-gradient-to-br from-white/10 to-transparent rounded-3xl p-5 border border-white/10 group hover:border-purple-500/30 transition-colors">
                                    <div className="flex items-center space-x-2 mb-2">
                                        <Star className="w-4 h-4 text-purple-400" />
                                        <span className="text-[10px] text-gray-400 uppercase tracking-[0.2em] font-bold">Synergy</span>
                                    </div>
                                    <div className="text-4xl font-black text-white">
                                        {festival.synergy_match.toFixed(1)}<span className="text-xl text-gray-500 font-normal ml-0.5">%</span>
                                    </div>
                                </div>
                                <div className="bg-gradient-to-br from-white/10 to-transparent rounded-3xl p-5 border border-white/10 group hover:border-pink-500/30 transition-colors">
                                    <div className="flex items-center space-x-2 mb-2">
                                        <Music className="w-4 h-4 text-pink-400" />
                                        <span className="text-[10px] text-gray-400 uppercase tracking-[0.2em] font-bold">Lineup Fit</span>
                                    </div>
                                    <div className="text-4xl font-black text-white">
                                        {festival.artist_perc.toFixed(1)}<span className="text-xl text-gray-500 font-normal ml-0.5">%</span>
                                    </div>
                                </div>
                            </div>

                            {/* Expansion Details */}
                            <AnimatePresence>
                                {isExpanded && (
                                    <motion.div
                                        initial={{ opacity: 0, height: 0 }}
                                        animate={{ opacity: 1, height: "auto" }}
                                        exit={{ opacity: 0, height: 0 }}
                                        className="space-y-8 pt-4 border-t border-white/5"
                                    >
                                        {/* Size and Type Info */}
                                        <div className="flex gap-4">
                                            {(festival.size || festival.type) && (
                                                <>
                                                    {festival.size && (
                                                        <div className="flex-1 bg-white/5 rounded-2xl p-4 border border-white/5 flex items-center space-x-3">
                                                            <div className="p-2 bg-blue-500/20 rounded-xl">
                                                                <Navigation className="w-4 h-4 text-blue-400 rotate-45" />
                                                            </div>
                                                            <div>
                                                                <div className="text-[10px] text-gray-500 uppercase font-bold tracking-wider">Crowd Size</div>
                                                                <div className="text-sm font-semibold">{typeof festival.size === 'number' ? festival.size.toLocaleString() : festival.size}</div>
                                                            </div>
                                                        </div>
                                                    )}
                                                    {festival.type && (
                                                        <div className="flex-1 bg-white/5 rounded-2xl p-4 border border-white/5 flex items-center space-x-3">
                                                            <div className="p-2 bg-emerald-500/20 rounded-xl">
                                                                <Navigation className="w-4 h-4 text-emerald-400 rotate-45" />
                                                            </div>
                                                            <div>
                                                                <div className="text-[10px] text-gray-500 uppercase font-bold tracking-wider">Festival Type</div>
                                                                <div className="text-sm font-semibold capitalize">{festival.type}</div>
                                                            </div>
                                                        </div>
                                                    )}
                                                </>
                                            )}
                                        </div>

                                        {/* Subgenre Pie Chart */}
                                        <div className="space-y-4">
                                            <h3 className="text-xs font-bold text-gray-500 uppercase tracking-[0.2em] pl-1">Genre DNA</h3>
                                            <div className="bg-white/5 rounded-3xl p-6 border border-white/5">
                                                <SubgenrePieChart subgenres={festival.fest_subgenres} />
                                            </div>
                                        </div>

                                        {/* All Shared Artists */}
                                        <div className="space-y-4">
                                            <h3 className="text-xs font-bold text-gray-500 uppercase tracking-[0.2em] pl-1">
                                                Matching Lineup ({festival.matched_count}/{festival.total_artists})
                                            </h3>
                                            <div className="flex flex-wrap gap-2">
                                                {festival.shared_artists.map((artist, idx) => (
                                                    <motion.span
                                                        key={idx}
                                                        initial={{ scale: 0.8, opacity: 0 }}
                                                        animate={{ scale: 1, opacity: 1 }}
                                                        transition={{ delay: idx * 0.02 }}
                                                        className="px-4 py-1.5 rounded-xl bg-purple-500/10 text-xs font-semibold text-purple-300 border border-purple-500/20"
                                                    >
                                                        {artist}
                                                    </motion.span>
                                                ))}
                                            </div>
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>

                            {/* Shared Artists Preview (only when not expanded) */}
                            {!isExpanded && (
                                <div className="space-y-3">
                                    <h3 className="text-[10px] font-bold text-gray-500 uppercase tracking-[0.2em] pl-1">
                                        Top Matches
                                    </h3>
                                    <div className="flex flex-wrap gap-2">
                                        {festival.shared_artists.slice(0, 3).map((artist, idx) => (
                                            <span key={idx} className="px-3 py-1 rounded-lg bg-white/5 text-[11px] font-medium border border-white/5">
                                                {artist}
                                            </span>
                                        ))}
                                        {festival.shared_artists.length > 3 && (
                                            <span className="px-3 py-1 rounded-lg bg-white/5 text-[11px] font-medium text-gray-500">
                                                +{festival.shared_artists.length - 3}
                                            </span>
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Footer Navigation (Stationary) */}
                        <div className={`shrink-0 flex items-center justify-between p-8 pt-4 border-t border-white/5 transition-all duration-300 ${isExpanded ? 'bg-black/40 py-6' : 'bg-transparent'}`}>
                            <button
                                onClick={(e) => { e.stopPropagation(); onPrev(); }}
                                disabled={!hasPrev}
                                className="p-3 rounded-2xl bg-white/5 hover:bg-white/10 disabled:opacity-20 transition-all active:scale-95"
                            >
                                <ChevronLeft className="w-5 h-5" />
                            </button>

                            <button
                                onClick={() => setIsExpanded(!isExpanded)}
                                className="flex items-center space-x-3 px-8 py-3.5 rounded-full bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold hover:scale-105 active:scale-95 transition-all shadow-[0_0_30px_rgba(168,85,247,0.4)]"
                            >
                                {isExpanded ? <ChevronLeft className="w-4 h-4 rotate-90" /> : <Star className="w-4 h-4" />}
                                <span className="text-sm tracking-wide">{isExpanded ? "Collapse View" : "More Details"}</span>
                            </button>

                            <button
                                onClick={(e) => { e.stopPropagation(); onNext(); }}
                                disabled={!hasNext}
                                className="p-3 rounded-2xl bg-white/5 hover:bg-white/10 disabled:opacity-20 transition-all active:scale-95"
                            >
                                <ChevronRight className="w-5 h-5" />
                            </button>
                        </div>
                    </div>

                    <style jsx global>{`
            .custom-scrollbar::-webkit-scrollbar {
              width: 4px;
            }
            .custom-scrollbar::-webkit-scrollbar-track {
              background: transparent;
            }
            .custom-scrollbar::-webkit-scrollbar-thumb {
              background: rgba(255, 255, 255, 0.1);
              border-radius: 10px;
            }
          `}</style>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
