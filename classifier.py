class GenreClassifier:
    BUCKET_MAP = {
    "house": [
        "house", "deep house", "tech house", "progressive house", "future house", 
        "bass house", "tropical house", "electro house", "acid house", "g-house", 
        "afro house", "organic house", "chicago house", "disco house", "nu-disco", 
        "lo-fi house", "funky house", "hard house", "jazz house", "eurodance", 
        "complextro", "big room", "hardwell style", "rally house"
    ],
    "techno": [
        "techno", "minimal techno", "hard techno", "acid techno", "dub techno", 
        "detroit techno", "peak time techno", "industrial techno", "melodic techno", 
        "dark techno", "hypnotic techno", "tech house", "electro house", 
        "acid house", "tech trance", "electronica"
    ],
    "trance": [
        "trance", "uplifting trance", "psytrance", "progressive trance", "goa trance", 
        "vocal trance", "tech trance", "dream trance", "hard trance", 
        "progressive house", "melodic techno"
    ],
    "dnb": [
        "drum and bass", "liquid dnb", "neurofunk", "jump-up", "jungle", 
        "breakcore", "halftime dnb", "techstep", "darkstep", "atmospheric dnb", 
        "breakbeat"
    ],
    "bass": [
        "dubstep", "riddim", "brostep", "future bass", "trap", "wave", 
        "glitch hop", "color bass", "melodic dubstep", "deathstep", "uk garage", 
        "speed garage", "2-step", "melodic bass", "glitchcore", "bass house", 
        "chillstep", "phonk", "breakbeat", "glitch"
    ],
    "hard_dance": [
        "hardstyle", "euphoric hardstyle", "rawstyle", "gabber", "happy hardcore", 
        "frenchcore", "uptempo hardcore", "hard dance", "hard techno", 
        "hard house", "hard trance"
    ],
    "downtempo_experimental": [
        "downtempo", "idm", "trip-hop", "chillstep", "psydub", "vaporwave", 
        "synthwave", "illbient", "ethereal", "lo-fi house", "liquid dnb", 
        "hyperpop", "electronica", "ambient", "chillout"
    ]
}

    @classmethod
    def classify(cls, raw_genres):
        buckets = set()
        for genre in raw_genres:
            genre_lower = genre.lower()
            for bucket, keywords in cls.BUCKET_MAP.items():
                if any(k in genre_lower for k in keywords):
                    buckets.add(bucket)
        return list(buckets)



class VibeClassifier:
    """
    Maps electronic subgenres to a 6-axis sonic vector (Scores 1-10).
    Axes: [Intensity, Euphoria, Space, Pulse, Chaos, Swing]
    """
    
    # The Master Sonic DNA Dictionary
    SONIC_DNA = {
        # --- PARENT: HOUSE ---
        'house':             {'intensity': 5, 'euphoria': 7, 'space': 5, 'pulse': 10, 'chaos': 3, 'swing': 7},
        'deep house':        {'intensity': 3, 'euphoria': 6, 'space': 8, 'pulse': 10, 'chaos': 2, 'swing': 6},
        'tech house':        {'intensity': 6, 'euphoria': 5, 'space': 5, 'pulse': 10, 'chaos': 3, 'swing': 7},
        'progressive house': {'intensity': 5, 'euphoria': 8, 'space': 7, 'pulse': 10, 'chaos': 3, 'swing': 4},
        'future house':      {'intensity': 6, 'euphoria': 7, 'space': 5, 'pulse': 10, 'chaos': 4, 'swing': 6},
        'bass house':        {'intensity': 8, 'euphoria': 4, 'space': 3, 'pulse': 10, 'chaos': 5, 'swing': 6},
        'tropical house':    {'intensity': 3, 'euphoria': 9, 'space': 6, 'pulse': 7, 'chaos': 2, 'swing': 5},
        'electro house':     {'intensity': 7, 'euphoria': 6, 'space': 4, 'pulse': 10, 'chaos': 5, 'swing': 4},
        'acid house':        {'intensity': 6, 'euphoria': 5, 'space': 5, 'pulse': 8, 'chaos': 6, 'swing': 5},
        'g-house':           {'intensity': 7, 'euphoria': 3, 'space': 4, 'pulse': 8, 'chaos': 3, 'swing': 7},
        'afro house':        {'intensity': 4, 'euphoria': 6, 'space': 6, 'pulse': 7, 'chaos': 3, 'swing': 9},
        'organic house':     {'intensity': 3, 'euphoria': 7, 'space': 7, 'pulse': 6, 'chaos': 2, 'swing': 8},
        'chicago house':     {'intensity': 5, 'euphoria': 7, 'space': 5, 'pulse': 8, 'chaos': 3, 'swing': 8},
        'disco house':       {'intensity': 5, 'euphoria': 9, 'space': 5, 'pulse': 8, 'chaos': 3, 'swing': 8},
        'nu-disco':          {'intensity': 4, 'euphoria': 8, 'space': 5, 'pulse': 7, 'chaos': 3, 'swing': 8},
        'lo-fi house':       {'intensity': 4, 'euphoria': 5, 'space': 8, 'pulse': 7, 'chaos': 3, 'swing': 6},
        'funky house':       {'intensity': 5, 'euphoria': 8, 'space': 4, 'pulse': 8, 'chaos': 3, 'swing': 9},
        'hard house':        {'intensity': 8, 'euphoria': 6, 'space': 3, 'pulse': 9, 'chaos': 4, 'swing': 5},
        'jazz house':        {'intensity': 3, 'euphoria': 7, 'space': 6, 'pulse': 6, 'chaos': 4, 'swing': 9},
        'rally house':       {'intensity': 7, 'euphoria': 6, 'space': 4, 'pulse': 8, 'chaos': 4, 'swing': 6},

        # --- PARENT: TECHNO ---
        'techno':            {'intensity': 7, 'euphoria': 4, 'space': 6, 'pulse': 10, 'chaos': 2, 'swing': 1},
        'minimal techno':    {'intensity': 4, 'euphoria': 3, 'space': 9, 'pulse': 9,  'chaos': 2, 'swing': 2},
        'hard techno':       {'intensity': 9, 'euphoria': 2, 'space': 4, 'pulse': 10, 'chaos': 3, 'swing': 1},
        'acid techno':       {'intensity': 8, 'euphoria': 4, 'space': 5, 'pulse': 10, 'chaos': 5, 'swing': 1},
        'dub techno':        {'intensity': 4, 'euphoria': 4, 'space': 10,'pulse': 8,  'chaos': 2, 'swing': 3},
        'detroit techno':    {'intensity': 6, 'euphoria': 5, 'space': 6, 'pulse': 9,  'chaos': 3, 'swing': 4},
        'peak time techno':  {'intensity': 8, 'euphoria': 5, 'space': 7, 'pulse': 10, 'chaos': 3, 'swing': 1},
        'industrial techno': {'intensity': 9, 'euphoria': 1, 'space': 5, 'pulse': 10, 'chaos': 4, 'swing': 1},
        'melodic techno':    {'intensity': 6, 'euphoria': 8, 'space': 8, 'pulse': 9,  'chaos': 2, 'swing': 1},
        'dark techno':       {'intensity': 8, 'euphoria': 2, 'space': 7, 'pulse': 9,  'chaos': 3, 'swing': 1},
        'hypnotic techno':   {'intensity': 5, 'euphoria': 3, 'space': 9, 'pulse': 10, 'chaos': 2, 'swing': 1},

        # --- PARENT: TRANCE ---
        'trance':            {'intensity': 6, 'euphoria': 8, 'space': 9, 'pulse': 9, 'chaos': 2, 'swing': 1},
        'uplifting trance':  {'intensity': 6, 'euphoria': 10,'space': 9, 'pulse': 9, 'chaos': 2, 'swing': 1},
        'psytrance':         {'intensity': 8, 'euphoria': 5, 'space': 8, 'pulse': 10,'chaos': 6, 'swing': 2},
        'progressive trance':{'intensity': 5, 'euphoria': 7, 'space': 8, 'pulse': 8, 'chaos': 3, 'swing': 2},
        'goa trance':        {'intensity': 7, 'euphoria': 6, 'space': 7, 'pulse': 9, 'chaos': 5, 'swing': 2},
        'vocal trance':      {'intensity': 5, 'euphoria': 9, 'space': 8, 'pulse': 8, 'chaos': 2, 'swing': 1},
        'tech trance':       {'intensity': 7, 'euphoria': 5, 'space': 6, 'pulse': 9, 'chaos': 3, 'swing': 1},
        'dream trance':      {'intensity': 4, 'euphoria': 9, 'space': 10,'pulse': 8, 'chaos': 2, 'swing': 1},
        'hard trance':       {'intensity': 8, 'euphoria': 6, 'space': 6, 'pulse': 10,'chaos': 3, 'swing': 1},

        # --- PARENT: DRUM AND BASS ---
        'drum and bass':     {'intensity': 7, 'euphoria': 5, 'space': 5, 'pulse': 2, 'chaos': 5, 'swing': 7},
        'liquid dnb':        {'intensity': 4, 'euphoria': 9, 'space': 8, 'pulse': 2, 'chaos': 3, 'swing': 8},
        'neurofunk':         {'intensity': 9, 'euphoria': 2, 'space': 4, 'pulse': 2, 'chaos': 7, 'swing': 6},
        'jump-up':           {'intensity': 8, 'euphoria': 4, 'space': 3, 'pulse': 2, 'chaos': 5, 'swing': 8},
        'jungle':            {'intensity': 7, 'euphoria': 6, 'space': 5, 'pulse': 1, 'chaos': 7, 'swing': 9},
        'breakcore':         {'intensity': 9, 'euphoria': 3, 'space': 4, 'pulse': 1, 'chaos': 10,'swing': 5},
        'halftime dnb':      {'intensity': 7, 'euphoria': 4, 'space': 6, 'pulse': 3, 'chaos': 5, 'swing': 7},
        'techstep':          {'intensity': 8, 'euphoria': 2, 'space': 5, 'pulse': 2, 'chaos': 5, 'swing': 6},
        'darkstep':          {'intensity': 9, 'euphoria': 1, 'space': 5, 'pulse': 2, 'chaos': 7, 'swing': 5},
        'atmospheric dnb':   {'intensity': 5, 'euphoria': 7, 'space': 9, 'pulse': 2, 'chaos': 3, 'swing': 7},

        # --- PARENT: BASS MUSIC & DUBSTEP ---
        'dubstep':           {'intensity': 9, 'euphoria': 4, 'space': 5, 'pulse': 2, 'chaos': 6, 'swing': 5},
        'riddim':            {'intensity': 10, 'euphoria': 2, 'space': 2, 'pulse': 3, 'chaos': 5, 'swing': 6},
        'brostep':           {'intensity': 9, 'euphoria': 4, 'space': 4, 'pulse': 2, 'chaos': 8, 'swing': 4},
        'future bass':       {'intensity': 6, 'euphoria': 9, 'space': 8, 'pulse': 4, 'chaos': 5, 'swing': 4},
        'trap':              {'intensity': 8, 'euphoria': 4, 'space': 4, 'pulse': 3, 'chaos': 5, 'swing': 7},
        'wave':              {'intensity': 5, 'euphoria': 6, 'space': 9, 'pulse': 4, 'chaos': 3, 'swing': 4},
        'glitch hop':        {'intensity': 6, 'euphoria': 6, 'space': 4, 'pulse': 3, 'chaos': 8, 'swing': 9},
        'color bass':        {'intensity': 8, 'euphoria': 8, 'space': 6, 'pulse': 3, 'chaos': 7, 'swing': 5},
        'melodic dubstep':   {'intensity': 7, 'euphoria': 9, 'space': 8, 'pulse': 2, 'chaos': 4, 'swing': 4},
        'deathstep':         {'intensity': 10,'euphoria': 1, 'space': 3, 'pulse': 2, 'chaos': 8, 'swing': 3},
        'uk garage':         {'intensity': 4, 'euphoria': 7, 'space': 5, 'pulse': 10, 'chaos': 3, 'swing': 10},
        'speed garage':      {'intensity': 6, 'euphoria': 6, 'space': 4, 'pulse': 8, 'chaos': 3, 'swing': 9},
        '2-step':            {'intensity': 4, 'euphoria': 6, 'space': 5, 'pulse': 2, 'chaos': 4, 'swing': 10},
        'melodic bass':      {'intensity': 6, 'euphoria': 9, 'space': 8, 'pulse': 3, 'chaos': 4, 'swing': 4},
        'glitchcore':        {'intensity': 8, 'euphoria': 7, 'space': 3, 'pulse': 4, 'chaos': 10,'swing': 3},
        'bass':              {'intensity': 7, 'euphoria': 5, 'space': 5, 'pulse': 4, 'chaos': 5, 'swing': 6},
        'glitch':            {'intensity': 7, 'euphoria': 4, 'space': 4, 'pulse': 3, 'chaos': 9, 'swing': 5},

        # --- PARENT: HARD DANCE / HARDCORE ---
        'hardstyle':         {'intensity': 9, 'euphoria': 7, 'space': 5, 'pulse': 9, 'chaos': 4, 'swing': 2},
        'euphoric hardstyle':{'intensity': 8, 'euphoria': 10,'space': 6, 'pulse': 9, 'chaos': 3, 'swing': 2},
        'rawstyle':          {'intensity': 10,'euphoria': 3, 'space': 3, 'pulse': 9, 'chaos': 5, 'swing': 1},
        'gabber':            {'intensity': 10,'euphoria': 2, 'space': 3, 'pulse': 10,'chaos': 4, 'swing': 1},
        'happy hardcore':    {'intensity': 8, 'euphoria': 10,'space': 5, 'pulse': 9, 'chaos': 4, 'swing': 3},
        'frenchcore':        {'intensity': 10,'euphoria': 4, 'space': 3, 'pulse': 10,'chaos': 5, 'swing': 1},
        'uptempo hardcore':  {'intensity': 10,'euphoria': 1, 'space': 2, 'pulse': 10,'chaos': 6, 'swing': 1},
        'hard dance':        {'intensity': 9, 'euphoria': 6, 'space': 4, 'pulse': 9, 'chaos': 4, 'swing': 2},

        # --- PARENT: DOWNTEMPO / EXPERIMENTAL ---
        'downtempo':         {'intensity': 2, 'euphoria': 6, 'space': 10, 'pulse': 4, 'chaos': 2, 'swing': 6},
        'idm':               {'intensity': 4, 'euphoria': 4, 'space': 7, 'pulse': 2, 'chaos': 10,'swing': 4},
        'trip-hop':          {'intensity': 3, 'euphoria': 4, 'space': 7, 'pulse': 4, 'chaos': 3, 'swing': 8},
        'chillstep':         {'intensity': 3, 'euphoria': 7, 'space': 9, 'pulse': 2, 'chaos': 2, 'swing': 4},
        'psydub':            {'intensity': 4, 'euphoria': 6, 'space': 8, 'pulse': 3, 'chaos': 5, 'swing': 6},
        'vaporwave':         {'intensity': 2, 'euphoria': 6, 'space': 9, 'pulse': 5, 'chaos': 2, 'swing': 5},
        'synthwave':         {'intensity': 5, 'euphoria': 7, 'space': 8, 'pulse': 7, 'chaos': 2, 'swing': 3},
        'illbient':          {'intensity': 4, 'euphoria': 2, 'space': 8, 'pulse': 2, 'chaos': 6, 'swing': 3},
        'ethereal':          {'intensity': 1, 'euphoria': 8, 'space': 10,'pulse': 1, 'chaos': 2, 'swing': 2},

        # --- MISC / HYBRID ---
        'hyperpop':          {'intensity': 10, 'euphoria': 10, 'space': 4, 'pulse': 5, 'chaos': 10, 'swing': 4},
        'eurodance':         {'intensity': 6, 'euphoria': 9, 'space': 5, 'pulse': 9, 'chaos': 2, 'swing': 4},
        'complextro':        {'intensity': 10, 'euphoria': 10, 'space': 4, 'pulse': 8, 'chaos': 10, 'swing': 4},
        'big room':          {'intensity': 8, 'euphoria': 6, 'space': 8, 'pulse': 9, 'chaos': 3, 'swing': 2},
        'hardwell style':    {'intensity': 8, 'euphoria': 6, 'space': 8, 'pulse': 9, 'chaos': 3, 'swing': 3},
        'phonk':             {'intensity': 10, 'euphoria': 1, 'space': 5, 'pulse': 4, 'chaos': 5, 'swing': 8},
        'edm':               {'intensity': 7, 'euphoria': 7, 'space': 6, 'pulse': 8, 'chaos': 4, 'swing': 4},
        'electronic':        {'intensity': 5, 'euphoria': 5, 'space': 5, 'pulse': 5, 'chaos': 5, 'swing': 5},
        'breakbeat':         {'intensity': 6, 'euphoria': 5, 'space': 4, 'pulse': 2, 'chaos': 5, 'swing': 9}
    }

    @classmethod
    def get_artist_vibe(cls, genres):
        """
        Takes a list of Last.fm genres for an artist, maps them, 
        and returns the averaged Hexagon coordinates.
        """
        vectors = []
        for g in genres:
            genre_lower = g.lower()
            if genre_lower in cls.SONIC_DNA:
                vectors.append(cls.SONIC_DNA[genre_lower])
        
        # If no genres map, return a dead-center generic score
        if not vectors:
            return {'intensity': 5, 'euphoria': 5, 'space': 5, 'pulse': 5, 'chaos': 5, 'swing': 5}
            
        # Average the scores
        avg_vibe = {
            'intensity': sum(v['intensity'] for v in vectors) / len(vectors),
            'euphoria':  sum(v['euphoria'] for v in vectors) / len(vectors),
            'space':     sum(v['space'] for v in vectors) / len(vectors),
            'pulse':     sum(v['pulse'] for v in vectors) / len(vectors),
            'chaos':     sum(v['chaos'] for v in vectors) / len(vectors),
            'swing':     sum(v['swing'] for v in vectors) / len(vectors)
        }
        
        # Round to 1 decimal place for clean data
        return {k: round(v, 1) for k, v in avg_vibe.items()}