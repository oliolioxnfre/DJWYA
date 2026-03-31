"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabaseClient";
import { Session } from "@supabase/supabase-js";
import { CsvDropzone } from "@/components/dashboard/CsvDropzone";
import Header from "@/components/dashboard/Header";
import { StarChart } from "@/components/dashboard/StarChart";
import { TopArtistsBarChart } from "@/components/dashboard/TopArtistsBarChart";
import { TopSubgenresChart } from "@/components/dashboard/TopSubgenresChart";
import { motion } from "framer-motion";

export default function DashboardPage() {
    const [session, setSession] = useState<Session | null>(null);
    const [username, setUsername] = useState<string | null>(null);
    const [avatarUrl, setAvatarUrl] = useState<string | null>(null);
    const [dna, setDna] = useState<any>(null);
    const [subgenres, setSubgenres] = useState<any>(null);
    const [topArtists, setTopArtists] = useState<any[]>([]);
    const [electronicOnly, setElectronicOnly] = useState(false);
    const [songCount, setSongCount] = useState<number>(0);
    const [loading, setLoading] = useState(true);
    const [artistsLoading, setArtistsLoading] = useState(false);
    const router = useRouter();

    useEffect(() => {
        supabase.auth.getSession().then(({ data: { session } }) => {
            if (!session) {
                router.replace("/");
            } else {
                setSession(session);
                fetchUserData(session.user.id);
            }
        });

        const {
            data: { subscription },
        } = supabase.auth.onAuthStateChange((_event, session) => {
            setSession(session);
            if (!session) router.replace("/");
        });

        return () => subscription.unsubscribe();
    }, [router]);

    useEffect(() => {
        if (session?.user) {
            fetchTopArtists(session.user.id, electronicOnly);
        }
    }, [electronicOnly, session?.user]);

    const fetchTopArtists = async (userId: string, isElectronic: boolean) => {
        setArtistsLoading(true);
        try {
            // Fetch more library items if we need to filter down to 50 electronic artists
            const { data: libData, error: libError } = await supabase
                .from("user_lib")
                .select("count, artist_id")
                .eq("user_id", userId)
                .order("count", { ascending: false })
                .limit(isElectronic ? 150 : 50);

            if (libError) {
                console.error("Error fetching library data:", libError);
                return;
            }

            if (libData && libData.length > 0) {
                const artistIds = libData.map((item: any) => item.artist_id);
                
                // Fetch the names
                const { data: artistNames } = await supabase
                    .from("user_lib")
                    .select("artist_id, artists:artist_id!inner(name)")
                    .in("artist_id", artistIds);

                // Fetch electronic status by checking the genres table for the 'non-electronic' flag
                let electronicIds = new Set<string>();

                if (isElectronic) {
                    try {
                        const { data: genresData, error: genresError } = await supabase
                            .from("artist_genres")
                            .select(`
                                artist_id,
                                genres!inner (
                                    "non-electronic"
                                )
                            `)
                            .in("artist_id", artistIds);
                        
                        if (genresError) {
                            console.error("Error fetching artist genres:", genresError);
                        } else if (genresData) {
                            // An artist is considered electronic if they have at least one genre 
                            // where non-electronic is NOT true
                            for (const g of genresData) {
                                const isNonElectronic = (g.genres as any)?.["non-electronic"];
                                if (isNonElectronic !== true) {
                                    electronicIds.add(g.artist_id);
                                }
                            }
                        }
                    } catch (e) {
                        console.error("Failed to fetch artist_genres:", e);
                    }
                }

                // Map results back together
                const nameMap = (artistNames || []).reduce((acc: any, curr: any) => {
                    const id = curr.artist_id;
                    const name = curr.artists?.name;
                    if (id && name) acc[id] = name;
                    return acc;
                }, {});

                let formatted = libData.map((item: any) => ({
                    name: nameMap[item.artist_id] || "Unknown Artist",
                    count: item.count,
                    isElectronic: isElectronic ? electronicIds.has(item.artist_id) : true
                }));

                // If filter is active, filter them out and take the top 50
                if (isElectronic) {
                    formatted = formatted.filter((a: any) => a.isElectronic).slice(0, 50);
                }

                setTopArtists(formatted);
            } else {
                setTopArtists([]);
            }
        } catch (err) {
            console.error("Error in fetchTopArtists:", err);
        } finally {
            setArtistsLoading(false);
        }
    };


    const fetchUserData = async (userId: string) => {
        setLoading(true);
        try {
            // 1. Fetch User Profile (Username, DNA, Subgenres)
            const { data: profile } = await supabase
                .from("users")
                .select("username, avatar_url, sonic_dna, subgenres")
                .eq("id", userId)
                .single();

            if (profile) {
                if (profile.username) setUsername(profile.username);
                else router.push("/onboarding");
                
                setAvatarUrl(profile.avatar_url);
                setDna(profile.sonic_dna);
                setSubgenres(profile.subgenres);
            }

            // 2. Fetch Initial Top Artists (Handled by useEffect now)
            // fetchTopArtists(userId, false);

            // 3. Fetch Total Song Count
            const { count } = await supabase
                .from("user_lib")
                .select("*", { count: "exact", head: true })
                .eq("user_id", userId);
            
            setSongCount(count || 0);

        } catch (err) {
            console.error("Error fetching dashboard data:", err);
        } finally {
            setLoading(false);
        }
    };

    const handleResetTaste = async () => {
        const confirmed = window.confirm("Are you sure you want to reset your taste? This will wipe your library data and Sonic DNA.");
        if (!confirmed || !session?.user) return;

        try {
            setLoading(true);
            await supabase.from("user_lib").delete().eq("user_id", session.user.id);
            await supabase.from("users").update({ sonic_dna: null, subgenres: null }).eq("id", session.user.id);
            window.location.reload();
        } catch (err: any) {
            console.error("Error resetting taste:", err);
            alert("Failed to reset taste. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-black">
                <div className="w-16 h-16 border-4 border-white/20 border-t-brand-purple rounded-full animate-spin" />
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-zinc-950 text-white p-8 md:p-12 pt-32 md:pt-40 font-sans selection:bg-brand-purple selection:text-white">
            <div className="max-w-7xl mx-auto space-y-12">
                <Header />

                {/* Hero Header Section */}
                <motion.header 
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex flex-col md:flex-row md:items-end gap-12"
                >
                    <h1 className="text-7xl md:text-9xl font-black italic tracking-tighter text-brand-purple drop-shadow-[0_0_50px_rgba(139,92,246,0.3)] uppercase leading-none">
                        {username || "USERNAME"}
                    </h1>

                    <div className="flex items-center gap-3 pb-4 md:pb-8">
                        <span className="text-2xl md:text-3xl font-bold text-zinc-400">
                            {songCount.toLocaleString()}
                        </span>
                        <span className="text-sm font-bold tracking-[0.3em] text-zinc-600 uppercase pt-1">
                            Liked Artists
                        </span>
                    </div>
                </motion.header>

                {/* Main Dashboard Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-stretch">
                    
                    {/* Top Left: Sonic DNA StarChart (Expanded again) */}
                    <motion.section 
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.1 }}
                        className="lg:col-span-2 bg-white/[0.03] border border-white/10 rounded-[2.5rem] p-8 md:p-12 backdrop-blur-3xl relative overflow-hidden group shadow-2xl h-[750px]"
                    >
                        <h2 className="text-xs font-bold tracking-[0.3em] uppercase text-zinc-500 mb-8 flex items-center gap-2">
                             Sonic DNA <div className="w-12 h-px bg-white/10" />
                        </h2>
                        
                        <div className="flex items-center justify-center w-full h-[calc(100%-80px)]">
                            {dna ? (
                                <StarChart dna={dna} size={600} />
                            ) : (
                                <div className="text-center space-y-4">
                                    <div className="w-20 h-20 mx-auto border-2 border-dashed border-white/10 rounded-full flex items-center justify-center">
                                        <div className="w-10 h-10 bg-white/5 rounded-full animate-pulse" />
                                    </div>
                                    <p className="text-zinc-500 text-sm font-medium">DNA profile pending.</p>
                                </div>
                            )}
                        </div>

                        <div className="absolute top-0 right-0 p-8">
                            <button
                                onClick={() => router.push('/graph')}
                                className="w-8 h-8 flex items-center justify-center bg-brand-purple hover:bg-brand-purple/80 text-white rounded-full transition-all shadow-lg active:scale-95"
                                title="Explore Genre Map"
                            >
                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                </svg>
                            </button>
                        </div>
                    </motion.section>

                    {/* Top Right: Top Artists Bar Chart (Narrower again) */}
                    <motion.section 
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.2 }}
                        className="lg:col-span-1 bg-white/[0.03] border border-white/10 rounded-[2.5rem] p-8 md:p-10 backdrop-blur-3xl shadow-2xl flex flex-col h-[750px]"
                    >
                        <div className="flex justify-between items-center mb-10 relative">
                            <h2 className="text-xs font-bold tracking-[0.3em] uppercase text-zinc-500 flex items-center gap-2 m-0 mt-2">
                                 Top Artists <div className="w-12 h-px bg-white/10" />
                            </h2>
                            <button
                                onClick={() => setElectronicOnly(!electronicOnly)}
                                className={`absolute right-0 top-0 px-3 py-1.5 rounded-full text-[9px] font-black tracking-widest uppercase transition-colors border ${
                                    electronicOnly 
                                        ? "bg-brand-purple/20 text-brand-purple border-brand-purple/50" 
                                        : "bg-white/5 text-zinc-500 border-white/10 hover:text-white hover:bg-white/20"
                                }`}
                                title="Toggle Electronic Artists Only"
                            >
                                Electronic
                            </button>
                        </div>
                        <div className="flex-1 overflow-hidden relative">
                            {artistsLoading && (
                                <div className="absolute inset-x-0 top-0 h-1 bg-brand-purple/20 overflow-hidden z-30">
                                    <div className="w-1/2 h-full bg-brand-purple animate-shimmer" />
                                </div>
                            )}
                            <TopArtistsBarChart artists={topArtists} />
                        </div>
                    </motion.section>

                    {/* Bottom: Subgenre Pie Chart */}
                    <motion.section 
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="lg:col-span-3 bg-white/[0.03] border border-white/10 rounded-[2.5rem] p-8 md:p-12 backdrop-blur-3xl shadow-2xl"
                    >
                        <h2 className="text-xs font-bold tracking-[0.3em] uppercase text-zinc-500 mb-8 flex items-center gap-2">
                             Genre Distribution <div className="w-12 h-px bg-white/10" />
                        </h2>
                        <TopSubgenresChart subgenres={subgenres} />
                    </motion.section>
                </div>

                {/* Footer Management */}
                <section className="mt-16 pt-16 border-t border-white/5 grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="bg-white/5 rounded-3xl p-8 border border-white/5 hover:border-white/10 transition-colors">
                        <h3 className="text-xl font-bold mb-4">Update Library</h3>
                        <CsvDropzone onUploadComplete={() => window.location.reload()} />
                    </div>
                    <div className="bg-white/5 rounded-3xl p-8 border border-white/5 flex flex-col items-center justify-center text-center space-y-6">
                        <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center border border-red-500/20 text-red-500">
                            <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                        </div>
                        <div>
                            <h3 className="text-xl font-bold mb-1">Reset Profile</h3>
                            <p className="text-zinc-500 text-sm">Clear your library and reboot your DNA.</p>
                        </div>
                        <button
                            onClick={handleResetTaste}
                            className="px-8 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-500 border border-red-500/20 rounded-full transition-all font-bold text-xs uppercase tracking-widest"
                        >
                            Confirm Reset
                        </button>
                    </div>
                </section>
            </div>
            
            <style jsx global>{`
                @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@100;400;700;900&display=swap');
                
                :root {
                    --brand-purple: #8b5cf6;
                }
                
                body {
                    font-family: 'Outfit', sans-serif;
                    background-color: #09090b;
                }
                
                .font-heading {
                    font-family: 'Outfit', sans-serif;
                }

                @keyframes shimmer {
                    0% { transform: translateX(-100%); }
                    100% { transform: translateX(200%); }
                }

                .animate-shimmer {
                    animation: shimmer 1.5s infinite linear;
                }
            `}</style>
        </div>
    );
}
