import os
from dotenv import load_dotenv
from supabase import create_client, Client

#"complextro"

class GenreClassifier:
    BUCKET_MAP = {
    "house": [
        "house", "deep-house", "tech-house", "progressive-house", "future-house", 
        "bass-house", "tropical-house", "electro-house", "acid-house", "g-house", 
        "afro-house", "organic-house", "chicago-house", "disco-house", "nu-disco", 
        "lo-fi-house", "funky-house", "hard-house", "jazz-house", "eurodance", 
        "complextro", "big-room", "hardwell-style", "rally-house", "melodic-house",
        "speed-house", "ghetto-house"
    ],
    "techno": [
        "techno", "minimal-techno", "hard-techno", "acid-techno", "dub-techno", 
        "detroit-techno", "peak-time-techno", "industrial-techno", "melodic-techno", 
        "dark-techno", "hypnotic-techno", "tech-house", "electro-house", 
        "acid-house", "tech-trance", "electronica", "cyber-house"
    ],
    "trance": [
        "trance", "uplifting-trance", "psytrance", "progressive-trance", "goa-trance", 
        "vocal-trance", "tech-trance", "dream-trance", "hard-trance", 
        "progressive-house", "melodic-techno", "acid-trance", "hard-trance"
    ],
    "dnb": [
        "drum-and-bass", "liquid-dnb", "neurofunk", "jump-up", "jungle", 
        "breakcore", "halftime-dnb", "techstep", "darkstep", "atmospheric-dnb", 
        "breakbeat", "atmospheric-jungle"
    ],
    "bass": [
        "dubstep", "riddim", "brostep", "future-bass", "trap", "wave", 
        "glitch-hop", "color-bass", "melodic-dubstep", "deathstep", "uk-garage", 
        "speed-garage", "2-step", "melodic-bass", "glitchcore", "bass-house", 
        "chillstep", "phonk", "breakbeat", "glitch", "moombahton", "midtempo-bass",
        "hardwave", "drift-phonk", "juke", "footwork"
    ],
    "hard_dance": [
        "hardstyle", "euphoric-hardstyle", "rawstyle", "gabber", "happy-hardcore", 
        "frenchcore", "uptempo-hardcore", "hard-dance", "hard-techno", 
        "hard-house", "hard-trance", "hard-bass", "donk", "bounce", "scouse-house",
        "nightcore"
    ],
    "downtempo_experimental": [
        "downtempo", "idm", "trip-hop", "chillstep", "psydub", "vaporwave", 
        "synthwave", "illbient", "ethereal", "lo-fi-house", "liquid-dnb", 
        "hyperpop", "electronica", "ambient", "chillout", "dream-pop", "outrun",
        "retrowave", "chillsynth", "musique-concrete", "deconstructed-club"
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
    Maps electronic subgenres to a 7-axis sonic vector (Scores 1-10).
    Axes: [Intensity, Euphoria, Space, Pulse, Chaos, Swing, Bass]
    """
    
    CATEGORIES = ['intensity', 'euphoria', 'space', 'pulse', 'chaos', 'swing', 'bass']
    
    # The Master Sonic DNA Dictionary
    SONIC_DNA = {
        # --- PARENT: HOUSE (Pulse heavy, moderate swing, low/mid bass) ---
        'house':             {'intensity': 4, 'euphoria': 8, 'space': 4, 'pulse': 8.5, 'chaos': 0, 'swing': 6, 'bass': 3},
        'deep-house':        {'intensity': 1.5, 'euphoria': 9, 'space': 9, 'pulse': 8, 'chaos': 0.5, 'swing': 6, 'bass': 4},
        'tech-house':        {'intensity': 7, 'euphoria': 3, 'space': 2.5, 'pulse': 9, 'chaos': 3, 'swing': 6.5, 'bass': 4.5},
        'progressive-house': {'intensity': 4.5, 'euphoria': 9.5, 'space': 9, 'pulse': 8.5, 'chaos': 1.5, 'swing': 5, 'bass': 3},
        'future-house':      {'intensity': 8, 'euphoria': 8.5, 'space': 3, 'pulse': 9, 'chaos': 4, 'swing': 6, 'bass': 5.5},
        'bass-house':        {'intensity': 9, 'euphoria': 2, 'space': 1.5, 'pulse': 9.5, 'chaos': 8, 'swing': 5.5, 'bass': 6.5},
        'tropical-house':    {'intensity': 1, 'euphoria': 9.5, 'space': 8, 'pulse': 8, 'chaos': 0.5, 'swing': 6.5, 'bass': 2},
        'electro-house':     {'intensity': 9.5, 'euphoria': 6.5, 'space': 2, 'pulse': 9.5, 'chaos': 7, 'swing': 5, 'bass': 5.5},
        'acid-house':        {'intensity': 8, 'euphoria': 4, 'space': 6, 'pulse': 9, 'chaos': 9, 'swing': 6, 'bass': 4},
        'g-house':           {'intensity': 8.5, 'euphoria': 1.5, 'space': 2, 'pulse': 9, 'chaos': 3, 'swing': 7, 'bass': 5.5},
        'afro-house':        {'intensity': 3, 'euphoria': 7, 'space': 8, 'pulse': 8.5, 'chaos': 2, 'swing': 8, 'bass': 3.5},
        'organic-house':     {'intensity': 1, 'euphoria': 8, 'space': 9.5, 'pulse': 8, 'chaos': 1, 'swing': 6.5, 'bass': 2.5},
        'chicago-house':     {'intensity': 4, 'euphoria': 8, 'space': 4, 'pulse': 9, 'chaos': 3, 'swing': 7, 'bass': 3.5},
        'disco-house':       {'intensity': 4, 'euphoria': 9.5, 'space': 4, 'pulse': 8.5, 'chaos': 1.5, 'swing': 7.5, 'bass': 3},
        'nu-disco':          {'intensity': 3, 'euphoria': 9, 'space': 5, 'pulse': 8.5, 'chaos': 2.5, 'swing': 8, 'bass': 3.5},
        'lo-fi-house':       {'intensity': 2, 'euphoria': 4, 'space': 9.5, 'pulse': 8, 'chaos': 6, 'swing': 7, 'bass': 3},
        'funky-house':       {'intensity': 3.5, 'euphoria': 9, 'space': 3.5, 'pulse': 8.5, 'chaos': 2, 'swing': 8.5, 'bass': 4},
        'hard-house':        {'intensity': 9.5, 'euphoria': 4, 'space': 0.5, 'pulse': 10, 'chaos': 7, 'swing': 4, 'bass': 5},
        'jazz-house':        {'intensity': 2.5, 'euphoria': 8.5, 'space': 8, 'pulse': 8, 'chaos': 5, 'swing': 9, 'bass': 3},
        'rally-house':       {'intensity': 8, 'euphoria': 5, 'space': 3, 'pulse': 9, 'chaos': 6, 'swing': 8, 'bass': 5},
        'witch-house':       {'intensity': 8, 'euphoria': 2, 'space': 9.5, 'pulse': 5, 'chaos': 7, 'swing': 7, 'bass': 6.5},
        'melodic-house':     {'intensity': 3, 'euphoria': 9.5, 'space': 9.5, 'pulse': 8.5, 'chaos': 1, 'swing': 5, 'bass': 3},
        'speed-house':       {'intensity': 9.5, 'euphoria': 6, 'space': 2.5, 'pulse': 10, 'chaos': 8, 'swing': 6, 'bass': 5.5},
        'ghetto-house':      {'intensity': 9, 'euphoria': 1, 'space': 1.5, 'pulse': 9.5, 'chaos': 8, 'swing': 8, 'bass': 5.5},

        # --- PARENT: TECHNO (High pulse, zero swing, clinical bass) ---
        'techno':            {'intensity': 8.5, 'euphoria': 0.5, 'space': 5, 'pulse': 9.5, 'chaos': 0, 'swing': 0, 'bass': 4.5},
        'minimal-techno':    {'intensity': 2.5, 'euphoria': 1.5, 'space': 9.5, 'pulse': 9, 'chaos': 0.5, 'swing': 0, 'bass': 2.5},
        'hard-techno':       {'intensity': 10, 'euphoria': 0, 'space': 2.5, 'pulse': 10, 'chaos': 4, 'swing': 0, 'bass': 6},
        'acid-techno':       {'intensity': 9.5, 'euphoria': 1.5, 'space': 4, 'pulse': 9.5, 'chaos': 9.5, 'swing': 0.5, 'bass': 5},
        'dub-techno':        {'intensity': 3, 'euphoria': 2.5, 'space': 10, 'pulse': 8, 'chaos': 1, 'swing': 2, 'bass': 5.5},
        'detroit-techno':    {'intensity': 6.5, 'euphoria': 4, 'space': 6, 'pulse': 9, 'chaos': 4, 'swing': 3, 'bass': 4},
        'peak-time-techno':  {'intensity': 10, 'euphoria': 4, 'space': 4, 'pulse': 10, 'chaos': 1.5, 'swing': 0, 'bass': 5.5},
        'industrial-techno': {'intensity': 10, 'euphoria': 0, 'space': 3.5, 'pulse': 10, 'chaos': 7, 'swing': 0, 'bass': 6.5},
        'melodic-techno':    {'intensity': 4, 'euphoria': 9, 'space': 9.5, 'pulse': 9, 'chaos': 0.5, 'swing': 0.5, 'bass': 3.5},
        'dark-techno':       {'intensity': 9.5, 'euphoria': 0, 'space': 8, 'pulse': 9.5, 'chaos': 4, 'swing': 0, 'bass': 5},
        'hypnotic-techno':   {'intensity': 3, 'euphoria': 1.5, 'space': 9.5, 'pulse': 9, 'chaos': 0, 'swing': 0, 'bass': 3.5},
        'cyber-house':       {'intensity': 8.5, 'euphoria': 6.5, 'space': 9, 'pulse': 9, 'chaos': 6, 'swing': 1.5, 'bass': 5},

        # --- PARENT: TRANCE (High euphoria, high space, high pulse) ---
        'trance':            {'intensity': 7, 'euphoria': 9.5, 'space': 9.5, 'pulse': 9, 'chaos': 0.5, 'swing': 0, 'bass': 3},
        'uplifting-trance':  {'intensity': 8, 'euphoria': 10, 'space': 10, 'pulse': 9, 'chaos': 1, 'swing': 0, 'bass': 2.5},
        'psytrance':         {'intensity': 9.5, 'euphoria': 4, 'space': 8.5, 'pulse': 9.5, 'chaos': 9, 'swing': 1, 'bass': 5},
        'progressive-trance':{'intensity': 5, 'euphoria': 9, 'space': 9, 'pulse': 8.5, 'chaos': 1.5, 'swing': 1, 'bass': 3},
        'goa-trance':        {'intensity': 9, 'euphoria': 7.5, 'space': 9, 'pulse': 9.5, 'chaos': 9.5, 'swing': 1.5, 'bass': 4.5},
        'vocal-trance':      {'intensity': 4.5, 'euphoria': 10, 'space': 9.5, 'pulse': 8.5, 'chaos': 0.5, 'swing': 0, 'bass': 2},
        'tech-trance':       {'intensity': 9, 'euphoria': 3, 'space': 5, 'pulse': 9.5, 'chaos': 6, 'swing': 0.5, 'bass': 4.5},
        'dream-trance':      {'intensity': 2, 'euphoria': 10, 'space': 10, 'pulse': 7.5, 'chaos': 0.5, 'swing': 0.5, 'bass': 1.5},
        'hard-trance':       {'intensity': 9.5, 'euphoria': 7.5, 'space': 5, 'pulse': 10, 'chaos': 5, 'swing': 0.5, 'bass': 5},
        'acid-trance':       {'intensity': 9, 'euphoria': 5.5, 'space': 7.5, 'pulse': 9.5, 'chaos': 9.5, 'swing': 1.5, 'bass': 4.5},

        # --- PARENT: DRUM AND BASS (Low pulse, high swing, mid-high bass) ---
        'drum-and-bass':     {'intensity': 9, 'euphoria': 4.5, 'space': 3.5, 'pulse': 1, 'chaos': 7, 'swing': 8.5, 'bass': 7.5},
        'liquid-dnb':        {'intensity': 3, 'euphoria': 9.5, 'space': 9.5, 'pulse': 1, 'chaos': 1.5, 'swing': 9, 'bass': 6.5},
        'neurofunk':         {'intensity': 10, 'euphoria': 1, 'space': 4, 'pulse': 1.5, 'chaos': 9, 'swing': 7.5, 'bass': 9},
        'jump-up':           {'intensity': 9.5, 'euphoria': 5, 'space': 1.5, 'pulse': 1.5, 'chaos': 8.5, 'swing': 8.5, 'bass': 8.5},
        'jungle':            {'intensity': 8.5, 'euphoria': 6, 'space': 6, 'pulse': 0.5, 'chaos': 9, 'swing': 9.5, 'bass': 7.5},
        'breakcore':         {'intensity': 10, 'euphoria': 2, 'space': 3, 'pulse': 0, 'chaos': 10, 'swing': 6, 'bass': 6},
        'halftime-dnb':      {'intensity': 8.5, 'euphoria': 3.5, 'space': 7.5, 'pulse': 1, 'chaos': 6, 'swing': 9, 'bass': 8.5},
        'techstep':          {'intensity': 9.5, 'euphoria': 0, 'space': 3.5, 'pulse': 1.5, 'chaos': 8, 'swing': 7, 'bass': 8},
        'darkstep':          {'intensity': 10, 'euphoria': 0, 'space': 4, 'pulse': 1, 'chaos': 9.5, 'swing': 6.5, 'bass': 8.5},
        'atmospheric-dnb':   {'intensity': 3.5, 'euphoria': 9, 'space': 9.5, 'pulse': 1, 'chaos': 2.5, 'swing': 8, 'bass': 6},
        'atmospheric-jungle':{'intensity': 4.5, 'euphoria': 8.5, 'space': 9.5, 'pulse': 0.5, 'chaos': 7, 'swing': 9, 'bass': 6.5},

        # --- PARENT: BASS MUSIC & DUBSTEP (The Baseline is 7 for Bass) ---
        'dubstep':           {'intensity': 9.5, 'euphoria': 8, 'space': 4.5, 'pulse': 1, 'chaos': 8.5, 'swing': 5.5, 'bass': 7},
        'riddim':            {'intensity': 10, 'euphoria': 1, 'space': 1, 'pulse': 1.5, 'chaos': 7.5, 'swing': 7.5, 'bass': 9.5},
        'brostep':           {'intensity': 9, 'euphoria': 4, 'space': 2, 'pulse': 1.5, 'chaos': 9.5, 'swing': 4, 'bass': 7.5},
        'future-bass':       {'intensity': 6.5, 'euphoria': 9.5, 'space': 8.5, 'pulse': 3.5, 'chaos': 6, 'swing': 8.5, 'bass': 6},
        'wave':              {'intensity': 3.5, 'euphoria': 8, 'space': 9.5, 'pulse': 4, 'chaos': 4, 'swing': 4, 'bass': 6.5},
        'glitch-hop':        {'intensity': 7.5, 'euphoria': 8, 'space': 5.5, 'pulse': 2.5, 'chaos': 9, 'swing': 9.5, 'bass': 5.5},
        'color-bass':        {'intensity': 9, 'euphoria': 9.5, 'space': 7.5, 'pulse': 1.5, 'chaos': 8.5, 'swing': 5.5, 'bass': 6},
        'colour-bass':       {'intensity': 9, 'euphoria': 9.5, 'space': 7.5, 'pulse': 1.5, 'chaos': 8.5, 'swing': 5.5, 'bass': 6},
        'melodic-dubstep':   {'intensity': 8, 'euphoria': 10, 'space': 9, 'pulse': 1, 'chaos': 3.5, 'swing': 3.5, 'bass': 6.5},
        'deathstep':         {'intensity': 10, 'euphoria': 0, 'space': 1.5, 'pulse': 1, 'chaos': 10, 'swing': 2, 'bass': 9.5},
        'uk-garage':         {'intensity': 6, 'euphoria': 6, 'space': 6, 'pulse': 6, 'chaos': 4.5, 'swing': 9.5, 'bass': 6.5},
        'speed-garage':      {'intensity': 8, 'euphoria': 5, 'space': 3.5, 'pulse': 8.5, 'chaos': 6, 'swing': 9, 'bass': 7.5},
        '2-step':            {'intensity': 3.5, 'euphoria': 6.5, 'space': 5, 'pulse': 4, 'chaos': 5, 'swing': 9.5, 'bass': 6.5},
        'melodic-bass':      {'intensity': 7, 'euphoria': 9.5, 'space': 9, 'pulse': 2, 'chaos': 5, 'swing': 4.5, 'bass': 6.5},
        'glitchcore':        {'intensity': 10, 'euphoria': 9, 'space': 2.5, 'pulse': 4, 'chaos': 10, 'swing': 5, 'bass': 6.5},
        'bass':              {'intensity': 8.5, 'euphoria': 4.5, 'space': 4.5, 'pulse': 4.5, 'chaos': 7, 'swing': 7.5, 'bass': 7.5},
        'glitch':            {'intensity': 8, 'euphoria': 7, 'space': 6.5, 'pulse': 2.5, 'chaos': 9.5, 'swing': 6, 'bass': 5},
        'moombahton':        {'intensity': 7.5, 'euphoria': 7.5, 'space': 3.5, 'pulse': 7, 'chaos': 5.5, 'swing': 9.5, 'bass': 6.5},
        'midtempo-bass':     {'intensity': 9.5, 'euphoria': 3.5, 'space': 8, 'pulse': 6, 'chaos': 8, 'swing': 5, 'bass': 8},
        'hardwave':          {'intensity': 8, 'euphoria': 8, 'space': 9.5, 'pulse': 5, 'chaos': 7, 'swing': 4, 'bass': 7},
        'drift-phonk':       {'intensity': 9.5, 'euphoria': 1.5, 'space': 3.5, 'pulse': 5.5, 'chaos': 8.5, 'swing': 8.5, 'bass': 8},
        'juke':              {'intensity': 9, 'euphoria': 2.5, 'space': 2.5, 'pulse': 1, 'chaos': 9.5, 'swing': 9.5, 'bass': 6.5},
        'footwork':          {'intensity': 9.5, 'euphoria': 2.5, 'space': 3.5, 'pulse': 1, 'chaos': 10, 'swing': 10, 'bass': 6.5},
        'grime':             {'intensity': 8.5, 'euphoria': 1.5, 'space': 3.5, 'pulse': 2, 'chaos': 7.5, 'swing': 8.5, 'bass': 8},
        'dub':               {'intensity': 2, 'euphoria': 6, 'space': 9.5, 'pulse': 4, 'chaos': 4, 'swing': 8, 'bass': 8.5},

        # --- PARENT: HARD DANCE / HARDCORE ---
        'hardstyle':         {'intensity': 9.5, 'euphoria': 7.5, 'space': 3.5, 'pulse': 9.5, 'chaos': 5.5, 'swing': 0, 'bass': 6.5},
        'euphoric-hardstyle':{'intensity': 9, 'euphoria': 9.5, 'space': 5.5, 'pulse': 9.5, 'chaos': 4.5, 'swing': 1.5, 'bass': 5.5},
        'rawstyle':          {'intensity': 10, 'euphoria': 1.5, 'space': 1.5, 'pulse': 9.5, 'chaos': 8, 'swing': 0, 'bass': 8},
        'gabber':            {'intensity': 10, 'euphoria': 0, 'space': 1.5, 'pulse': 10, 'chaos': 9, 'swing': 0, 'bass': 7.5},
        'happy-hardcore':    {'intensity': 9, 'euphoria': 9.5, 'space': 5, 'pulse': 9.5, 'chaos': 7, 'swing': 3.5, 'bass': 4.5},
        'frenchcore':        {'intensity': 10, 'euphoria': 2.5, 'space': 1.5, 'pulse': 10, 'chaos': 9.5, 'swing': 0, 'bass': 7.5},
        'uptempo-hardcore':  {'intensity': 10, 'euphoria': 0, 'space': 0, 'pulse': 10, 'chaos': 10, 'swing': 0, 'bass': 7},
        'hard-dance':        {'intensity': 9.5, 'euphoria': 6.5, 'space': 3.5, 'pulse': 9.5, 'chaos': 7, 'swing': 1.5, 'bass': 6},
        'hard-bass':         {'intensity': 9.5, 'euphoria': 3.5, 'space': 0.5, 'pulse': 9.5, 'chaos': 6, 'swing': 7.5, 'bass': 8},
        'donk':              {'intensity': 9.5, 'euphoria': 8, 'space': 0.5, 'pulse': 9.5, 'chaos': 8.5, 'swing': 8.5, 'bass': 6.5},
        'bounce':            {'intensity': 8.5, 'euphoria': 9, 'space': 1.5, 'pulse': 9, 'chaos': 5.5, 'swing': 8.5, 'bass': 5.5},
        'scouse-house':      {'intensity': 8.5, 'euphoria': 9, 'space': 1.5, 'pulse': 9, 'chaos': 6.5, 'swing': 8.5, 'bass': 5.5},
        'nightcore':         {'intensity': 9.5, 'euphoria': 9, 'space': 3, 'pulse': 8.5, 'chaos': 8, 'swing': 5.5, 'bass': 2.5},

        # --- PARENT: DOWNTEMPO / EXPERIMENTAL ---
        'downtempo':         {'intensity': 0.5, 'euphoria': 6.5, 'space': 9.5, 'pulse': 3.5, 'chaos': 0.5, 'swing': 7, 'bass': 3.5},
        'idm':               {'intensity': 1, 'euphoria': 3.5, 'space': 8.5, 'pulse': 0.5, 'chaos': 9.5, 'swing': 7, 'bass': 3},
        'trip-hop':          {'intensity': 1, 'euphoria': 4.5, 'space': 8, 'pulse': 3.5, 'chaos': 4.5, 'swing': 9, 'bass': 5},
        'chillstep':         {'intensity': 0.5, 'euphoria': 8.5, 'space': 9.5, 'pulse': 2.5, 'chaos': 1.5, 'swing': 5, 'bass': 4.5},
        'psydub':            {'intensity': 1, 'euphoria': 8, 'space': 9.5, 'pulse': 3.5, 'chaos': 7.5, 'swing': 7, 'bass': 7},
        'vaporwave':         {'intensity': 1.5, 'euphoria': 8, 'space': 9.5, 'pulse': 2.5, 'chaos': 4, 'swing': 4.5, 'bass': 2},
        'synthwave':         {'intensity': 2.5, 'euphoria': 8, 'space': 9, 'pulse': 8, 'chaos': 1.5, 'swing': 3.5, 'bass': 4},
        'illbient':          {'intensity': 0.5, 'euphoria': 0.5, 'space': 9.5, 'pulse': 2, 'chaos': 8.5, 'swing': 3.5, 'bass': 4.5},
        'ethereal':          {'intensity': 0, 'euphoria': 9.5, 'space': 10, 'pulse': 0.5, 'chaos': 0.5, 'swing': 1.5, 'bass': 1},
        'ambient':           {'intensity': 0, 'euphoria': 5, 'space': 10, 'pulse': 0, 'chaos': 0, 'swing': 0, 'bass': 0.5},
        'dream-pop':         {'intensity': 1.5, 'euphoria': 9, 'space': 9.5, 'pulse': 1.5, 'chaos': 0.5, 'swing': 3.5, 'bass': 2},
        'outrun':            {'intensity': 3.5, 'euphoria': 8, 'space': 8.5, 'pulse': 8.5, 'chaos': 1.5, 'swing': 2.5, 'bass': 4.5},
        'retrowave':         {'intensity': 2, 'euphoria': 8, 'space': 9, 'pulse': 8, 'chaos': 1.5, 'swing': 2.5, 'bass': 4},
        'chillsynth':        {'intensity': 0.5, 'euphoria': 7.5, 'space': 9.5, 'pulse': 5, 'chaos': 1.5, 'swing': 3.5, 'bass': 2},
        'musique-concrete':  {'intensity': 1.5, 'euphoria': 0, 'space': 9.5, 'pulse': 0, 'chaos': 9.5, 'swing': 2.5, 'bass': 1.5},
        'deconstructed-club':{'intensity': 9, 'euphoria': 0.5, 'space': 8, 'pulse': 2.5, 'chaos': 9.5, 'swing': 4.5, 'bass': 6.5},

        # --- MISC / HYBRID ---
        'hyperpop':          {'intensity': 9.5, 'euphoria': 8.5, 'space': 5.5, 'pulse': 5.5, 'chaos': 9.5, 'swing': 7, 'bass': 4.5},
        'eurodance':         {'intensity': 7.5, 'euphoria': 9.5, 'space': 3.5, 'pulse': 9, 'chaos': 2.5, 'swing': 6, 'bass': 4},
        'complextro':        {'intensity': 9.5, 'euphoria': 9, 'space': 4.5, 'pulse': 9, 'chaos': 9.5, 'swing': 6.5, 'bass': 5.5},
        'big-room':          {'intensity': 6.5, 'euphoria': 7.5, 'space': 5.5, 'pulse': 9.5, 'chaos': 2.5, 'swing': 0, 'bass': 6},
        'hardwell-style':    {'intensity': 9, 'euphoria': 7.5, 'space': 5.5, 'pulse': 9.5, 'chaos': 2.5, 'swing': 1.5, 'bass': 6},
        'phonk':             {'intensity': 9, 'euphoria': 1, 'space': 1, 'pulse': 3.5, 'chaos': 7.5, 'swing': 9, 'bass': 7.5},
        'breakbeat':         {'intensity': 7.5, 'euphoria': 5, 'space': 5, 'pulse': 2, 'chaos': 7.5, 'swing': 9, 'bass': 6},
        'future-funk':       {'intensity': 4.5, 'euphoria': 9.5, 'space': 5.5, 'pulse': 8, 'chaos': 3.5, 'swing': 9.5, 'bass': 4.5}
    }

    # High-level "umbrella" genres that skew data if combined with specific subgenres
    GENERIC_GENRES = {'electronic', 'edm', 'house', 'techno', 'trance', 'dance', 'electronica', }

    @classmethod
    def get_artist_vibe(cls, genres):
        """
        Takes a list of Last.fm genres for an artist, maps them, 
        and returns the averaged Hexagon coordinates, weighted by relevance 
        (the first genre has the most weight, decreasing thereafter).
        Generic umbrella genres are discarded if specific subgenres exist.
        """
        # Separate genres into generic and specific
        generic_matches = []
        specific_matches = []
        
        for g in genres:
            genre_lower = g.lower()
            if genre_lower in cls.SONIC_DNA:
                if genre_lower in cls.GENERIC_GENRES:
                    generic_matches.append(genre_lower)
                else:
                    specific_matches.append(genre_lower)
                    
        # If we have specific genres, use ONLY them to prevent skewing.
        # Otherwise, fall back to the generic ones.
        active_genres = specific_matches if specific_matches else generic_matches
        
        vectors = [cls.SONIC_DNA[g] for g in active_genres]
        
        # If no genres map, return a dead-center generic Nothing
        if not vectors:
            return None
            
        # Calculate weighted average
        # Weight = 1.0 / (index + 1) -> [1.0, 0.5, 0.33, 0.25, ...]
        weights = [1.0 / (i + 1) for i in range(len(vectors))]
        total_weight = sum(weights)
        
        avg_vibe = {}
        for category in cls.CATEGORIES:
            # Sum (value * weight) for each matched genre
            weighted_sum = sum(v[category] * w for v, w in zip(vectors, weights))
            # Divide by total weight to normalize back to a 1-10 scale
            avg_vibe[category] = weighted_sum / total_weight
        
        # Round to 1 decimal place for clean data
        return {k: round(v, 2) for k, v in avg_vibe.items()}


    @classmethod
    def update_user_dna(cls, user_id):
        load_dotenv()
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        supabase: Client = create_client(url, key)
        print(f"Fetching sonic DNA and play counts for {user_id}...")
        # We ask for the user_lib row, but ALSO tell Supabase 
        # to look up the name and sonic_dna from the artists table.
        response = supabase.table("user_lib").select("count, artists(name, sonic_dna, genres)").eq("user_id", user_id).execute()
        artist_data_list = []
        full_artist_info_list = [] # For subgenre extraction
        
        for row in response.data:
            play_count = row.get("count", 1)
            artist_info = row.get('artists')
            if not artist_info:
                continue
                
            dna = artist_info.get("sonic_dna")
            name = artist_info.get("name", "Unknown Artist")
            genres = artist_info.get("genres", [])
            
            if dna and isinstance(dna, dict):
                # Only add if it has all the standard categories
                if all(cat in dna for cat in cls.CATEGORIES):
                    artist_data_list.append({
                        'name': name,
                        'dna': dna,
                        'count': play_count
                    })
                    full_artist_info_list.append({
                        'name': name,
                        'genres': genres,
                        'count': play_count
                    })
        
        # Calculate the user's DNA
        user_dna = cls.calculate_user_dna(artist_data_list)
        
        # Calculate the user's Subgenre Vector (Top 25)
        user_subgenres = cls.extract_top_subgenres(full_artist_info_list, limit=25)
        
        # Update the user's data in the database
        supabase.table("public.users").update({
            "sonic_dna": user_dna,
            "subgenres": user_subgenres
        }).eq("id", user_id).execute()
        
        return artist_data_list



    @classmethod
    def recalculate_all_artist_dna(cls):
        """Iterates through every artist in the database and updates their Sonic DNA based on current mapping."""
        load_dotenv()
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        supabase: Client = create_client(url, key)
        
        print("🔄 Fetching all artists from database...")
        # Note: using 'id' to ensure we update the correct row precisely
        response = supabase.table("artists").select("id, name, name_slug, genres").execute()
        artists = response.data
        
        if not artists:
            print("❌ No artists found in database.")
            return

        print(f"🧪 Recalculating DNA for {len(artists)} artists using new dramatic values...")
        updates = []
        
        for artist in artists:
            genres = artist.get('genres', [])
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
            # Batch updates in chunks of 500
            for i in range(0, len(updates), 500):
                batch = updates[i:i+500]
                supabase.table("artists").upsert(batch).execute()
        
        print(f"✅ Successfully updated DNA for {len(updates)} artists.")
        return len(updates)

    @classmethod
    def calculate_dna(cls, artist_data_list):
        """
        Calculates a frequency-weighted average DNA for a collection of artists.
        artist_data_list: List of dicts like [{'dna': {...}, 'count': 5}]
        Returns a dict with the averaged categories.
        """
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
        """Wrapper for calculate_dna, specifically for user context."""
        return cls.calculate_dna(artist_data_list)

    @classmethod
    def extract_top_subgenres(cls, artist_info_list, limit=25):
        """
        Aggregates subgenres from artist info (name, genres, count).
        Weights subgenres based on artist frequency.
        Returns a normalized dict of top X subgenres.
        """
        subgenre_weights = {}
        
        for artist in artist_info_list:
            genres = artist.get('genres', [])
            count = artist.get('count', 1)
            
            # Map raw genres to our canonical subgenres
            mapped_subgenres = []
            for g in genres:
                g_lower = g.lower()
                if g_lower in cls.SONIC_DNA:
                    mapped_subgenres.append(g_lower)
            
            if not mapped_subgenres:
                continue
                
            # Distribute the artist's "weight" (play count) across their subgenres
            # The first subgenre gets the most weight (per get_artist_vibe logic)
            weights = [1.0 / (i + 1) for i in range(len(mapped_subgenres))]
            total_artist_weight = sum(weights)
            
            for sub, w in zip(mapped_subgenres, weights):
                contribution = (w / total_artist_weight) * count
                subgenre_weights[sub] = subgenre_weights.get(sub, 0.0) + contribution
        
        if not subgenre_weights:
            return {}
            
        # Sort by weight descending
        sorted_subgenres = sorted(subgenre_weights.items(), key=lambda x: x[1], reverse=True)
        top_subgenres = sorted_subgenres[:limit]
        
        # Normalize weights between 0 and 1 relative to the top subgenre
        max_weight = top_subgenres[0][1]
        normalized_vector = {sub: round(w / max_weight, 3) for sub, w in top_subgenres}
        
        return normalized_vector