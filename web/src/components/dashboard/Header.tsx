"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";
import { supabase } from "@/lib/supabaseClient";

export default function Header() {
    const pathname = usePathname();
    const isDashboard = ["/dashboard", "/dashboard/settings"].includes(pathname);
    const [avatarUrl, setAvatarUrl] = useState<string | null>(null);

    useEffect(() => {
        if (!isDashboard) return;

        const fetchPfp = async () => {
            const { data: { session } } = await supabase.auth.getSession();
            if (!session) return;

            const { data } = await supabase
                .from("users")
                .select("avatar_url")
                .eq("id", session.user.id)
                .single();

            if (data) {
                setAvatarUrl(data.avatar_url);
            }
        };

        fetchPfp();
    }, [isDashboard]);

    return (
        <div className="fixed top-0 left-0 right-0 z-[2000] p-6 pointer-events-none">
            {/* Logo Area - Top Left */}
            <div className="absolute top-6 left-8 pointer-events-auto flex items-center gap-8">
                <Link href="/dashboard" className="transition-transform hover:scale-105 active:scale-95 block">
                    <Image
                        src="/logo.png"
                        alt="DJWYA Logo"
                        width={60}
                        height={60}
                        className="drop-shadow-[0_0_20px_rgba(139,92,246,0.5)]"
                    />
                </Link>

                {/* Local Nav for Dashboard - Minimalistic */}
                {isDashboard && (
                    <nav className="flex items-center gap-6 pt-1">
                        <Link 
                            href="/dashboard" 
                            className={`text-[10px] font-bold tracking-[.25em] uppercase transition-all hover:opacity-70 ${(pathname as string) === "/dashboard" ? "text-white" : "text-zinc-500"}`}
                        >
                            Dashboard
                        </Link>
                        <Link 
                            href="/dashboard/festivals" 
                            className={`text-[10px] font-bold tracking-[.25em] uppercase transition-all hover:white ${(pathname as string) === "/dashboard/festivals" ? "text-white" : "text-zinc-500"}`}
                        >
                            Festival Map
                        </Link>
                        <Link 
                            href="/graph" 
                            className={`text-[10px] font-bold tracking-[.25em] uppercase transition-all hover:white ${(pathname as string) === "/graph" ? "text-white" : "text-zinc-500"}`}
                        >
                            Genre Network
                        </Link>
                        <Link 
                            href="/dashboard/settings" 
                            className={`text-[10px] font-bold tracking-[.25em] uppercase transition-all hover:white ${(pathname as string) === "/dashboard/settings" ? "text-white" : "text-zinc-500"}`}
                        >
                            Settings
                        </Link>
                    </nav>
                )}
            </div>

            {/* Profile Picture - Top Right */}
            {isDashboard && avatarUrl && (
                <div className="absolute top-8 right-10 pointer-events-auto">
                    <Link href="/dashboard/settings">
                        <img 
                            src={avatarUrl}
                            alt="Profile"
                            className="w-10 h-10 rounded-full object-cover border border-white/20 shadow-lg hover:scale-110 active:scale-95 transition-transform"
                        />
                    </Link>
                </div>
            )}
        </div>
    );
}
