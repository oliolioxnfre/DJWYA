"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Header from "@/components/dashboard/Header";
import { supabase } from "@/lib/supabaseClient";

export default function SettingsPage() {
    const [userId, setUserId] = useState<string | null>(null);
    const [username, setUsername] = useState("");
    const [avatarUrl, setAvatarUrl] = useState("");
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    const [settings, setSettings] = useState({
        cursorTracers: false,
        clickFireworks: false,
        partyMode: false,
        vignette: true,
    });

    useEffect(() => {
        const fetchProfile = async () => {
            const { data: { session } } = await supabase.auth.getSession();
            if (!session) return;
            
            setUserId(session.user.id);

            const { data } = await supabase
                .from("users")
                .select("username, avatar_url")
                .eq("id", session.user.id)
                .single();

            if (data) {
                setUsername(data.username || "");
                setAvatarUrl(data.avatar_url || "");
            }
            setLoading(false);
        };

        fetchProfile();

        const saved = localStorage.getItem("djwya_bs_settings");
        if (saved) {
            setSettings(JSON.parse(saved));
        }
    }, []);

    const toggle = (key: string) => {
        const next = { ...settings, [key]: !settings[key as keyof typeof settings] };
        setSettings(next);
        localStorage.setItem("djwya_bs_settings", JSON.stringify(next));
    };

    const handleSaveProfile = async () => {
        if (!userId) return;
        setSaving(true);

        try {
            // Check if username is taken (by someone else)
            const { data: existingUser } = await supabase
                .from("users")
                .select("id")
                .eq("username", username)
                .neq("id", userId)
                .maybeSingle();

            if (existingUser) {
                alert("That username is already taken. Choose something more unique.");
                setSaving(false);
                return;
            }

            const { error } = await supabase
                .from("users")
                .update({
                    username: username,
                    avatar_url: avatarUrl
                })
                .eq("id", userId);

            if (error) throw error;
            alert("Profile updated successfully!");
        } catch (err: any) {
            console.error("Error saving profile:", err);
            alert("Failed to save profile. Please try again.");
        } finally {
            setSaving(false);
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
            <div className="max-w-4xl mx-auto space-y-16">
                <Header />

                <div className="flex flex-col md:flex-row md:items-end justify-between gap-8">
                    <motion.header 
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-4"
                    >
                        <h1 className="text-7xl font-black italic tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-brand-purple to-pink-500 uppercase">
                            Settings
                        </h1>
                        <p className="text-zinc-500 text-sm font-bold tracking-widest uppercase">
                            Identity & Visual Overrides
                        </p>
                    </motion.header>

                    <button
                        onClick={handleSaveProfile}
                        disabled={saving}
                        className={`px-10 py-4 rounded-full font-black uppercase tracking-[0.2em] text-xs transition-all shadow-2xl ${
                            saving 
                                ? "bg-zinc-800 text-zinc-500" 
                                : "bg-white text-black hover:scale-105 active:scale-95 shadow-brand-purple/20"
                        }`}
                    >
                        {saving ? "Saving..." : "Save Changes"}
                    </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                    {/* Identity Section */}
                    <section className="space-y-8">
                        <h2 className="text-xs font-bold tracking-[0.4em] uppercase text-zinc-600 flex items-center gap-4">
                            Identity <div className="flex-1 h-px bg-white/5" />
                        </h2>
                        
                        <div className="space-y-6">
                            <div className="space-y-2">
                                <label className="text-[10px] font-black uppercase tracking-widest text-zinc-500 ml-2">Public Alias</label>
                                <input 
                                    type="text"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    placeholder="Enter username..."
                                    className="w-full bg-white/5 border border-white/10 p-5 rounded-3xl font-bold focus:border-brand-purple/50 focus:outline-none transition-all placeholder:text-zinc-700"
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="text-[10px] font-black uppercase tracking-widest text-zinc-500 ml-2">Avatar URL</label>
                                <input 
                                    type="text"
                                    value={avatarUrl}
                                    onChange={(e) => setAvatarUrl(e.target.value)}
                                    placeholder="https://..."
                                    className="w-full bg-white/5 border border-white/10 p-5 rounded-3xl font-bold focus:border-brand-purple/50 focus:outline-none transition-all placeholder:text-zinc-700"
                                />
                                <p className="text-[9px] text-zinc-700 ml-2 mt-1 italic">Use a public URL from Discord, Spotify, or Gravatar</p>
                            </div>
                        </div>
                    </section>

                    {/* Vibe Section */}
                    <section className="space-y-8">
                        <h2 className="text-xs font-bold tracking-[0.4em] uppercase text-zinc-600 flex items-center gap-4">
                            BS Effects <div className="flex-1 h-px bg-white/5" />
                        </h2>
                        
                        <div className="grid grid-cols-1 gap-4">
                            {Object.entries(settings).map(([key, val]) => (
                                <div 
                                    key={key} 
                                    className="bg-white/5 border border-white/10 rounded-[2rem] p-6 pr-8 flex items-center justify-between hover:border-white/20 transition-all group"
                                >
                                    <div>
                                        <h3 className="text-xs font-black uppercase tracking-wide group-hover:text-brand-purple transition-colors">
                                            {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                                        </h3>
                                        <p className="text-zinc-600 text-[10px] mt-0.5 leading-tight max-w-[180px]">
                                            {getDesc(key)}
                                        </p>
                                    </div>
                                    
                                    <button
                                        onClick={() => toggle(key)}
                                        className={`w-12 h-6 rounded-full p-1 transition-colors duration-500 ${
                                            val ? "bg-brand-purple" : "bg-white/10"
                                        }`}
                                    >
                                        <motion.div 
                                            className="w-4 h-4 bg-white rounded-full"
                                            animate={{ x: val ? 24 : 0 }}
                                        />
                                    </button>
                                </div>
                            ))}
                        </div>
                    </section>
                </div>

                {/* Profile Preview */}
                <section className="pt-8 flex items-center justify-center">
                    <div className="flex flex-col items-center gap-6 p-12 rounded-[4rem] bg-gradient-to-br from-brand-purple/10 to-transparent border border-white/5 w-full max-w-sm">
                        <div className="relative">
                            <img 
                                src={avatarUrl || `https://api.dicebear.com/7.x/pixel-art/svg?seed=${username}`}
                                alt="Preview"
                                className="w-32 h-32 rounded-3xl object-cover shadow-2xl border-2 border-brand-purple/20"
                                onError={(e) => {
                                    (e.target as any).src = `https://api.dicebear.com/7.x/pixel-art/svg?seed=${username}`;
                                }}
                            />
                            <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-brand-purple rounded-xl flex items-center justify-center text-black font-black text-xs shadow-lg">
                                ON
                            </div>
                        </div>
                        <div className="text-center">
                            <h3 className="text-2xl font-black italic uppercase tracking-tighter">{username || "USERNAME"}</h3>
                            <p className="text-[10px] font-bold tracking-[.3em] uppercase text-zinc-500 mt-1">Stargazer Elite</p>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    );
}

function getDesc(key: string) {
    switch (key) {
        case 'cursorTracers': return 'Add neon tracers that follow your mouse cursor.';
        case 'clickFireworks': return 'Ignite pixelated explosions every time you click.';
        case 'partyMode': return 'Dynamic background pulses & random colors.';
        case 'vignette': return 'Classic dark edges for maximum cinematic feel.';
        default: return '';
    }
}
