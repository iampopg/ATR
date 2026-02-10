#!/usr/bin/env python3
"""
Week 3 - Task 4: Entropy Analyzer
Calculates Shannon entropy to detect encryption
"""

import math
from collections import Counter

def calculate_entropy(filepath):
    """Calculate Shannon entropy of file (0-8 bits/byte)"""
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        
        if not data:
            return 0.0
        
        # Count byte frequencies
        byte_counts = Counter(data)
        total_bytes = len(data)
        
        # Calculate entropy
        entropy = 0.0
        for count in byte_counts.values():
            probability = count / total_bytes
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    except Exception as e:
        print(f"Error calculating entropy: {e}")
        return 0.0

def is_encrypted(entropy):
    """Detect if file is likely encrypted (entropy > 7.5)"""
    return entropy > 7.5

def classify_entropy(entropy):
    """Classify file based on entropy"""
    if entropy < 4.0:
        return "Low (Repetitive data)"
    elif entropy < 6.0:
        return "Normal (Text/Code)"
    elif entropy < 7.5:
        return "High (Compressed)"
    else:
        return "Very High (Encrypted/Random)"

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python week3_entropy_analyzer.py <file_path>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    entropy = calculate_entropy(filepath)
    
    print(f"File: {filepath}")
    print(f"Entropy: {entropy:.2f} bits/byte")
    print(f"Classification: {classify_entropy(entropy)}")
    print(f"Encrypted: {'YES' if is_encrypted(entropy) else 'NO'}")
