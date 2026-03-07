"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabaseClient";

export default function AuthCallbackPage() {
    const router = useRouter();
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const handleAuth = async () => {
            // Supabase automatically handles the URL hash/query params
            // and sets the local session. We just need to wait for it.
            const { data: { session }, error: sessionError } = await supabase.auth.getSession();

            if (sessionError) {
                console.error("Auth callback error:", sessionError.message);
                setError(sessionError.message);
                return;
            }

            if (session) {
                console.log("Session established! Checking for profile...");

                // Add a small check for username
                const { data: profile, error: profileError } = await supabase
                    .from("users")
                    .select("username")
                    .eq("id", session.user.id)
                    .single();

                if (profileError || !profile?.username) {
                    console.log("No username found. Redirecting to onboarding...");
                    router.push("/onboarding");
                } else {
                    console.log("Username found. Redirecting to dashboard...");
                    router.push("/dashboard");
                }
            } else {
                // If there's no session and the hash hasn't been processed yet, 
                // there's a chance auth state change listener will catch it.
                const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
                    if (event === "SIGNED_IN" && session) {
                        subscription.unsubscribe();

                        // Check profile here too
                        const { data: profile } = await supabase
                            .from("users")
                            .select("username")
                            .eq("id", session.user.id)
                            .single();

                        if (!profile?.username) {
                            router.push("/onboarding");
                        } else {
                            router.push("/dashboard");
                        }
                    }
                });
            }
        };

        handleAuth();
    }, [router]);

    return (
        <div className="flex min-h-screen items-center justify-center bg-black">
            <div className="text-center space-y-4">
                {error ? (
                    <div className="text-brand-pink text-xl font-bold">
                        <p>Authentication Failed</p>
                        <p className="text-sm text-zinc-400 mt-2">{error}</p>
                        <button
                            onClick={() => router.push("/")}
                            className="mt-4 px-6 py-2 bg-white/10 rounded-full hover:bg-white/20 text-white transition-colors"
                        >
                            Return Home
                        </button>
                    </div>
                ) : (
                    <>
                        <div className="w-16 h-16 border-4 border-brand-purple border-t-brand-neon rounded-full animate-spin mx-auto" />
                        <h2 className="text-2xl font-bold tracking-widest text-white/80 uppercase font-heading">
                            Authenticating...
                        </h2>
                        <p className="text-zinc-500 font-sans">Connecting to your DJWYA profile.</p>
                    </>
                )}
            </div>
        </div>
    );
}
