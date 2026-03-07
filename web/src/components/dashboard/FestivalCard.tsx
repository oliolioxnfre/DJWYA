"use client";

import React from "react";
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
}

interface FestivalCardProps {
    festival: FestivalData;
    onNext: () => void;
    onPrev: () => void;
    onClose: () => void;
    hasNext: boolean;
    hasPrev: boolean;
    isOpen: boolean;
}

export default function FestivalCard({
    festival,
    onNext,
    onPrev,
    onClose,
    hasNext,
    hasPrev,
    isOpen,
}: FestivalCardProps) {
    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    initial={{ opacity: 0, y: 20, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 20, scale: 0.95 }}
                    transition={{ duration: 0.3, ease: "easeOut" }}
                    className="absolute bottom-8 left-1/2 -translate-x-1/2 w-full max-w-md z-[1000] px-4 sm:px-0"
                >
                    {/* Glassmorphic Container */}
                    <div className="relative overflow-hidden rounded-3xl bg-black/60 backdrop-blur-xl border border-white/10 shadow-2xl p-6 text-white pb-20">

                        {/* Top Bar */}
                        <div className="flex justify-between items-start mb-4">
                            <div>
                                <h2 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                                    {festival.festival}
                                </h2>
                                <div className="flex items-center text-gray-400 text-sm mt-1">
                                    <MapPin className="w-4 h-4 mr-1" />
                                    {festival.lat && festival.lng
                                        ? `${festival.lat.toFixed(2)}, ${festival.lng.toFixed(2)}`
                                        : "Unknown Location"}
                                </div>
                            </div>
                            <button
                                onClick={onClose}
                                className="p-2 rounded-full bg-white/5 hover:bg-white/10 transition-colors"
                            >
                                <X className="w-5 h-5 text-gray-300" />
                            </button>
                        </div>

                        {/* Match Stats */}
                        <div className="grid grid-cols-2 gap-4 mb-6">
                            <div className="bg-white/5 rounded-2xl p-4 border border-white/5">
                                <div className="flex items-center space-x-2 mb-1">
                                    <Star className="w-4 h-4 text-purple-400" />
                                    <span className="text-xs text-gray-400 uppercase tracking-wider font-semibold">Synergy</span>
                                </div>
                                <div className="text-3xl font-bold text-white">
                                    {festival.synergy_match.toFixed(1)}<span className="text-lg text-gray-500">%</span>
                                </div>
                            </div>
                            <div className="bg-white/5 rounded-2xl p-4 border border-white/5">
                                <div className="flex items-center space-x-2 mb-1">
                                    <Music className="w-4 h-4 text-pink-400" />
                                    <span className="text-xs text-gray-400 uppercase tracking-wider font-semibold">Lineup Fit</span>
                                </div>
                                <div className="text-3xl font-bold text-white">
                                    {festival.artist_perc.toFixed(1)}<span className="text-lg text-gray-500">%</span>
                                </div>
                            </div>
                        </div>

                        {/* Shared Artists */}
                        <div className="space-y-2 mb-8">
                            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
                                Matching Artists ({festival.matched_count}/{festival.total_artists})
                            </h3>
                            <div className="flex flex-wrap gap-2">
                                {festival.shared_artists.slice(0, 5).map((artist, idx) => (
                                    <span key={idx} className="px-3 py-1 rounded-full bg-white/10 text-sm font-medium border border-white/5">
                                        {artist}
                                    </span>
                                ))}
                                {festival.shared_artists.length > 5 && (
                                    <span className="px-3 py-1 rounded-full bg-white/5 text-sm font-medium text-gray-400 border border-white/5">
                                        +{festival.shared_artists.length - 5} more
                                    </span>
                                )}
                            </div>
                        </div>

                        {/* Footer Navigation */}
                        <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent flex justify-between items-center rounded-b-3xl">
                            <button
                                onClick={onPrev}
                                disabled={!hasPrev}
                                className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 disabled:opacity-30 disabled:hover:bg-white/10 transition-colors"
                            >
                                <ChevronLeft className="w-5 h-5" />
                                <span className="text-sm font-medium">Prev</span>
                            </button>

                            <button className="flex items-center space-x-2 px-5 py-2.5 rounded-full bg-white text-black font-semibold hover:scale-105 transition-transform shadow-[0_0_20px_rgba(255,255,255,0.3)]">
                                <Navigation className="w-4 h-4" />
                                <span>Fly To</span>
                            </button>

                            <button
                                onClick={onNext}
                                disabled={!hasNext}
                                className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 disabled:opacity-30 disabled:hover:bg-white/10 transition-colors"
                            >
                                <span className="text-sm font-medium">Next</span>
                                <ChevronRight className="w-5 h-5" />
                            </button>
                        </div>
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
