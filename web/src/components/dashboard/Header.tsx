"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Header() {
    const pathname = usePathname();
    const isDashboard = pathname === "/dashboard";

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
                            className="text-[10px] font-bold tracking-[.25em] uppercase text-white transition-all hover:opacity-70"
                        >
                            Dashboard
                        </Link>
                        <Link 
                            href="/dashboard/festivals" 
                            className="text-[10px] font-bold tracking-[.25em] uppercase text-zinc-500 transition-all hover:text-white"
                        >
                            Festival Map
                        </Link>
                        <Link 
                            href="/graph" 
                            className="text-[10px] font-bold tracking-[.25em] uppercase text-zinc-500 transition-all hover:text-white"
                        >
                            Genre Network
                        </Link>
                    </nav>
                )}
            </div>
        </div>
    );
}
