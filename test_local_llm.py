#!/usr/bin/env python3
"""
Quick test to verify local LLM setup works without API token.
"""

print("=" * 70)
print("🧪 Testing Local LLM (No API Token Required)")
print("=" * 70)
print()

# Test 1: Import check
print("1️⃣  Checking imports...")
try:
    from app.utils.local_llm import LocalLLM
    print("   ✅ LocalLLM module loaded")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    exit(1)

# Test 2: Model loading
print("\n2️⃣  Loading model (first time downloads ~1GB)...")
try:
    llm = LocalLLM(model_name="google/flan-t5-small")  # Smaller model for faster test
    print("   ✅ Model loaded successfully")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    exit(1)

# Test 3: Simple inference
print("\n3️⃣  Testing inference...")
try:
    result = llm.invoke("What is Python?")
    print(f"   ✅ Inference works!")
    print(f"   Response: {result[:100]}...")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    exit(1)

print("\n" + "=" * 70)
print("🎉 SUCCESS! Local LLM works without any API token!")
print("=" * 70)
print()
print("📝 Note: The model was downloaded to ~/.cache/huggingface/")
print("   Subsequent runs will be much faster (no download needed)")
print()
print("🚀 You can now start the server without any token:")
print("   uvicorn app.main:app --host 0.0.0.0 --port 8000")
