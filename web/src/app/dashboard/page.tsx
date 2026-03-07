"use client";

import Image from "next/image";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabaseClient";
import { Session } from "@supabase/supabase-js";
import { CsvDropzone } from "@/components/dashboard/CsvDropzone";

export default function DashboardPage() {
    const [session, setSession] = useState<Session | null>(null);
    const [username, setUsername] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        supabase.auth.getSession().then(({ data: { session } }) => {
            if (!session) {
                router.replace("/");
            } else {
                setSession(session);

                // Check for username
                supabase
                    .from("users")
                    .select("username")
                    .eq("id", session.user.id)
                    .single()
                    .then(({ data: profile }) => {
                        if (profile?.username) {
                            setUsername(profile.username);
                        } else {
                            router.push("/onboarding");
                        }
                    });
            }
            setLoading(false);
        });

        const {
            data: { subscription },
        } = supabase.auth.onAuthStateChange((_event, session) => {
            setSession(session);
            if (!session) router.replace("/");
        });

        return () => subscription.unsubscribe();
    }, [router]);

    const handleResetTaste = async () => {
        const confirmed = window.confirm("Are you sure you want to reset your taste? This will wipe your library data and Sonic DNA.");
        if (!confirmed || !session?.user) return;

        try {
            setLoading(true);
            // Delete from user_lib
            const { error: libError } = await supabase
                .from("user_lib")
                .delete()
                .eq("user_id", session.user.id);

            if (libError) throw libError;

            // Update user's sonic_dna and subgenres to null
            const { error: userError } = await supabase
                .from("users")
                .update({ sonic_dna: null, subgenres: null })
                .eq("id", session.user.id);

            if (userError) throw userError;

            // Simple reload to refresh all states
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
                <div className="w-16 h-16 border-4 border-white/20 border-t-white rounded-full animate-spin" />
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-black text-white p-8 md:p-12 font-sans">
            <div className="max-w-7xl mx-auto space-y-12">
                <header className="flex justify-between items-center border-b border-white/10 pb-6">
                    <div className="flex items-center gap-6">
                        <Image
                            src="/logo.png"
                            alt="DJWYA Logo"
                            width={80}
                            height={80}
                            className="drop-shadow-[0_0_15px_rgba(139,92,246,0.3)]"
                        />
                        <div>
                            <h1 className="text-2xl md:text-3xl font-black font-heading tracking-tight uppercase">
                                Dashboard
                            </h1>
                            <p className="text-sm text-zinc-400">
                                Welcome back, {username ? `${username}` : (session?.user?.user_metadata?.full_name || session?.user?.email)}
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={() => supabase.auth.signOut()}
                        className="px-6 py-2 rounded-full border border-white/20 hover:bg-white/10 transition-colors text-sm font-medium"
                    >
                        Sign Out
                    </button>
                </header>

                <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="col-span-1 md:col-span-2 bg-white/5 border border-white/10 rounded-3xl p-8 backdrop-blur-md">
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-2xl font-bold font-heading">Your Sonic DNA</h2>
                            <button
                                onClick={() => router.push('/graph')}
                                className="text-sm px-4 py-2 bg-brand-purple/20 hover:bg-brand-purple/40 border border-brand-purple/30 rounded-full transition-all flex items-center gap-2"
                            >
                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                </svg>
                                Explore Genre Map
                            </button>
                        </div>
                        <div className="w-full aspect-video bg-black/50 rounded-2xl border border-white/5 flex items-center justify-center flex-col text-zinc-500">
                            <svg className="w-12 h-12 mb-4 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                            </svg>
                            <p>StarChart Engine Initializing...</p>
                            <p className="text-sm mt-2 max-w-sm text-center">We will import your data from Spotify/Last.fm to generate a 7-axis Vibe map.</p>
                        </div>
                    </div>

                    <div className="bg-white/5 border border-white/10 rounded-3xl p-8 backdrop-blur-md flex flex-col items-center justify-center space-y-4 text-center">
                        {session?.user?.user_metadata?.avatar_url && (
                            <img
                                src={session.user.user_metadata.avatar_url}
                                alt="Profile"
                                className="w-32 h-32 rounded-full border-4 border-brand-purple/50 shadow-[0_0_30px_rgba(139,92,246,0.3)]"
                            />
                        )}
                        <div>
                            <h3 className="text-xl font-bold">{username ? `${username}` : session?.user?.user_metadata?.full_name}</h3>
                            <p className="text-zinc-400 text-sm">Big Time Baller</p>
                        </div>
                    </div>
                </section>

                <section className="mt-8">
                    <h2 className="text-2xl font-bold font-heading mb-6 border-b border-white/10 pb-4">Manage Library</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="bg-white/5 border border-white/10 rounded-3xl p-8 backdrop-blur-md">
                            <h3 className="text-xl font-bold mb-2">Import from Spotify</h3>
                            <p className="text-zinc-400 text-sm mb-6">Upload your exported liked songs CSV to generate your Sonic DNA and find matching festivals.</p>
                            <CsvDropzone onUploadComplete={() => {
                                // Refresh DNA or UI state here later
                                console.log("Upload complete, refreshing data...");
                            }} />
                        </div>
                        <div className="bg-white/5 border border-white/10 rounded-3xl p-8 backdrop-blur-md flex flex-col items-center justify-center text-center">
                            <div className="p-4 bg-red-500/10 rounded-full border border-red-500/20 mb-4 text-red-500">
                                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                            </div>
                            <h3 className="text-xl font-bold mb-2 text-white">Reset Taste</h3>
                            <p className="text-zinc-400 text-sm mb-6">Wipe your entire library and start fresh with a new Sonic DNA profile.</p>
                            <button
                                onClick={handleResetTaste}
                                className="px-6 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-500 border border-red-500/20 rounded-full transition-all font-medium text-sm"
                            >
                                Reset My Profile
                            </button>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    );
}
