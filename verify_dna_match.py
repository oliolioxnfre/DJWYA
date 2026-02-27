
import math
from classifier import VibeClassifier

def test_dna_consistency():
    # Sample data: 2 artists with specific DNA and play counts
    sample_artist_data = [
        {
            'name': 'Artist A',
            'dna': {'intensity': 10, 'euphoria': 0, 'space': 5, 'pulse': 10, 'chaos': 4, 'swing': 0, 'bass': 6},
            'count': 3
        },
        {
            'name': 'Artist B',
            'dna': {'intensity': 4, 'euphoria': 9, 'space': 9, 'pulse': 9, 'chaos': 1, 'swing': 1, 'bass': 3},
            'count': 1
        }
    ]

    # Calculate DNA using the centralized method
    calculated_dna = VibeClassifier.calculate_dna(sample_artist_data)
    
    # Manual calculation:
    # total_plays = 4
    # intensity: (10*3 + 4*1) / 4 = 34 / 4 = 8.5
    # euphoria: (0*3 + 9*1) / 4 = 9 / 4 = 2.25
    # space: (5*3 + 9*1) / 4 = 24 / 4 = 6.0
    # pulse: (10*3 + 9*1) / 4 = 39 / 4 = 9.75
    # chaos: (4*3 + 1*1) / 4 = 13 / 4 = 3.25
    # swing: (0*3 + 1*1) / 4 = 1 / 4 = 0.25
    # bass: (6*3 + 3*1) / 4 = 21 / 4 = 5.25
    
    expected_dna = {
        'intensity': 8.5,
        'euphoria': 2.25,
        'space': 6.0,
        'pulse': 9.75,
        'chaos': 3.25,
        'swing': 0.25,
        'bass': 5.25
    }
    
    print(f"Calculated: {calculated_dna}")
    print(f"Expected:   {expected_dna}")
    
    for cat in VibeClassifier.CATEGORIES:
        assert calculated_dna[cat] == expected_dna[cat], f"Mismatch in {cat}: {calculated_dna[cat]} != {expected_dna[cat]}"
    
    print("✅ DNA Calculation consistency test passed!")

    # Test distance for identical DNA
    user_dna = calculated_dna
    fest_dna = calculated_dna # Exact same
    
    squared_diffs = [(user_dna[cat] - fest_dna[cat]) ** 2 for cat in VibeClassifier.CATEGORIES]
    dist = math.sqrt(sum(squared_diffs))
    synergy = 100 * math.exp(-0.15 * dist)
    
    print(f"Synergy for identical DNA: {synergy}%")
    assert synergy == 100.0, f"Synergy should be 100% for identical DNA, got {synergy}%"
    print("✅ Synergy 100% test passed!")

if __name__ == "__main__":
    test_dna_consistency()
