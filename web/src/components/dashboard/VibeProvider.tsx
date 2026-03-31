"use client";

import { useEffect, useState, useRef } from "react";
import confetti from "canvas-confetti";
import { usePathname } from "next/navigation";

export default function VibeProvider({ children }: { children: React.ReactNode }) {
    const [settings, setSettings] = useState({
        cursorTracers: false,
        clickFireworks: false,
        partyMode: false,
        vignette: true,
    });
    
    const pathname = usePathname();

    useEffect(() => {
        const check = () => {
            const saved = localStorage.getItem("djwya_bs_settings");
            if (saved) {
                setSettings(JSON.parse(saved));
            }
        };
        
        check();
        const interval = setInterval(check, 1000); // Poll for changes
        return () => clearInterval(interval);
    }, [pathname]);

    useEffect(() => {
        if (!settings.clickFireworks) return;

        const handleClick = (e: MouseEvent) => {
            confetti({
                particleCount: 50,
                spread: 100,
                origin: { x: e.clientX / window.innerWidth, y: e.clientY / window.innerHeight },
                colors: ["#8b5cf6", "#ec4899", "#10b981"],
                shapes: ["circle", "square"],
                scalar: 0.5,
                zIndex: 10000
            });
        };

        window.addEventListener("click", handleClick);
        return () => window.removeEventListener("click", handleClick);
    }, [settings.clickFireworks]);

    return (
        <>
            {children}
            
            {/* Vibe Styles */}
            <style jsx global>{`
                body::after {
                    content: "";
                    position: fixed;
                    inset: 0;
                    box-shadow: inset 0 0 150px rgba(0,0,0,${settings.vignette ? 0.8 : 0});
                    pointer-events: none;
                    z-index: 9999;
                    transition: box-shadow 0.5s ease;
                }

                ${settings.partyMode ? `
                    @keyframes partyPulse {
                        0% { background-color: #09090b; }
                        25% { background-color: #1a0b1a; }
                        50% { background-color: #0b1a1a; }
                        75% { background-color: #1a1a0b; }
                        100% { background-color: #09090b; }
                    }
                    body {
                        animation: partyPulse 4s infinite linear;
                        transition: background-color 0.5s ease;
                    }
                ` : ""}

                ${settings.cursorTracers ? `
                    .tracer {
                        position: fixed;
                        width: 8px;
                        height: 8px;
                        background: #8b5cf6;
                        border-radius: 50%;
                        pointer-events: none;
                        z-index: 9998;
                        filter: blur(4px) drop-shadow(0 0 8px #8b5cf6);
                        opacity: 0.8;
                    }
                ` : ""}
            `}</style>

            {settings.cursorTracers && <CursorTracers />}
        </>
    );
}

function CursorTracers() {
    const tracersRef = useRef<HTMLDivElement[]>([]);
    const count = 12;

    useEffect(() => {
        const tracers: HTMLDivElement[] = [];
        for (let i = 0; i < count; i++) {
            const el = document.createElement("div");
            el.className = "tracer";
            document.body.appendChild(el);
            tracers.push(el);
        }
        tracersRef.current = tracers;

        const handleMove = (e: MouseEvent) => {
            tracers.forEach((el, i) => {
                setTimeout(() => {
                    el.style.left = e.clientX - 4 + "px";
                    el.style.top = e.clientY - 4 + "px";
                    el.style.opacity = (1 - i / count).toString();
                }, i * 30);
            });
        };

        window.addEventListener("mousemove", handleMove);
        return () => {
            window.removeEventListener("mousemove", handleMove);
            tracers.forEach(el => el.remove());
        };
    }, []);

    return null;
}
