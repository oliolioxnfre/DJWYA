import ForceGraph from '@/components/ForceGraph';
import { Metadata } from 'next';
import Header from '@/components/dashboard/Header';

export const metadata: Metadata = {
    title: 'Sonic Universe | DJWYA',
    description: 'Interactive map of electronic music genres and their relationships.',
};

export default function GenresPage() {
    return (
        <main className="w-full h-screen bg-[#0f0f13] overflow-hidden flex flex-col relative text-white">
            {/* Background ambient light */}
            <div className="absolute top-0 inset-x-0 h-40 bg-gradient-to-b from-purple-900/20 to-transparent pointer-events-none z-0" />

            <Header />

            {/* Graph Container */}
            <div className="flex-1 w-full relative z-0">
                <ForceGraph />
            </div>
        </main>
    );
}
