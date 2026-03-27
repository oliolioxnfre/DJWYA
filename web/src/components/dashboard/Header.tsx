"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Header() {
    const pathname = usePathname();

    const navLinks = [
        { name: "Dashboard", href: "/dashboard" },
        { name: "Genres", href: "/graph" },
        { name: "Festivals", href: "/dashboard/festivals" },
    ];

    return (
        <div className="fixed top-0 left-0 right-0 z-[2000] p-6 pointer-events-none">
            {/* Logo - Top Left */}
            <div className="absolute top-6 left-8 pointer-events-auto">
                <Link href="/dashboard" className="transition-transform hover:scale-105 active:scale-95 block">
                    <Image
                        src="/logo.png"
                        alt="DJWYA Logo"
                        width={60}
                        height={60}
                        className="drop-shadow-[0_0_20px_rgba(139,92,246,0.5)]"
                    />
                </Link>
            </div>

            {/* Navigation Buttons - Dead Center */}
            <nav className="mx-auto w-fit flex items-center gap-1 p-1 rounded-full bg-black/40 backdrop-blur-xl border border-white/10 pointer-events-auto shadow-[0_0_30px_rgba(0,0,0,0.5)]">
                {navLinks.map((link) => (
                    <Link
                        key={link.href}
                        href={link.href}
                        className={`px-6 py-2 rounded-full text-[10px] font-bold tracking-[0.2em] uppercase transition-all duration-300 ${
                            pathname === link.href
                                ? "bg-white text-black shadow-[0_0_25px_rgba(255,255,255,0.4)]"
                                : "text-zinc-500 hover:text-white hover:bg-white/5"
                        }`}
                    >
                        {link.name}
                    </Link>
                ))}
            </nav>
        </div>
    );
}
