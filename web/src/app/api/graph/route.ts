import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

export async function GET() {
    try {
        const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
        const supabaseServiceKey = process.env.SUPABASE_SERVICE_KEY!;

        // Use service role key to bypass Row Level Security on read requests
        const supabaseAdmin = createClient(supabaseUrl, supabaseServiceKey);

        // 1. Fetch all genres
        const { data: genres, error: genresError } = await supabaseAdmin
            .from('genres')
            .select('id, name, description, sonic_dna');

        if (genresError) throw genresError;

        // 2. Fetch all edges
        const { data: edges, error: edgesError } = await supabaseAdmin
            .from('genre_edges')
            .select('child_id, parent_id, edge_type, weight');

        if (edgesError) throw edgesError;

        // 3. Format for D3
        // D3 expects nodes: [{id, ...}], links: [{source, target, ...}]
        const nodes = genres.map(g => ({
            id: g.id,
            name: g.name,
            description: g.description,
            sonic_dna: g.sonic_dna
        }));

        const links = edges.map(e => ({
            source: e.child_id,
            target: e.parent_id,
            type: e.edge_type,
            weight: e.weight
        }));

        return NextResponse.json({ nodes, links });

    } catch (error: any) {
        console.error("Error fetching graph data:", error.message);
        return NextResponse.json({ error: 'Failed to fetch graph data' }, { status: 500 });
    }
}
