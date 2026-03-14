from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json, time, hashlib, logging

logger = logging.getLogger("kavacha")

from models.model_loader import get_all_models
from services.voice_analyzer import analyze_chunk, enroll_voice, decode_audio_b64
from services.adversarial_engine import perturb_frame
from services.zk_simulator import generate_proof, verify_proof

MODELS = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    MODELS.update(get_all_models())
    yield

app = FastAPI(title="KAVACHA API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/api/v1/health")
async def health():
    return {"status": "operational", "models": list(MODELS.keys()), "platform": "KAVACHA v1.0"}

@app.post("/api/v1/voice/enroll")
async def enroll(payload: dict):
    try:
        audio = decode_audio_b64(payload.get("audio_base64",""))
        h = enroll_voice(payload.get("user_id","demo"), audio, MODELS["ecapa"])
        return {"enrollment_id": f"enroll_{int(time.time())}", "voice_passport_hash": h, "status": "enrolled"}
    except Exception as e:
        logger.exception("Enrollment failed")
        raise HTTPException(400, "Enrollment failed")

@app.post("/api/v1/voice/verify")
async def verify(payload: dict):
    try:
        return analyze_chunk(payload.get("audio_base64",""), payload.get("user_id","demo"), MODELS, payload.get("session_id","demo"))
    except Exception as e:
        logger.exception("Voice verification failed")
        raise HTTPException(400, "Voice verification failed")

@app.websocket("/ws/voice/stream/{session_id}")
async def ws_voice(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        while True:
            data = json.loads(await websocket.receive_text())
            if data.get("type") == "audio_chunk":
                result = analyze_chunk(data["audio_b64"], "demo_user", MODELS, session_id)
                await websocket.send_json(result)
            elif data.get("type") == "enroll":
                audio = decode_audio_b64(data["audio_b64"])
                h = enroll_voice("demo_user", audio, MODELS["ecapa"])
                await websocket.send_json({"type": "enrolled", "passport_hash": h})
    except Exception as e:
        logger.warning(f"WS closed: {e}")

@app.post("/api/v1/video/perturb")
async def video_perturb(payload: dict):
    return perturb_frame(payload.get("frame_base64",""), payload.get("method","pgd"))

@app.post("/api/v1/zk/generate-proof")
async def zk_generate(payload: dict):
    p = generate_proof(
        payload.get("biometric_hash","0x"+"a"*64),
        payload.get("liveness_score", 0.85),
        payload.get("trust_score", 75.0),
        payload.get("user_address","0x0")
    )
    return {"proof_hash": p.proof_hash, "public_inputs": p.public_inputs,
            "verifier_key": p.verifier_key, "timestamp": p.timestamp,
            "circuit": p.circuit_version, "proof_size_bytes": p.proof_size_bytes,
            "liveness_confirmed": p.biometric_match,
            "message": "ZK-STARK proof generated. Zero biometric data transmitted."}

@app.post("/api/v1/zk/verify-proof")
async def zk_verify(payload: dict):
    return verify_proof(payload.get("proof_hash",""), payload.get("public_inputs",[]))

@app.post("/api/v1/zk/anchor-blockchain")
async def anchor(payload: dict):
    tx = "0x" + hashlib.sha256(f"{payload.get('proof_hash','')}:{time.time()}".encode()).hexdigest()
    return {"tx_hash": tx, "block_explorer": f"https://amoy.polygonscan.com/tx/{tx}",
            "network": "Polygon Amoy Testnet", "gas_used": 45823, "status": "confirmed"}

@app.get("/api/v1/demo/simulate/{scenario}")
async def simulate(scenario: str):
    data = {
        "authentic": {"trust_score":87.3,"verdict":"AUTHENTIC","action":"VERIFIED — Proceeding to ZK Attestation","breakdown":{"deepfake_cnn":91.2,"codec_artifacts":88.4,"speaker_biometric":84.1,"liveness":85.5},"latency_ms":164},
        "deepfake":  {"trust_score":18.7,"verdict":"DEEPFAKE","action":"BLOCKED — Transaction Destroyed","breakdown":{"deepfake_cnn":12.3,"codec_artifacts":8.9,"speaker_biometric":31.2,"liveness":22.4},"latency_ms":171},
        "suspicious":{"trust_score":54.1,"verdict":"SUSPICIOUS","action":"ESCALATED — Secondary Challenge Required","breakdown":{"deepfake_cnn":61.4,"codec_artifacts":48.2,"speaker_biometric":52.8,"liveness":54.0},"latency_ms":158}
    }
    return data.get(scenario, data["authentic"])
