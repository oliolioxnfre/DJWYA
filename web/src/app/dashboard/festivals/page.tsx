"use client";

import React, { useState, useEffect, useMemo } from "react";
import dynamic from "next/dynamic";
import { Loader2, AlertCircle, Compass, Search, X, MapPin, Settings2 } from "lucide-react";
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
    const [searchQuery, setSearchQuery] = useState("");
    const [isSearchFocused, setIsSearchFocused] = useState(false);
    const [isIntroDismissed, setIsIntroDismissed] = useState(false);

    // Settings States
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);
    const [sortBy, setSortBy] = useState("total_match");
    const [filterFullyAnnounced, setFilterFullyAnnounced] = useState(false);
    const [filterRegion, setFilterRegion] = useState("All");

    const US_REGIONS: Record<string, string[]> = {
        "East Coast": ["Maine", "New Hampshire", "Massachusetts", "Rhode Island", "Connecticut", "New York", "New Jersey", "Pennsylvania", "Delaware", "Maryland", "Virginia", "North Carolina", "South Carolina", "Georgia", "Florida", "District of Columbia"],
        "Midwest": ["Ohio", "Indiana", "Illinois", "Michigan", "Wisconsin", "Minnesota", "Iowa", "Missouri", "North Dakota", "South Dakota", "Nebraska", "Kansas"],
        "South": ["Kentucky", "Tennessee", "Alabama", "Mississippi", "Arkansas", "Louisiana", "Oklahoma", "Texas", "West Virginia"],
        "Mountains & Southwest": ["Montana", "Idaho", "Wyoming", "Colorado", "New Mexico", "Arizona", "Utah", "Nevada"],
        "West Coast": ["Washington", "Oregon", "California", "Alaska", "Hawaii"]
    };

    const determineRegion = (state?: string, country?: string) => {
        if (!country) return "Unknown";
        if (country !== "United States") {
            if (country === "Canada") return "Canada";
            if (["Mexico", "Colombia", "Brazil", "Argentina"].includes(country)) return "Latin America";
            if (["Thailand", "Philippines", "Australia", "Japan"].includes(country)) return "Asia & Oceania";
            if (["Egypt", "South Africa"].includes(country)) return "Africa & Middle East";
            return "Europe"; // Defaulting the rest of International to Europe
        }
        if (!state) return "Unknown";
        
        for (const [regionName, states] of Object.entries(US_REGIONS)) {
            if (states.includes(state)) {
                return regionName;
            }
        }
        return "Unknown";
    };

    const processedFestivals = useMemo(() => {
        let result = [...festivals];

        if (filterFullyAnnounced) {
            result = result.filter(f => f.tba !== true);
        }

        if (filterRegion !== "All") {
            result = result.filter(f => determineRegion(f.state, f.country) === filterRegion);
        }

        result.sort((a, b) => {
            if (sortBy === "total_match") {
                return (b.total_match || 0) - (a.total_match || 0);
            } else if (sortBy === "total_artists") {
                return (b.total_artists || 0) - (a.total_artists || 0);
            } else if (sortBy === "synergy_match") {
                return (b.synergy_match || 0) - (a.synergy_match || 0);
            } else if (sortBy === "artist_score") {
                return (b.artist_score || 0) - (a.artist_score || 0);
            } else if (sortBy === "artist_perc") {
                return (b.artist_perc || 0) - (a.artist_perc || 0);
            }
            return 0;
        });

        return result;
    }, [festivals, filterFullyAnnounced, sortBy, filterRegion]);

    // Reset card when filters change
    useEffect(() => {
        setIsCardOpen(false);
        setSelectedIndex(-1);
    }, [filterFullyAnnounced, sortBy, filterRegion]);

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

                // Filter out festivals without location coordinates OR those that have already ended
                const today = new Date().toISOString().split('T')[0];
                
                const mappedMatches = (json.data || []).map((f: any) => ({
                    ...f,
                    lat: f.lat ? parseFloat(f.lat) : null,
                    lng: f.lng ? parseFloat(f.lng) : null,
                    location: f.location,
                    start_date: f.start_date,
                    end_date: f.end_date,
                    state: f.state,
                    country: f.country,
                    size: f.size,
                    type: f.type,
                    fest_subgenres: f.fest_subgenres,
                    tba: f.tba
                })).filter((f: any) => 
                    f.lat !== null && 
                    f.lng !== null && 
                    (!f.end_date || f.end_date >= today)
                );

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
        if (processedFestivals.length > 0) {
            setHasStarted(true);
            setSelectedIndex(0);
            setIsCardOpen(true);
        }
    };

    const handleNext = () => {
        if (selectedIndex < processedFestivals.length - 1) {
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
        setSearchQuery("");
        setIsSearchFocused(false);
    };

    const filteredFestivals = searchQuery.trim() === ""
        ? []
        : processedFestivals
            .map((f, index) => ({ ...f, originalIndex: index }))
            .filter(f => f.festival.toLowerCase().includes(searchQuery.toLowerCase()))
            .slice(0, 8);

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

            {/* Top Center Search Bar */}
            <div className="fixed top-6 left-1/2 -translate-x-1/2 z-[2500] w-full max-w-md px-4">
                <div className="relative group">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <Search className="h-4 w-4 text-gray-400 group-focus-within:text-purple-400 transition-colors" />
                    </div>
                    <input
                        type="text"
                        placeholder="Search for a festival..."
                        className="block w-full pl-11 pr-11 py-3 bg-[#1a1a24]/80 backdrop-blur-xl border border-white/10 rounded-xl text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 transition-all shadow-2xl"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        onFocus={() => setIsSearchFocused(true)}
                    />
                    {searchQuery && (
                        <button
                            onClick={() => {
                                setSearchQuery("");
                                setIsSearchFocused(false);
                            }}
                            className="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-500 hover:text-white transition-colors"
                        >
                            <X className="h-4 w-4" />
                        </button>
                    )}
                </div>

                {/* Search Results Dropdown */}
                {isSearchFocused && filteredFestivals.length > 0 && (
                    <div className="absolute mt-2 w-full left-0 px-4">
                        <div className="bg-[#1a1a24]/95 backdrop-blur-2xl border border-white/10 rounded-xl shadow-2xl overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
                            {filteredFestivals.map((result) => {
                                const color = result.synergy_match > 80 ? "#22c55e" : result.synergy_match > 50 ? "#eab308" : "#ef4444";
                                return (
                                    <button
                                        key={result.originalIndex}
                                        className="w-full text-left px-4 py-3 hover:bg-purple-500/10 flex items-center gap-3 transition-colors border-b border-white/5 last:border-0"
                                        onClick={() => handleSelectFestival(result.originalIndex)}
                                    >
                                        <div
                                            className="w-2 h-2 rounded-full shrink-0 shadow-[0_0_8px_rgba(168,85,247,0.5)]"
                                            style={{ backgroundColor: color }}
                                        />
                                        <div className="flex flex-col min-w-0">
                                            <span className="text-sm font-medium text-gray-200 truncate">{result.festival}</span>
                                            <div className="flex items-center gap-2">
                                                <span className="text-[10px] text-gray-500 uppercase tracking-wider flex items-center">
                                                    <MapPin className="w-2.5 h-2.5 mr-1" />
                                                    {result.location}
                                                </span>
                                                <span className="text-[10px] font-bold text-purple-400">
                                                    {Math.round(result.synergy_match)}% Match
                                                </span>
                                            </div>
                                        </div>
                                    </button>
                                );
                            })}
                        </div>
                    </div>
                )}
            </div>

            {/* Bottom Pill Navigation */}
            {processedFestivals.length > 0 && !isCardOpen && !isExpanded && (
                <div className="fixed bottom-10 left-1/2 -translate-x-1/2 z-[2100]">
                    <div className="flex items-stretch h-16 shadow-[0_0_30px_rgba(168,85,247,0.4)] rounded-full group cursor-pointer hover:scale-105 active:scale-95 transition-transform overflow-hidden">
                        {/* GO Button */}
                        <button
                            onClick={handleStartFinder}
                            className="flex items-center justify-center px-12 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 transition-all border border-white/20 border-r-0 rounded-l-full"
                            title="Discovery Finder"
                        >
                            <span className="text-3xl font-black tracking-widest text-white mt-0.5">GO</span>
                        </button>
                        
                        {/* Divider Gap Line */}
                        <div className="w-[1px] bg-white/20 self-center h-8" />
                        
                        {/* Settings Button */}
                        <button
                            onClick={() => setIsSettingsOpen(!isSettingsOpen)}
                            className={`flex items-center justify-center px-6 bg-gradient-to-r from-indigo-600 to-pink-600 hover:from-indigo-500 hover:to-pink-500 transition-all border border-white/20 border-l-0 rounded-r-full ${isSettingsOpen ? 'brightness-125' : ''}`}
                            title="Filters & Sorting"
                        >
                            <Settings2 className="w-6 h-6 text-white" />
                        </button>
                    </div>
                </div>
            )}

            {/* Settings Menu Panel */}
            {isSettingsOpen && !isCardOpen && !isExpanded && (
                <div className="fixed bottom-32 left-1/2 -translate-x-1/2 z-[2100] w-[320px] bg-black/80 backdrop-blur-2xl border border-white/10 rounded-3xl p-6 shadow-2xl animate-in fade-in slide-in-from-bottom-4 duration-300">
                    <div className="flex justify-between items-center mb-6">
                        <h3 className="text-white font-bold text-lg tracking-tight">Display Settings</h3>
                        <button onClick={() => setIsSettingsOpen(false)} className="text-gray-400 hover:text-white transition-colors">
                            <X className="w-5 h-5" />
                        </button>
                    </div>

                    <div className="space-y-6">
                        {/* Filters */}
                        <div>
                            <h4 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-3">Filters</h4>
                            <label className="flex items-center justify-between cursor-pointer group">
                                <span className="text-sm text-gray-300 group-hover:text-white transition-colors">Fully Announced Only</span>
                                <div className="relative">
                                    <input 
                                        type="checkbox" 
                                        className="sr-only" 
                                        checked={filterFullyAnnounced}
                                        onChange={(e) => setFilterFullyAnnounced(e.target.checked)}
                                    />
                                    <div className={`block w-10 h-6 rounded-full transition-colors ${filterFullyAnnounced ? 'bg-purple-500' : 'bg-white/10'}`}></div>
                                    <div className={`absolute left-1 top-1 bg-white w-4 h-4 rounded-full transition-transform ${filterFullyAnnounced ? 'transform translate-x-4' : ''}`}></div>
                                </div>
                            </label>
                        </div>
                        <div className="h-px bg-white/10 w-full" />

                        {/* Region Filter */}
                        <div className="z-50 relative">
                            <h4 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-3">Region</h4>
                            <div className="relative">
                                <select 
                                    value={filterRegion}
                                    onChange={(e) => setFilterRegion(e.target.value)}
                                    className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-purple-500 transition-colors appearance-none cursor-pointer hover:bg-black/60"
                                >
                                    <option value="All">All Regions</option>
                                    <optgroup label="United States" className="bg-[#1a1a24] text-white">
                                        <option value="East Coast">East Coast</option>
                                        <option value="Midwest">Midwest</option>
                                        <option value="South">South</option>
                                        <option value="Mountains & Southwest">Mountains & Southwest</option>
                                        <option value="West Coast">West Coast</option>
                                    </optgroup>
                                    <optgroup label="International" className="bg-[#1a1a24] text-white">
                                        <option value="Canada">Canada</option>
                                        <option value="Europe">Europe</option>
                                        <option value="Latin America">Latin America</option>
                                        <option value="Asia & Oceania">Asia & Oceania</option>
                                        <option value="Africa & Middle East">Africa & Middle East</option>
                                    </optgroup>
                                </select>
                                <div className="absolute right-4 top-1/2 transform -translate-y-1/2 pointer-events-none text-gray-400">
                                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                        <polyline points="6 9 12 15 18 9"></polyline>
                                    </svg>
                                </div>
                            </div>
                        </div>

                        <div className="h-px bg-white/10 w-full" />

                        {/* Sorting */}
                        <div>
                            <h4 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-3">Sort By</h4>
                            <div className="space-y-3">
                                {[
                                    { id: 'total_match', label: 'Total Match Score (Default)' },
                                    { id: 'synergy_match', label: 'DNA Synergy Match' },
                                    { id: 'artist_perc', label: 'Artist Overlap %' },
                                    { id: 'artist_score', label: 'Artist Overlap Score' },
                                    { id: 'total_artists', label: 'Lineup Size' }
                                ].map(sortOpt => (
                                    <label key={sortOpt.id} className="flex items-center space-x-3 cursor-pointer group">
                                        <div className="relative flex items-center justify-center">
                                            <input 
                                                type="radio" 
                                                name="sortOpt" 
                                                className="sr-only"
                                                checked={sortBy === sortOpt.id}
                                                onChange={() => setSortBy(sortOpt.id)}
                                            />
                                            <div className={`w-4 h-4 rounded-full border flex items-center justify-center transition-colors ${sortBy === sortOpt.id ? 'border-purple-500' : 'border-gray-500 group-hover:border-white'}`}>
                                                {sortBy === sortOpt.id && (
                                                    <div className="w-2 h-2 rounded-full bg-purple-500" />
                                                )}
                                            </div>
                                        </div>
                                        <span className={`text-sm transition-colors ${sortBy === sortOpt.id ? 'text-white font-medium' : 'text-gray-400 group-hover:text-gray-200'}`}>
                                            {sortOpt.label}
                                        </span>
                                    </label>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            
            <div className={`absolute inset-0 transition-all duration-700 ease-in-out ${isExpanded ? 'blur-xl scale-105 opacity-40' : 'blur-0 scale-100 opacity-100'}`}>
                    <MapBox
                        festivals={processedFestivals}
                        selectedIndex={isCardOpen ? selectedIndex : -1}
                        onSelectFestival={handleSelectFestival}
                    />
                </div>

                {/* Intro Overlay */}
                {!hasStarted && !isIntroDismissed && processedFestivals.length > 0 && (
                    <div className="absolute inset-x-8 top-32 mx-auto max-w-lg z-[1000] pointer-events-none">
                        <div className="bg-black/60 backdrop-blur-xl border border-white/10 rounded-3xl p-8 text-center shadow-2xl pointer-events-auto relative">
                            {/* Close button */}
                            <button 
                                onClick={() => setIsIntroDismissed(true)}
                                className="absolute top-4 right-4 text-gray-500 hover:text-white transition-colors"
                            >
                                <X className="w-5 h-5" />
                            </button>
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
                {processedFestivals.length === 0 && (
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
                        festival={processedFestivals[selectedIndex]}
                        hasNext={selectedIndex < processedFestivals.length - 1}
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
