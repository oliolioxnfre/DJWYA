import os
from dotenv import load_dotenv
from supabase import create_client, Client

import threading

class GenreManager:
    _instance = None
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                print("🧬 Initializing GenreManager Singleton...")
                cls._instance = cls()
        return cls._instance
        
    def __init__(self):
        load_dotenv()
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        supabase: Client = create_client(url, key)
        
        # Load all genres into memory
        res = supabase.table("genres").select("id, slug, aliases, sonic_dna, non-electronic").execute()
        self.slug_to_dna = {}
        self.slug_to_electronic = {}
        self.alias_to_slug = {}
        self.slug_to_id = {}
        
        for row in res.data:
            slug = row.get("slug")
            if not slug: continue
            
            self.slug_to_id[slug] = row.get("id")
            
            dna = row.get("sonic_dna")
            # Only count as 'proper' DNA if it is a dict and has our 7 axes
            if dna and isinstance(dna, dict):
                # We define categories here to avoid circular dependencies with VibeClassifier
                cats = ['intensity', 'euphoria', 'space', 'pulse', 'chaos', 'swing', 'bass']
                if any(cat in dna for cat in cats):
                    self.slug_to_dna[slug] = dna
                
            # A genre is electronic if "non-electronic" is NOT True
            self.slug_to_electronic[slug] = not row.get("non-electronic", False)
            
            # Map identity
            self.alias_to_slug[slug] = slug
            aliases = row.get("aliases") or []
            for alias in aliases:
                self.alias_to_slug[alias.lower().strip()] = slug
                
    def get_canonical_slug(self, raw_genre):
        """Funnel alias or raw string into canonical slug."""
        cleaned = raw_genre.lower().strip()
        mapped = self.alias_to_slug.get(cleaned, cleaned)
        mapped = mapped.replace(" ", "-")
        return self.alias_to_slug.get(mapped, mapped)
        
    def get_canonical_id(self, raw_genre):
        slug = self.get_canonical_slug(raw_genre)
        return self.slug_to_id.get(slug)
        
    def is_electronic(self, raw_genre):
        slug = self.get_canonical_slug(raw_genre)
        # If it's in the explicit map, use its electronic flag
        if slug in self.slug_to_electronic:
            return self.slug_to_electronic[slug]
        return False

class VibeClassifier:
    """
    Maps electronic subgenres to a 7-axis sonic vector (Scores 1-10).
    Axes: [Intensity, Euphoria, Space, Pulse, Chaos, Swing, Bass]
    """
    
    CATEGORIES = ['intensity', 'euphoria', 'space', 'pulse', 'chaos', 'swing', 'bass']

    @classmethod
    def get_artist_vibe(cls, genres):
        """
        Takes a list of Last.fm genres for an artist, maps them through the database, 
        and returns the averaged Hexagon coordinates, weighted by relevance.
        """
        manager = GenreManager.get_instance()
        
        active_slugs = []
        for g in genres:
            slug = manager.get_canonical_slug(g)
            # Only use genres that actually have a sonic_dna mapped in the DB
            # and verify it is a valid dictionary
            if slug in manager.slug_to_dna and slug not in active_slugs:
                active_slugs.append(slug)
        
        if not active_slugs:
            return None
            
        vectors = [manager.slug_to_dna[slug] for slug in active_slugs]
        
        # Calculate weights based on order (first match gets more weight)
        weights = [1.0 / (i + 1) for i in range(len(vectors))]
        total_weight = sum(weights)
        
        if total_weight == 0:
            return None
        
        avg_vibe = {}
        for category in cls.CATEGORIES:
            # Defensive check: ensure v is a dict and has the category
            weighted_sum = sum(
                (v.get(category, 0.0) if isinstance(v, dict) else 0.0) * w 
                for v, w in zip(vectors, weights)
            )
            avg_vibe[category] = weighted_sum / total_weight
        
        return {k: round(v, 2) for k, v in avg_vibe.items()}

    @classmethod
    def update_user_dna(cls, user_id):
        load_dotenv()
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        supabase: Client = create_client(url, key)
        print(f"Fetching sonic DNA and play counts for {user_id}...")
        
        response = supabase.table("user_lib").select("count, artists(name, sonic_dna, artist_genres(genres(slug)))").eq("user_id", user_id).execute()
        artist_data_list = []
        full_artist_info_list = [] # For subgenre extraction
        
        for row in response.data:
            play_count = row.get("count", 1)
            artist_info = row.get('artists')
            if not artist_info:
                continue
                
            dna = artist_info.get("sonic_dna")
            name = artist_info.get("name", "Unknown Artist")
            
            # Extract genres from junction table format
            genres = []
            ag_list = artist_info.get("artist_genres") or []
            for ag in ag_list:
                g = ag.get("genres")
                if g and g.get("slug"):
                    genres.append(g["slug"])
            
            full_artist_info_list.append({
                'name': name,
                'genres': genres,
                'count': play_count
            })
            
            if dna and isinstance(dna, dict):
                if all(cat in dna for cat in cls.CATEGORIES):
                    artist_data_list.append({
                        'name': name,
                        'dna': dna,
                        'count': play_count
                    })
        
        user_dna = cls.calculate_user_dna(artist_data_list)
        user_subgenres = cls.extract_top_subgenres(full_artist_info_list)
        
        print(f"📡 Syncing {len(user_subgenres)} subgenres to user profile...")
        try:
            supabase.table("users").update({
                "sonic_dna": user_dna,
                "subgenres": user_subgenres
            }).eq("id", user_id).execute()
        except Exception as e:
            print(f"❌ Error updating user DNA in database: {e}")
            raise e
        
        print(f"✅ Successfully updated DNA for {user_id}.")
        return artist_data_list

    @classmethod
    def recalculate_all_artist_dna(cls):
        load_dotenv()
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        supabase: Client = create_client(url, key)
        
        print("🔄 Fetching all artists from database...")
        response = supabase.table("artists").select("id, name, name_slug, artist_genres(genres(slug))").execute()
        artists = response.data
        
        if not artists:
            print("❌ No artists found in database.")
            return

        print(f"🧪 Recalculating DNA for {len(artists)} artists using database mappings...")
        updates = []
        
        for artist in artists:
            ag_list = artist.get("artist_genres") or []
            genres = []
            for ag in ag_list:
                g = ag.get("genres")
                if g and g.get("slug"):
                    genres.append(g["slug"])
                    
            if not genres:
                continue
                
            new_dna = cls.get_artist_vibe(genres)
            if new_dna:
                updates.append({
                    "id": artist['id'], 
                    "name": artist['name'],
                    "name_slug": artist['name_slug'],
                    "sonic_dna": new_dna
                })
        
        if updates:
            print(f"🚀 Syncing {len(updates)} updates to Supabase in batches...")
            for i in range(0, len(updates), 500):
                batch = updates[i:i+500]
                supabase.table("artists").upsert(batch).execute()
        
        print(f"✅ Successfully updated DNA for {len(updates)} artists.")
        return len(updates)

    @classmethod
    def calculate_dna(cls, artist_data_list):
        if not artist_data_list:
            return {cat: 0.0 for cat in cls.CATEGORIES}
            
        total_plays = sum(item.get('count', 1) for item in artist_data_list)
        if total_plays == 0:
            return {cat: 0.0 for cat in cls.CATEGORIES}
            
        final_dna = {cat: 0.0 for cat in cls.CATEGORIES}
        for item in artist_data_list:
            dna = item['dna']
            count = item.get('count', 1)
            weight = count / total_plays
            for cat in cls.CATEGORIES:
                final_dna[cat] += dna.get(cat, 0.0) * weight
                
        return {cat: round(val, 2) for cat, val in final_dna.items()}

    @classmethod
    def calculate_user_dna(cls, artist_data_list):
        return cls.calculate_dna(artist_data_list)

    @classmethod
    def extract_top_subgenres(cls, artist_info_list):
        """
        Aggregates subgenres from artist info (name, genres, count).
        Weights subgenres based on artist frequency.
        Returns a normalized dict of subgenres.
        """
        manager = GenreManager.get_instance()
        subgenre_weights = {}
        
        for artist in artist_info_list:
            genres = artist.get('genres', [])
            count = artist.get('count', 1)
            
            mapped_subgenres = []
            for g in genres:
                slug = manager.get_canonical_slug(g)
                # Include all electronic subgenres in the distribution, 
                # even if we don't have DNA coordinates for them yet.
                if manager.is_electronic(slug) and slug not in mapped_subgenres:
                    mapped_subgenres.append(slug)
            
            if not mapped_subgenres:
                continue
                
            weights = [1.0 / (i + 1) for i in range(len(mapped_subgenres))]
            total_artist_weight = sum(weights)
            
            for sub, w in zip(mapped_subgenres, weights):
                contribution = (w / total_artist_weight) * count
                subgenre_weights[sub] = subgenre_weights.get(sub, 0.0) + contribution
        
        if not subgenre_weights:
            return {}
            
        sorted_subgenres = sorted(subgenre_weights.items(), key=lambda x: x[1], reverse=True)
        top_subgenres = sorted_subgenres
        
        if not top_subgenres:
            return {}
            
        max_weight = top_subgenres[0][1]
        normalized_vector = {sub: round(w / max_weight, 3) for sub, w in top_subgenres}
        
        return normalized_vector