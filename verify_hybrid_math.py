
import math

# Mocking the math for verification
def cosine_similarity(vec1, vec2):
    if not vec1 or not vec2: return 0.0
    intersect = set(vec1.keys()) & set(vec2.keys())
    if not intersect: return 0.0
    dot_product = sum(vec1[k] * vec2[k] for k in intersect)
    mag1 = math.sqrt(sum(v**2 for v in vec1.values()))
    mag2 = math.sqrt(sum(v**2 for v in vec2.values()))
    return dot_product / (mag1 * mag2)

def calculate_hybrid_score(user_data, festival_data):
    user_dna = user_data.get('sonic_dna', {})
    fest_dna = festival_data.get('sonic_dna', {})
    user_subs = user_data.get('subgenres', {})
    fest_subs = festival_data.get('subgenres', {})
    
    # Cosine
    s_score = cosine_similarity(user_subs, fest_subs)
    
    # Euclidean
    weights = {'intensity': 1.5, 'pulse': 1.5, 'euphoria': 1.0, 'space': 1.0, 'chaos': 1.0, 'swing': 1.0, 'bass': 1.2}
    cats = ['intensity', 'euphoria', 'space', 'pulse', 'chaos', 'swing', 'bass']
    
    sq_diffs = []
    for cat in cats:
        u = float(user_dna.get(cat, 0))
        f = float(fest_dna.get(cat, 0))
        w = weights.get(cat, 1.0)
        sq_diffs.append(w * (u - f)**2)
    dist = math.sqrt(sum(sq_diffs))
    a_score = math.exp(-0.15 * dist)
    
    hybrid = (0.7 * s_score) + (0.3 * a_score)
    return round(hybrid * 100, 2)

def verify():
    # Test 1: Identical Data
    user = {
        'sonic_dna': {'intensity': 8, 'pulse': 8, 'bass': 5},
        'subgenres': {'dark_techno': 1.0, 'industrial': 0.5}
    }
    score = calculate_hybrid_score(user, user)
    print(f"Identical Match Score: {score}%")
    assert score == 100.0
    
    # Test 2: Different Subgenres, Same DNA
    fest_diff_subs = {
        'sonic_dna': {'intensity': 8, 'pulse': 8, 'bass': 5},
        'subgenres': {'trance': 1.0}
    }
    score_diff = calculate_hybrid_score(user, fest_diff_subs)
    print(f"Same DNA, Different Subgenres Score: {score_diff}%")
    # s_score should be 0. a_score should be 1.0. Final = 0.7*0 + 0.3*1.0 = 30%
    assert 29.0 < score_diff < 31.0
    
    # Test 3: Overlapping Subgenres
    fest_overlap = {
        'sonic_dna': {'intensity': 8, 'pulse': 8, 'bass': 5},
        'subgenres': {'dark_techno': 0.8, 'minimal': 0.5}
    }
    score_overlap = calculate_hybrid_score(user, fest_overlap)
    print(f"Overlapping Subgenres Score: {score_overlap}%")
    # Cosine between {dark: 1, ind: 0.5} and {dark: 0.8, min: 0.5}
    # Dot = 1 * 0.8 = 0.8
    # Mag1 = sqrt(1^2 + 0.5^2) = sqrt(1.25) = 1.118
    # Mag2 = sqrt(0.8^2 + 0.5^2) = sqrt(0.64 + 0.25) = sqrt(0.89) = 0.943
    # Cos = 0.8 / (1.118 * 0.943) = 0.8 / 1.054 = 0.759
    # Final = (0.7 * 0.759) + (0.3 * 1.0) = 0.531 + 0.3 = 0.831 -> 83.1%
    assert 80.0 < score_overlap < 85.0

    print("✅ Hybrid Math Verification Passed!")

if __name__ == "__main__":
    verify()
