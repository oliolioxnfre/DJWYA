import os
from dotenv import load_dotenv
from supabase import create_client, Client

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
    
    # The Master Sonic DNA Dictionary
    SONIC_DNA = {
        # --- PARENT: HOUSE ---
        'house':             {'intensity': 5, 'euphoria': 7, 'space': 5, 'pulse': 10, 'chaos': 0, 'swing': 10, 'bass': 5},
        'deep-house':        {'intensity': 2, 'euphoria': 8, 'space': 10, 'pulse': 10, 'chaos': 1, 'swing': 8, 'bass': 7},
        'tech-house':        {'intensity': 7, 'euphoria': 4, 'space': 4, 'pulse': 10, 'chaos': 4, 'swing': 10, 'bass': 6},
        'progressive-house': {'intensity': 5, 'euphoria': 10, 'space': 9, 'pulse': 10, 'chaos': 2, 'swing': 3, 'bass': 4},
        'future-house':      {'intensity': 7, 'euphoria': 8, 'space': 4, 'pulse': 10, 'chaos': 5, 'swing': 7, 'bass': 8},
        'bass-house':        {'intensity': 10, 'euphoria': 3, 'space': 2, 'pulse': 10, 'chaos': 7, 'swing': 8, 'bass': 10},
        'tropical-house':    {'intensity': 2, 'euphoria': 10, 'space': 8, 'pulse': 10, 'chaos': 1, 'swing': 6, 'bass': 3},
        'electro-house':     {'intensity': 9, 'euphoria': 6, 'space': 3, 'pulse': 10, 'chaos': 6, 'swing': 4, 'bass': 7},
        'acid-house':        {'intensity': 7, 'euphoria': 4, 'space': 6, 'pulse': 10, 'chaos': 9, 'swing': 7, 'bass': 6},
        'g-house':           {'intensity': 8, 'euphoria': 2, 'space': 3, 'pulse': 10, 'chaos': 4, 'swing': 9, 'bass': 9},
        'afro-house':        {'intensity': 4, 'euphoria': 6, 'space': 7, 'pulse': 10, 'chaos': 3, 'swing': 10, 'bass': 5},
        'organic-house':     {'intensity': 2, 'euphoria': 7, 'space': 9, 'pulse': 10, 'chaos': 2, 'swing': 9, 'bass': 4},
        'chicago-house':     {'intensity': 5, 'euphoria': 7, 'space': 5, 'pulse': 10, 'chaos': 4, 'swing': 10, 'bass': 6},
        'disco-house':       {'intensity': 5, 'euphoria': 10, 'space': 5, 'pulse': 10, 'chaos': 2, 'swing': 10, 'bass': 5},
        'nu-disco':          {'intensity': 4, 'euphoria': 9, 'space': 6, 'pulse': 10, 'chaos': 3, 'swing': 10, 'bass': 5},
        'lo-fi-house':       {'intensity': 3, 'euphoria': 5, 'space': 9, 'pulse': 10, 'chaos': 5, 'swing': 8, 'bass': 5},
        'funky-house':       {'intensity': 4, 'euphoria': 9, 'space': 4, 'pulse': 10, 'chaos': 3, 'swing': 10, 'bass': 6},
        'hard-house':        {'intensity': 10, 'euphoria': 5, 'space': 1, 'pulse': 10, 'chaos': 6, 'swing': 6, 'bass': 7},
        'jazz-house':        {'intensity': 3, 'euphoria': 8, 'space': 7, 'pulse': 10, 'chaos': 5, 'swing': 10, 'bass': 5},
        'rally-house':       {'intensity': 7, 'euphoria': 6, 'space': 4, 'pulse': 9, 'chaos': 5, 'swing': 7, 'bass': 6},
        'witch-house':       {'intensity': 9, 'euphoria': 3, 'space': 10, 'pulse': 7, 'chaos': 6, 'swing': 4, 'bass': 7},
        'melodic-house':     {'intensity': 4, 'euphoria': 9, 'space': 9, 'pulse': 10, 'chaos': 2, 'swing': 6, 'bass': 4},
        'speed-house':       {'intensity': 10, 'euphoria': 7, 'space': 3, 'pulse': 10, 'chaos': 8, 'swing': 8, 'bass': 7},
        'ghetto-house':      {'intensity': 9, 'euphoria': 2, 'space': 2, 'pulse': 10, 'chaos': 7, 'swing': 10, 'bass': 8},

        # --- PARENT: TECHNO ---
        'techno':            {'intensity': 8, 'euphoria': 1, 'space': 6, 'pulse': 10, 'chaos': 0, 'swing': 0, 'bass': 5},
        'minimal-techno':    {'intensity': 3, 'euphoria': 2, 'space': 10, 'pulse': 10, 'chaos': 1, 'swing': 1, 'bass': 3},
        'hard-techno':       {'intensity': 10, 'euphoria': 0, 'space': 3, 'pulse': 10, 'chaos': 3, 'swing': 0, 'bass': 7},
        'acid-techno':       {'intensity': 9, 'euphoria': 2, 'space': 5, 'pulse': 10, 'chaos': 10, 'swing': 1, 'bass': 6},
        'dub-techno':        {'intensity': 4, 'euphoria': 3, 'space': 10, 'pulse': 8, 'chaos': 1, 'swing': 4, 'bass': 6},
        'detroit-techno':    {'intensity': 6, 'euphoria': 5, 'space': 6, 'pulse': 10, 'chaos': 4, 'swing': 4, 'bass': 5},
        'peak-time-techno':  {'intensity': 10, 'euphoria': 5, 'space': 5, 'pulse': 10, 'chaos': 2, 'swing': 0, 'bass': 6},
        'industrial-techno': {'intensity': 10, 'euphoria': 0, 'space': 4, 'pulse': 10, 'chaos': 6, 'swing': 0, 'bass': 7},
        'melodic-techno':    {'intensity': 5, 'euphoria': 9, 'space': 10, 'pulse': 10, 'chaos': 1, 'swing': 1, 'bass': 4},
        'dark-techno':       {'intensity': 9, 'euphoria': 1, 'space': 8, 'pulse': 10, 'chaos': 3, 'swing': 0, 'bass': 6},
        'hypnotic-techno':   {'intensity': 4, 'euphoria': 2, 'space': 10, 'pulse': 10, 'chaos': 0, 'swing': 0, 'bass': 4},
        'cyber-house':       {'intensity': 8, 'euphoria': 6, 'space': 10, 'pulse': 10, 'chaos': 5, 'swing': 2, 'bass': 6},

        # --- PARENT: TRANCE ---
        'trance':            {'intensity': 6, 'euphoria': 10, 'space': 10, 'pulse': 10, 'chaos': 1, 'swing': 0, 'bass': 3},
        'uplifting-trance':  {'intensity': 7, 'euphoria': 10, 'space': 10, 'pulse': 10, 'chaos': 2, 'swing': 0, 'bass': 3},
        'psytrance':         {'intensity': 10, 'euphoria': 5, 'space': 9, 'pulse': 10, 'chaos': 9, 'swing': 2, 'bass': 6},
        'progressive-trance':{'intensity': 5, 'euphoria': 9, 'space': 9, 'pulse': 10, 'chaos': 2, 'swing': 2, 'bass': 4},
        'goa-trance':        {'intensity': 8, 'euphoria': 7, 'space': 8, 'pulse': 10, 'chaos': 10, 'swing': 3, 'bass': 5},
        'vocal-trance':      {'intensity': 5, 'euphoria': 10, 'space': 9, 'pulse': 9, 'chaos': 1, 'swing': 0, 'bass': 2},
        'tech-trance':       {'intensity': 9, 'euphoria': 4, 'space': 6, 'pulse': 10, 'chaos': 5, 'swing': 1, 'bass': 5},
        'dream-trance':      {'intensity': 3, 'euphoria': 10, 'space': 10, 'pulse': 8, 'chaos': 1, 'swing': 1, 'bass': 2},
        'hard-trance':       {'intensity': 10, 'euphoria': 7, 'space': 6, 'pulse': 10, 'chaos': 4, 'swing': 1, 'bass': 6},
        'acid-trance':       {'intensity': 8, 'euphoria': 6, 'space': 8, 'pulse': 10, 'chaos': 10, 'swing': 2, 'bass': 5},

        # --- PARENT: DRUM AND BASS ---
        'drum-and-bass':     {'intensity': 9, 'euphoria': 5, 'space': 4, 'pulse': 0, 'chaos': 7, 'swing': 10, 'bass': 9},
        'liquid-dnb':        {'intensity': 4, 'euphoria': 10, 'space': 10, 'pulse': 1, 'chaos': 2, 'swing': 9, 'bass': 7},
        'neurofunk':         {'intensity': 10, 'euphoria': 2, 'space': 5, 'pulse': 1, 'chaos': 10, 'swing': 8, 'bass': 10},
        'jump-up':           {'intensity': 10, 'euphoria': 5, 'space': 2, 'pulse': 2, 'chaos': 8, 'swing': 10, 'bass': 9},
        'jungle':            {'intensity': 8, 'euphoria': 6, 'space': 6, 'pulse': 0, 'chaos': 9, 'swing': 10, 'bass': 8},
        'breakcore':         {'intensity': 10, 'euphoria': 3, 'space': 4, 'pulse': 0, 'chaos': 10, 'swing': 6, 'bass': 7},
        'halftime-dnb':      {'intensity': 8, 'euphoria': 4, 'space': 7, 'pulse': 2, 'chaos': 6, 'swing': 9, 'bass': 9},
        'techstep':          {'intensity': 10, 'euphoria': 1, 'space': 4, 'pulse': 1, 'chaos': 7, 'swing': 8, 'bass': 9},
        'darkstep':          {'intensity': 10, 'euphoria': 0, 'space': 5, 'pulse': 1, 'chaos': 9, 'swing': 7, 'bass': 9},
        'atmospheric-dnb':   {'intensity': 4, 'euphoria': 9, 'space': 10, 'pulse': 1, 'chaos': 3, 'swing': 8, 'bass': 6},
        'atmospheric-jungle':{'intensity': 5, 'euphoria': 8, 'space': 10, 'pulse': 0, 'chaos': 6, 'swing': 10, 'bass': 7},

        # --- PARENT: BASS MUSIC & DUBSTEP ---
        'dubstep':           {'intensity': 10, 'euphoria': 4, 'space': 5, 'pulse': 1, 'chaos': 8, 'swing': 6, 'bass': 10},
        'riddim':            {'intensity': 10, 'euphoria': 1, 'space': 1, 'pulse': 2, 'chaos': 6, 'swing': 7, 'bass': 10},
        'brostep':           {'intensity': 10, 'euphoria': 5, 'space': 3, 'pulse': 1, 'chaos': 10, 'swing': 4, 'bass': 10},
        'future-bass':       {'intensity': 6, 'euphoria': 10, 'space': 8, 'pulse': 4, 'chaos': 6, 'swing': 5, 'bass': 8},
        'trap':              {'intensity': 9, 'euphoria': 4, 'space': 4, 'pulse': 4, 'chaos': 6, 'swing': 9, 'bass': 9},
        'wave':              {'intensity': 4, 'euphoria': 7, 'space': 10, 'pulse': 5, 'chaos': 4, 'swing': 4, 'bass': 6},
        'glitch-hop':        {'intensity': 7, 'euphoria': 9, 'space': 6, 'pulse': 3, 'chaos': 9, 'swing': 10, 'bass': 8},
        'color-bass':        {'intensity': 9, 'euphoria': 10, 'space': 7, 'pulse': 2, 'chaos': 9, 'swing': 5, 'bass': 9},
        'colour-bass':       {'intensity': 9, 'euphoria': 10, 'space': 7, 'pulse': 2, 'chaos': 9, 'swing': 5, 'bass': 9},
        'melodic-dubstep':   {'intensity': 8, 'euphoria': 10, 'space': 9, 'pulse': 1, 'chaos': 4, 'swing': 3, 'bass': 8},
        'deathstep':         {'intensity': 10, 'euphoria': 0, 'space': 2, 'pulse': 1, 'chaos': 10, 'swing': 2, 'bass': 10},
        'uk-garage':         {'intensity': 4, 'euphoria': 7, 'space': 6, 'pulse': 10, 'chaos': 4, 'swing': 10, 'bass': 7},
        'speed-garage':      {'intensity': 7, 'euphoria': 9, 'space': 4, 'pulse': 10, 'chaos': 5, 'swing': 10, 'bass': 8},
        '2-step':            {'intensity': 4, 'euphoria': 6, 'space': 5, 'pulse': 5, 'chaos': 5, 'swing': 10, 'bass': 7},
        'melodic-bass':      {'intensity': 7, 'euphoria': 10, 'space': 9, 'pulse': 2, 'chaos': 5, 'swing': 4, 'bass': 8},
        'glitchcore':        {'intensity': 10, 'euphoria': 10, 'space': 3, 'pulse': 4, 'chaos': 10, 'swing': 4, 'bass': 8},
        'bass':              {'intensity': 8, 'euphoria': 5, 'space': 5, 'pulse': 5, 'chaos': 6, 'swing': 7, 'bass': 10},
        'glitch':            {'intensity': 7, 'euphoria': 9, 'space': 6, 'pulse': 3, 'chaos': 10, 'swing': 6, 'bass': 6},
        'moombahton':        {'intensity': 7, 'euphoria': 8, 'space': 4, 'pulse': 8, 'chaos': 5, 'swing': 10, 'bass': 8},
        'midtempo-bass':     {'intensity': 9, 'euphoria': 4, 'space': 8, 'pulse': 7, 'chaos': 8, 'swing': 5, 'bass': 9},
        'hardwave':          {'intensity': 7, 'euphoria': 8, 'space': 10, 'pulse': 5, 'chaos': 6, 'swing': 4, 'bass': 7},
        'drift-phonk':       {'intensity': 10, 'euphoria': 1, 'space': 4, 'pulse': 6, 'chaos': 8, 'swing': 9, 'bass': 9},
        'juke':              {'intensity': 9, 'euphoria': 3, 'space': 3, 'pulse': 0, 'chaos': 10, 'swing': 10, 'bass': 7},
        'footwork':          {'intensity': 10, 'euphoria': 3, 'space': 4, 'pulse': 0, 'chaos': 10, 'swing': 10, 'bass': 7},
        'grime':             {'intensity': 8, 'euphoria': 2, 'space': 4, 'pulse': 2, 'chaos': 7, 'swing': 10, 'bass': 9},
        'dub':               {'intensity': 3, 'euphoria': 5, 'space': 10, 'pulse': 8, 'chaos': 4, 'swing': 10, 'bass': 10},

        # --- PARENT: HARD DANCE / HARDCORE ---
        'hardstyle':         {'intensity': 10, 'euphoria': 7, 'space': 4, 'pulse': 10, 'chaos': 5, 'swing': 1, 'bass': 8},
        'euphoric-hardstyle':{'intensity': 9, 'euphoria': 10, 'space': 6, 'pulse': 10, 'chaos': 4, 'swing': 2, 'bass': 7},
        'rawstyle':          {'intensity': 10, 'euphoria': 2, 'space': 2, 'pulse': 10, 'chaos': 7, 'swing': 0, 'bass': 9},
        'gabber':            {'intensity': 10, 'euphoria': 1, 'space': 2, 'pulse': 10, 'chaos': 8, 'swing': 0, 'bass': 8},
        'happy-hardcore':    {'intensity': 9, 'euphoria': 10, 'space': 5, 'pulse': 10, 'chaos': 6, 'swing': 4, 'bass': 6},
        'frenchcore':        {'intensity': 10, 'euphoria': 3, 'space': 2, 'pulse': 10, 'chaos': 9, 'swing': 0, 'bass': 9},
        'uptempo-hardcore':  {'intensity': 10, 'euphoria': 0, 'space': 1, 'pulse': 10, 'chaos': 10, 'swing': 0, 'bass': 8},
        'hard-dance':        {'intensity': 10, 'euphoria': 6, 'space': 4, 'pulse': 10, 'chaos': 6, 'swing': 2, 'bass': 7},
        'hard-bass':         {'intensity': 10, 'euphoria': 4, 'space': 1, 'pulse': 10, 'chaos': 5, 'swing': 10, 'bass': 10},
        'donk':              {'intensity': 9, 'euphoria': 8, 'space': 1, 'pulse': 10, 'chaos': 8, 'swing': 10, 'bass': 8},
        'bounce':            {'intensity': 8, 'euphoria': 9, 'space': 2, 'pulse': 10, 'chaos': 5, 'swing': 10, 'bass': 7},
        'scouse-house':      {'intensity': 8, 'euphoria': 9, 'space': 2, 'pulse': 10, 'chaos': 6, 'swing': 10, 'bass': 7},
        'nightcore':         {'intensity': 10, 'euphoria': 10, 'space': 3, 'pulse': 10, 'chaos': 7, 'swing': 6, 'bass': 5},

        # --- PARENT: DOWNTEMPO / EXPERIMENTAL ---
        'downtempo':         {'intensity': 0, 'euphoria': 6, 'space': 10, 'pulse': 4, 'chaos': 1, 'swing': 7, 'bass': 4},
        'idm':               {'intensity': 0, 'euphoria': 4, 'space': 8, 'pulse': 0, 'chaos': 10, 'swing': 6, 'bass': 4},
        'trip-hop':          {'intensity': 0, 'euphoria': 4, 'space': 8, 'pulse': 5, 'chaos': 4, 'swing': 9, 'bass': 7},
        'chillstep':         {'intensity': 0, 'euphoria': 8, 'space': 10, 'pulse': 3, 'chaos': 2, 'swing': 5, 'bass': 6},
        'psydub':            {'intensity': 0, 'euphoria': 7, 'space': 10, 'pulse': 4, 'chaos': 7, 'swing': 7, 'bass': 8},
        'vaporwave':         {'intensity': 2, 'euphoria': 7, 'space': 10, 'pulse': 3, 'chaos': 3, 'swing': 5, 'bass': 3},
        'synthwave':         {'intensity': 2, 'euphoria': 8, 'space': 9, 'pulse': 8, 'chaos': 2, 'swing': 4, 'bass': 5},
        'illbient':          {'intensity': 0, 'euphoria': 1, 'space': 10, 'pulse': 3, 'chaos': 8, 'swing': 4, 'bass': 5},
        'ethereal':          {'intensity': 0, 'euphoria': 9, 'space': 10, 'pulse': 0, 'chaos': 1, 'swing': 2, 'bass': 1},
        'ambient':           {'intensity': 0, 'euphoria': 5, 'space': 10, 'pulse': 0, 'chaos': 0, 'swing': 0, 'bass': 1},
        'dream-pop':         {'intensity': 2, 'euphoria': 9, 'space': 10, 'pulse': 2, 'chaos': 1, 'swing': 4, 'bass': 3},
        'outrun':            {'intensity': 3, 'euphoria': 8, 'space': 8, 'pulse': 9, 'chaos': 2, 'swing': 3, 'bass': 5},
        'retrowave':         {'intensity': 2, 'euphoria': 8, 'space': 9, 'pulse': 8, 'chaos': 2, 'swing': 3, 'bass': 5},
        'chillsynth':        {'intensity': 1, 'euphoria': 7, 'space': 10, 'pulse': 6, 'chaos': 2, 'swing': 4, 'bass': 3},
        'musique-concrete':  {'intensity': 2, 'euphoria': 0, 'space': 10, 'pulse': 0, 'chaos': 10, 'swing': 3, 'bass': 2},
        'deconstructed-club':{'intensity': 9, 'euphoria': 1, 'space': 7, 'pulse': 3, 'chaos': 10, 'swing': 5, 'bass': 7},

        # --- MISC / HYBRID ---
        'hyperpop':          {'intensity': 10, 'euphoria': 10, 'space': 5, 'pulse': 6, 'chaos': 10, 'swing': 7, 'bass': 6},
        'eurodance':         {'intensity': 7, 'euphoria': 10, 'space': 4, 'pulse': 10, 'chaos': 3, 'swing': 6, 'bass': 5},
        'complextro':        {'intensity': 10, 'euphoria': 10, 'space': 5, 'pulse': 10, 'chaos': 10, 'swing': 6, 'bass': 8},
        'big-room':          {'intensity': 10, 'euphoria': 7, 'space': 6, 'pulse': 10, 'chaos': 3, 'swing': 1, 'bass': 7},
        'hardwell-style':    {'intensity': 10, 'euphoria': 7, 'space': 6, 'pulse': 10, 'chaos': 3, 'swing': 2, 'bass': 7},
        'phonk':             {'intensity': 10, 'euphoria': 1, 'space': 0, 'pulse': 4, 'chaos': 7, 'swing': 9, 'bass': 9},
        'edm':               {'intensity': 8, 'euphoria': 8, 'space': 6, 'pulse': 10, 'chaos': 5, 'swing': 5, 'bass': 6},
        'breakbeat':         {'intensity': 7, 'euphoria': 5, 'space': 5, 'pulse': 2, 'chaos': 7, 'swing': 10, 'bass': 6},
        'future-funk':       {'intensity': 5, 'euphoria': 10, 'space': 5, 'pulse': 8, 'chaos': 4, 'swing': 10, 'bass': 6}
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
        for category in ['intensity', 'euphoria', 'space', 'pulse', 'chaos', 'swing', 'bass']:
            # Sum (value * weight) for each matched genre
            weighted_sum = sum(v[category] * w for v, w in zip(vectors, weights))
            # Divide by total weight to normalize back to a 1-10 scale
            avg_vibe[category] = weighted_sum / total_weight
        
        # Round to 1 decimal place for clean data
        return {k: round(v, 1) for k, v in avg_vibe.items()}


    @classmethod
    def update_user_dna(cls, user_id):
        load_dotenv()
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        supabase: Client = create_client(url, key)
        """Queries the user_lib table joined with artists to get play counts and sonic_dna."""
        print(f"Fetching sonic DNA and play counts for {user_id}...")
        # We ask for the user_lib row, but ALSO tell Supabase 
        # to look up the name and sonic_dna from the artists table.
        response = supabase.table("user_lib").select("count, artists(name, sonic_dna)").eq("user_id", user_id).execute()
        artist_data_list = []
        for row in response.data:
            play_count = row.get("count", 1)
            artist_info = row.get('artists')
            if not artist_info:
                continue
                
            dna = artist_info.get("sonic_dna")
            name = artist_info.get("name", "Unknown Artist")
            
            if dna and isinstance(dna, dict):
                # Only add if it has all the standard categories
                categories = ['intensity', 'euphoria', 'space', 'pulse', 'chaos', 'swing', 'bass']
                if all(cat in dna for cat in categories):
                    artist_data_list.append({
                        'name': name,
                        'dna': dna,
                        'count': play_count
                    })
        
        # Calculate the user's DNA
        user_dna = cls.calculate_user_dna(artist_data_list)
        
        # Update the user's DNA in the database
        supabase.table("public.users").update({"sonic_dna": user_dna}).eq("id", user_id).execute()
        return artist_data_list



    @classmethod
    def calculate_user_dna(cls, artist_data_list):
        """Calculates a weighted average DNA for the user based on artist DNA and play counts."""
        if not artist_data_list:
            return {'intensity': 0, 'euphoria': 0, 'space': 0, 'pulse': 0, 'chaos': 0, 'swing': 0, 'bass': 0}
            
        categories = ['intensity', 'euphoria', 'space', 'pulse', 'chaos', 'swing', 'bass']
        total_play_count = sum(item['count'] for item in artist_data_list)
        
        user_dna = {cat: 0.0 for cat in categories}
        for item in artist_data_list:
            weight = item['count'] / total_play_count
            for cat in categories:
                user_dna[cat] += item['dna'][cat] * weight
                
        return {cat: round(val, 1) for cat, val in user_dna.items()}