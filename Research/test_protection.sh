#!/bin/bash
# Test script: Generate token for wrong file, try to use on ARCHITECTURE.md

echo "=========================================="
echo "TEST: Token for wrong file"
echo "=========================================="
echo ""

# Step 1: Generate token for DIFFERENT file
echo "Step 1: Generating token for /tmp/other_file.txt"
echo "----------------------------------------"
python3 token_generator.py /tmp/other_file.txt > /tmp/token_output.txt
cat /tmp/token_output.txt
echo ""

# Extract token details
TOKEN=$(grep "Token:" /tmp/token_output.txt | awk '{print $2}')
TIMESTAMP=$(grep "Timestamp:" /tmp/token_output.txt | awk '{print $2}')

# Generate nonces (simplified - in real test use actual nonces)
NONCE_C="1234567890abcdef1234567890abcdef"
NONCE_S="fedcba0987654321fedcba0987654321"

echo "Step 2: Trying to use this token on ARCHITECTURE.md"
echo "----------------------------------------"
python3 file_protector.py "$TOKEN" "$NONCE_C" "$NONCE_S" "$TIMESTAMP"
echo ""

echo "=========================================="
echo "Expected: ❌ DENIED (token for wrong file)"
echo "=========================================="
