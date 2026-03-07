"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabaseClient";
import Image from "next/image";

export default function OnboardingPage() {
    const [username, setUsername] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [user, setUser] = useState<any>(null);
    const router = useRouter();

    useEffect(() => {
        const checkUser = async () => {
            const { data: { session } } = await supabase.auth.getSession();
            if (!session) {
                router.replace("/");
                return;
            }
            setUser(session.user);

            // Check if they already have a username
            const { data: profile } = await supabase
                .from("users")
                .select("username")
                .eq("id", session.user.id)
                .single();

            if (profile?.username) {
                router.replace("/dashboard");
            }
        };

        checkUser();
    }, [router]);

    const handleOnboarding = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        const trimmedUsername = username.trim().toLowerCase();
        if (trimmedUsername.length < 3) {
            setError("Username must be at least 3 characters.");
            setLoading(false);
            return;
        }

        try {
            const { error: updateError } = await supabase
                .from("users")
                .update({
                    username: trimmedUsername,
                    updated_at: new Date().toISOString()
                })
                .eq("id", user.id);

            if (updateError) {
                if (updateError.code === "23505") { // Unique constraint violation
                    setError("That username is already taken.");
                } else {
                    setError(updateError.message);
                }
                return;
            }

            // Success! Go to dashboard
            router.push("/dashboard");
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-black selection:bg-brand-pink/30">
            {/* Background effects */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-brand-purple/20 rounded-full blur-[150px] -z-10 pointer-events-none" />

            <div className="w-full max-w-md z-10 space-y-8 bg-white/5 border border-white/10 rounded-3xl p-10 backdrop-blur-xl">
                <div className="text-center space-y-4">
                    <Image
                        src="/logo.png"
                        alt="DJWYA Logo"
                        width={120}
                        height={120}
                        className="mx-auto drop-shadow-[0_0_20px_rgba(139,92,246,0.3)] mb-6"
                    />
                    <h1 className="text-3xl font-black font-heading tracking-tight uppercase text-white">
                        Finish your profile
                    </h1>
                    <p className="text-zinc-400 text-sm">
                        Choose a unique username to represent your Sonic DNA.
                    </p>
                </div>

                <form onSubmit={handleOnboarding} className="space-y-6">
                    <div className="space-y-2">
                        <label htmlFor="username" className="text-xs font-bold text-zinc-500 uppercase tracking-widest ml-1">
                            Username
                        </label>
                        <input
                            id="username"
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="e.g. technovibe"
                            className="w-full bg-black/50 border border-white/10 rounded-2xl px-6 py-4 text-white focus:outline-none focus:ring-2 focus:ring-brand-purple/50 focus:border-brand-purple/50 transition-all placeholder:text-zinc-700"
                            required
                        />
                    </div>

                    {error && (
                        <p className="text-brand-pink text-xs font-medium text-center animate-pulse">
                            {error}
                        </p>
                    )}

                    <button
                        type="submit"
                        disabled={loading || username.length < 3}
                        className="w-full group relative flex items-center justify-center px-8 py-4 bg-white text-black font-bold rounded-2xl transition-all hover:scale-105 active:scale-95 disabled:opacity-50 disabled:hover:scale-100 disabled:cursor-not-allowed overflow-hidden"
                    >
                        <span className="relative z-10">{loading ? "Setting Up..." : "Enter the Rave"}</span>
                        <div className="absolute inset-x-0 bottom-0 h-1 bg-gradient-to-r from-brand-neon via-brand-purple to-brand-pink transform scale-x-0 group-hover:scale-x-100 transition-transform origin-left duration-500" />
                    </button>
                </form>
            </div>
        </main>
    );
}
