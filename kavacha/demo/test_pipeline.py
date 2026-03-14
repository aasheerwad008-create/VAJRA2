"""
KAVACHA End-to-End Pipeline Test
Run this before judges arrive to verify everything works.
"""
import requests
import json
import time

BASE = "http://localhost:8000"


def test(name, passed, detail=""):
    icon = "✅" if passed else "❌"
    print(f"{icon} {name}" + (f": {detail}" if detail else ""))
    return passed


def run_tests():
    print("\n🛡️  KAVACHA PRE-DEMO SYSTEM CHECK")
    print("=" * 50)
    all_pass = True

    # 1. Health check
    try:
        r = requests.get(f"{BASE}/api/v1/health", timeout=5)
        d = r.json()
        p = r.status_code == 200 and "ecapa" in d.get("models", [])
        all_pass &= test("Backend health", p, str(d.get("models")))
    except Exception as e:
        all_pass &= test("Backend health", False, str(e))

    # 2. Authentic scenario
    try:
        r = requests.get(f"{BASE}/api/v1/demo/simulate/authentic")
        d = r.json()
        p = d["verdict"] == "AUTHENTIC" and d["trust_score"] > 70
        all_pass &= test("Authentic demo", p, f"Score: {d['trust_score']}, Verdict: {d['verdict']}")
    except Exception as e:
        all_pass &= test("Authentic demo", False, str(e))

    # 3. Deepfake scenario
    try:
        r = requests.get(f"{BASE}/api/v1/demo/simulate/deepfake")
        d = r.json()
        p = d["verdict"] == "DEEPFAKE" and d["trust_score"] < 40
        all_pass &= test("Deepfake detection", p, f"Score: {d['trust_score']}, Verdict: {d['verdict']}")
    except Exception as e:
        all_pass &= test("Deepfake detection", False, str(e))

    # 4. ZK proof generation
    try:
        r = requests.post(f"{BASE}/api/v1/zk/generate-proof", json={
            "biometric_hash": "0x" + "a" * 64,
            "liveness_score": 0.87,
            "trust_score": 87.3,
            "user_address": "0x742d35Cc6634C0532925a3b8D4C9B6eD5e6f3842"
        })
        d = r.json()
        p = "proof_hash" in d and d["proof_hash"].startswith("0x")
        all_pass &= test("ZK proof generation", p, d.get("proof_hash", "")[:20] + "...")
    except Exception as e:
        all_pass &= test("ZK proof generation", False, str(e))

    # 5. Blockchain anchor
    try:
        r = requests.post(f"{BASE}/api/v1/zk/anchor-blockchain", json={
            "proof_hash": "0x" + "b" * 64,
            "user_address": "0x742d35Cc6634C0532925a3b8D4C9B6eD5e6f3842"
        })
        d = r.json()
        p = "tx_hash" in d and "polygonscan" in d.get("block_explorer", "")
        all_pass &= test("Blockchain anchor", p, d.get("tx_hash", "")[:20] + "...")
    except Exception as e:
        all_pass &= test("Blockchain anchor", False, str(e))

    # 6. Video perturbation
    try:
        import base64
        import numpy as np
        import cv2
        blank = np.zeros((240, 320, 3), dtype=np.uint8)
        _, buf = cv2.imencode('.jpg', blank)
        b64 = base64.b64encode(buf).decode()
        r = requests.post(f"{BASE}/api/v1/video/perturb", json={"frame_base64": b64, "method": "pgd"})
        d = r.json()
        p = "perturbed_frame" in d
        all_pass &= test("Video perturbation", p, f"Method: {d.get('method')}")
    except Exception as e:
        all_pass &= test("Video perturbation", False, str(e))

    print("=" * 50)
    if all_pass:
        print("✅ ALL SYSTEMS GO — KAVACHA IS READY FOR JUDGES")
    else:
        print("❌ SOME TESTS FAILED — FIX BEFORE DEMO")
    return all_pass


if __name__ == "__main__":
    run_tests()
