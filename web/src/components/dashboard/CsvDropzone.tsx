"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import Papa from "papaparse";
import { supabase } from "@/lib/supabaseClient";

interface CsvDropzoneProps {
    onUploadComplete?: () => void;
}

export function CsvDropzone({ onUploadComplete }: CsvDropzoneProps) {
    const [isUploading, setIsUploading] = useState(false);
    const [filterElectronic, setFilterElectronic] = useState(false);
    const [statusText, setStatusText] = useState("");
    const [error, setError] = useState<string | null>(null);

    const onDrop = useCallback(async (acceptedFiles: File[]) => {
        const file = acceptedFiles[0];
        if (!file) return;

        setIsUploading(true);
        setError(null);
        setStatusText("Parsing CSV...");

        Papa.parse(file, {
            header: true,
            skipEmptyLines: true,
            complete: async (results) => {
                try {
                    const data = results.data as any[];
                    setStatusText("Extracting Artists...");

                    // Same extraction logic as app.py
                    const electronicArtists: Record<string, { original_name: string; count: number; genres: string[] }> = {};

                    data.forEach((row) => {
                        const rawArtists = row["Artist Name(s)"] || row["Artist"] || "";
                        const csvGenresRaw = row["Genres"] || "";

                        const trackArtists = rawArtists.split(";").map((a: string) => a.trim()).filter(Boolean);
                        const csvGenresList = csvGenresRaw
                            ? csvGenresRaw.split(",").map((g: string) => g.trim().toLowerCase().replace(/ /g, "-")).filter(Boolean)
                            : [];

                        trackArtists.forEach((artistName: string) => {
                            const normName = artistName.toLowerCase().trim();
                            if (electronicArtists[normName]) {
                                electronicArtists[normName].count += 1;
                            } else {
                                electronicArtists[normName] = {
                                    original_name: artistName,
                                    count: 1,
                                    genres: csvGenresList
                                };
                            }
                        });
                    });

                    // Format specifically for the API
                    const artistRequests = Object.values(electronicArtists).map(artist => ({
                        name: artist.original_name,
                        fallback_genres: artist.genres,
                        count: artist.count
                    }));

                    setStatusText("Getting User Session...");
                    const { data: { session } } = await supabase.auth.getSession();
                    if (!session) throw new Error("Not authenticated");

                    setStatusText("Analyzing Sonic DNA (This may take a minute)...");
                    // Assuming FastAPI is running strictly on local port 8000 for now
                    const response = await fetch("http://localhost:8000/api/ingest", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                            user_id: session.user.id,
                            artists: artistRequests,
                            filter_electronic: filterElectronic
                        })
                    });

                    if (!response.ok) {
                        const errData = await response.json();
                        throw new Error(errData.detail || "Failed to process CSV");
                    }

                    setStatusText("Success!");
                    setTimeout(() => {
                        setIsUploading(false);
                        setStatusText("");
                        if (onUploadComplete) onUploadComplete();
                    }, 2000);

                } catch (err: any) {
                    console.error("Upload error:", err);
                    setError(err.message || "An unknown error occurred.");
                    setIsUploading(false);
                }
            },
            error: (err) => {
                setError(`Failed to parse CSV: ${err.message}`);
                setIsUploading(false);
            }
        });
    }, [onUploadComplete]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'text/csv': ['.csv']
        },
        maxFiles: 1,
        disabled: isUploading
    });

    return (
        <div className="w-full">
            <div
                {...getRootProps()}
                className={`
                    relative overflow-hidden rounded-2xl border-2 border-dashed p-10 text-center cursor-pointer transition-all duration-300
                    ${isDragActive ? 'border-brand-neon bg-brand-neon/10' : 'border-white/20 hover:border-brand-purple/50 hover:bg-white/5'}
                    ${isUploading ? 'opacity-70 pointer-events-none' : ''}
                `}
            >
                <input {...getInputProps()} />

                {isUploading ? (
                    <div className="flex flex-col items-center space-y-4">
                        <div className="w-12 h-12 border-4 border-brand-purple border-t-brand-neon rounded-full animate-spin" />
                        <p className="text-white font-bold animate-pulse">{statusText}</p>
                    </div>
                ) : (
                    <div className="flex flex-col items-center space-y-4 relative z-10">
                        <div className="p-4 bg-black/50 rounded-full border border-white/10 group-hover:scale-110 transition-transform">
                            <svg className="w-8 h-8 text-brand-purple" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                            </svg>
                        </div>
                        <div>
                            <p className="text-xl font-bold font-heading mb-1">Upload Spotify Data</p>
                            <p className="text-sm text-zinc-400">Drag & drop your CSV file here, or click to select</p>
                        </div>
                    </div>
                )}

                {/* Background glow effects */}
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full bg-gradient-to-br from-brand-purple/10 to-transparent blur-3xl -z-10" />
            </div>

            <div className="mt-4 flex items-center justify-center gap-3">
                <label className="relative inline-flex items-center cursor-pointer">
                    <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={filterElectronic}
                        onChange={() => setFilterElectronic(!filterElectronic)}
                    />
                    <div className="w-11 h-6 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-brand-purple"></div>
                    <span className="ms-3 text-sm font-medium text-zinc-400">Filter Electronic Artists Only</span>
                </label>
            </div>

            {error && (
                <div className="mt-4 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm text-center">
                    {error}
                </div>
            )}
        </div>
    );
}
