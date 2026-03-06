import ForceGraph from '@/components/ForceGraph';
import { Metadata } from 'next';

export const metadata: Metadata = {
    title: 'Sonic Universe | DJWYA',
    description: 'Interactive map of electronic music genres and their relationships.',
};

export default function GenresPage() {
    return (
        <main className="w-full h-screen bg-[#0f0f13] overflow-hidden flex flex-col relative text-white">
            {/* Background ambient light */}
            <div className="absolute top-0 inset-x-0 h-40 bg-gradient-to-b from-purple-900/20 to-transparent pointer-events-none z-0" />

            {/* Header Overlay */}
            <div className="absolute top-0 left-0 right-0 p-6 z-10 pointer-events-none flex justify-between items-start">
                <div>
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-indigo-400 drop-shadow-md pb-1">
                        Sonic Universe
                    </h1>
                    <p className="text-gray-400 text-sm mt-1 max-w-md drop-shadow-md">
                        Interactive map of electronic music genres and their relationships.
                        Drag nodes, scroll to zoom, and hover to reveal parental and influential roots.
                    </p>
                </div>
            </div>

            {/* Graph Container */}
            <div className="flex-1 w-full relative z-0">
                <ForceGraph />
            </div>

            {/* Legend Overlay */}
            <div className="absolute bottom-6 right-6 z-10 pointer-events-none bg-[#0f0f13]/80 backdrop-blur-md p-4 rounded-xl border border-white/10 shadow-xl">
                <h3 className="text-[10px] font-semibold text-gray-400 uppercase tracking-widest mb-3">Edges Legend</h3>
                <div className="flex flex-col gap-3 text-xs mb-3">
                    <div className="flex items-center gap-3">
                        <div className="w-6 h-[2px] bg-indigo-500 shadow-[0_0_8px_rgba(99,102,241,0.8)]" />
                        <span className="text-gray-300 font-medium tracking-wide">Direct Parent</span>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className="w-6 h-[2px] bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]" />
                        <span className="text-gray-300 font-medium tracking-wide">Influence</span>
                    </div>
                </div>

                <h3 className="text-[10px] font-semibold text-gray-400 uppercase tracking-widest mb-3 mt-4">Nodes Legend</h3>
                <div className="flex items-center gap-3 text-xs">
                    <div className="w-3 h-3 bg-purple-500 rounded-full shadow-[0_0_8px_rgba(168,85,247,0.8)]" />
                    <span className="text-gray-300 font-medium tracking-wide">Genre</span>
                </div>
            </div>
        </main>
    );
}
