"use client";

import Image from "next/image";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabaseClient";
import { Session } from "@supabase/supabase-js";

export default function DashboardPage() {
    const [session, setSession] = useState<Session | null>(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        supabase.auth.getSession().then(({ data: { session } }) => {
            if (!session) {
                router.replace("/");
            } else {
                setSession(session);
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
                                Welcome back, {session?.user?.user_metadata?.full_name || session?.user?.email}
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
                        <h2 className="text-2xl font-bold font-heading mb-4">Your Sonic DNA</h2>
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
                            <h3 className="text-xl font-bold">{session?.user?.user_metadata?.full_name}</h3>
                            <p className="text-zinc-400 text-sm">Ravers Elite</p>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    );
}
