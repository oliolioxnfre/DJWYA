"use client";

import React, { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { Loader2, AlertCircle, Compass } from "lucide-react";
import { supabase } from "@/lib/supabaseClient";
import FestivalCard, { FestivalData } from "@/components/dashboard/FestivalCard";
import type { MapBoxProps } from "@/components/dashboard/MapBox";
import Header from "@/components/dashboard/Header";

// Dynamically import MapBox to prevent SSR issues with Leaflet
const MapBox = dynamic<MapBoxProps>(() => import("@/components/dashboard/MapBox"), {
    ssr: false,
    loading: () => (
        <div className="w-full h-full bg-[#0a0a0a] flex items-center justify-center">
            <div className="flex flex-col items-center text-gray-400">
                <Loader2 className="w-8 h-8 animate-spin mb-4" />
                <p>Loading Map Data...</p>
            </div>
        </div>
    ),
});

export default function FestivalsPage() {
    const [festivals, setFestivals] = useState<FestivalData[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedIndex, setSelectedIndex] = useState<number>(-1);
    const [isCardOpen, setIsCardOpen] = useState(false);
    const [hasStarted, setHasStarted] = useState(false);
    const [isExpanded, setIsExpanded] = useState(false);

    useEffect(() => {
        async function loadFestivals() {
            try {
                const { data: { user } } = await supabase.auth.getUser();
                if (!user) throw new Error("Not authenticated");

                // Fetch user id from our db
                const { data: userData } = await supabase
                    .from("users")
                    .select("id")
                    .eq("auth_id", user.id)
                    .single();

                const p_uid = userData ? userData.id : user.id;

                // Fetch festivals
                const res = await fetch(`http://127.0.0.1:8000/api/festivals?user_id=${p_uid}`);
                if (!res.ok) throw new Error("Failed to fetch festivals");

                const json = await res.json();

                // Filter out festivals without location coordinates for mapping
                const mappedMatches = (json.data || []).map((f: any) => ({
                    ...f,
                    lat: f.lat ? parseFloat(f.lat) : null,
                    lng: f.lng ? parseFloat(f.lng) : null,
                    location: f.location,
                    date: f.date,
                    size: f.size,
                    type: f.type,
                    fest_subgenres: f.fest_subgenres
                })).filter((f: any) => f.lat !== null && f.lng !== null);

                setFestivals(mappedMatches);
            } catch (err: unknown) {
                console.error(err);
                if (err instanceof Error) {
                    setError(err.message || "Failed to load festivals");
                } else {
                    setError("Failed to load festivals");
                }
            } finally {
                setLoading(false);
            }
        }

        loadFestivals();
    }, []);

    const handleStartFinder = () => {
        if (festivals.length > 0) {
            setHasStarted(true);
            setSelectedIndex(0);
            setIsCardOpen(true);
        }
    };

    const handleNext = () => {
        if (selectedIndex < festivals.length - 1) {
            setSelectedIndex(s => s + 1);
        }
    };

    const handlePrev = () => {
        if (selectedIndex > 0) {
            setSelectedIndex(s => s - 1);
        }
    };

    const handleCloseCard = () => {
        setIsCardOpen(false);
        setIsExpanded(false);
    };

    const handleSelectFestival = (idx: number) => {
        setHasStarted(true);
        setSelectedIndex(idx);
        setIsCardOpen(true);
    };

    if (loading) {
        return (
            <div className="flex h-screen items-center justify-center bg-[#0a0a0a]">
                <Loader2 className="w-10 h-10 animate-spin text-purple-500" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex h-screen items-center justify-center bg-[#0a0a0a]">
                <div className="bg-red-500/10 border border-red-500/20 p-6 rounded-2xl flex items-start space-x-4 max-w-lg">
                    <AlertCircle className="w-6 h-6 text-red-400 shrink-0 mt-0.5" />
                    <div>
                        <h3 className="text-red-400 font-semibold mb-1">Error Loading Map</h3>
                        <p className="text-red-300 text-sm">{error}</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="h-screen w-full bg-[#0a0a0a] overflow-hidden relative">
            <Header />
            
            <div className={`absolute inset-0 transition-all duration-700 ease-in-out ${isExpanded ? 'blur-xl scale-105 opacity-40' : 'blur-0 scale-100 opacity-100'}`}>
                    <MapBox
                        festivals={festivals}
                        selectedIndex={isCardOpen ? selectedIndex : -1}
                        onSelectFestival={handleSelectFestival}
                    />
                </div>

                {/* Intro Overlay */}
                {!hasStarted && festivals.length > 0 && (
                    <div className="absolute inset-x-8 top-10 mx-auto max-w-lg z-[1000] pointer-events-none">
                        <div className="bg-black/60 backdrop-blur-xl border border-white/10 rounded-3xl p-8 text-center shadow-2xl pointer-events-auto">
                            <Compass className="w-12 h-12 text-purple-400 mx-auto mb-4" />
                            <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent mb-4">
                                Festival Finder
                            </h1>
                            <p className="text-gray-400 text-sm mb-8 leading-relaxed">
                                We&apos;ve scanned the globe to find festivals matching your Sonic DNA.
                                Ready to see where your artists are playing?
                            </p>
                            <button
                                onClick={handleStartFinder}
                                className="px-8 py-4 bg-white text-black font-semibold rounded-full w-full hover:scale-[1.02] transition-transform flex items-center justify-center space-x-2 shadow-[0_0_30px_rgba(255,255,255,0.2)]"
                            >
                                <Compass className="w-5 h-5" />
                                <span>Explore Top Matches</span>
                            </button>
                        </div>
                    </div>
                )}

                {/* No Data Overlay */}
                {festivals.length === 0 && (
                    <div className="absolute inset-0 flex items-center justify-center z-[1000] bg-black/60 backdrop-blur-sm">
                        <div className="bg-black border border-white/10 rounded-2xl p-8 text-center max-w-sm">
                            <h2 className="text-xl font-bold text-white mb-2">No Matches Found</h2>
                            <p className="text-gray-400 text-sm">
                                We couldn&apos;t find any festivals matching your library. Make sure your taste profile is synced!
                            </p>
                        </div>
                    </div>
                )}

                {/* Dynamic Festival Card Overlay */}
                {isCardOpen && selectedIndex >= 0 && (
                    <FestivalCard
                        festival={festivals[selectedIndex]}
                        hasNext={selectedIndex < festivals.length - 1}
                        hasPrev={selectedIndex > 0}
                        isOpen={isCardOpen}
                        onNext={handleNext}
                        onPrev={handlePrev}
                        onClose={handleCloseCard}
                        onExpandChange={setIsExpanded}
                    />
                )}
            </div>
    );
}
