"""
KAVACHA RAKSHA Engine — 3-Model Voice Deepfake Detection.
Bayesian ensemble: EfficientNet-B0 + Codec Detector + ECAPA-TDNN.
"""
import numpy as np
import torch
import torchaudio
import torchaudio.transforms as T
import torchvision.transforms as tv_transforms
import librosa
import io, base64, time, hashlib
from PIL import Image
from scipy.spatial.distance import cosine

SAMPLE_RATE = 16000
MEL_BINS = 128
MEL_SIZE = (128, 128)
W_CNN, W_CODEC, W_BIO, W_LIVENESS = 0.35, 0.25, 0.20, 0.20
THRESHOLD_BLOCK, THRESHOLD_SUSPICIOUS = 40, 70
VOICE_PASSPORTS: dict = {}

def decode_audio_b64(audio_b64: str) -> np.ndarray:
    audio_bytes = base64.b64decode(audio_b64)
    waveform, sr = torchaudio.load(io.BytesIO(audio_bytes))
    if sr != SAMPLE_RATE:
        waveform = T.Resample(sr, SAMPLE_RATE)(waveform)
    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)
    return waveform.squeeze().numpy()

def compute_mel(audio: np.ndarray) -> np.ndarray:
    mel = librosa.feature.melspectrogram(
        y=audio, sr=SAMPLE_RATE, n_mels=MEL_BINS, fmax=8000, hop_length=256, n_fft=2048
    )
    mel_db = librosa.power_to_db(mel, ref=np.max)
    img = Image.fromarray(((mel_db + 80) / 80 * 255).astype(np.uint8))
    return np.array(img.resize(MEL_SIZE))

def score_cnn(mel: np.ndarray, model) -> float:
    tf = tv_transforms.Compose([
        tv_transforms.ToTensor(),
        tv_transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
    ])
    img_rgb = np.stack([mel, mel, mel], axis=-1)
    tensor = tf(img_rgb).unsqueeze(0).float()
    with torch.no_grad():
        probs = torch.softmax(model(tensor), dim=1)
    return probs[0][0].item() * 100

def score_codec(audio: np.ndarray) -> float:
    fft = np.fft.rfft(audio)
    mags = np.abs(fft)
    freqs = np.fft.rfftfreq(len(audio), 1/SAMPLE_RATE)
    def band(lo, hi):
        mask = (freqs >= lo) & (freqs < hi)
        return np.mean(mags[mask]) if mask.any() else 0
    base = band(500, 2000)
    if base < 1e-6:
        return 50.0
    ratio1 = band(3000,5000) / (base + 1e-9)
    ratio2 = band(7000,9000) / (base + 1e-9)
    rms = librosa.feature.rms(y=audio, frame_length=512, hop_length=160)[0]
    var_score = min(100, np.var(rms) * 50000)
    zcr_var = np.var(librosa.feature.zero_crossing_rate(audio)[0]) * 10000
    penalty = min(60, (ratio1 + ratio2) * 15)
    return float(max(0, min(100, 60 + var_score*0.2 + zcr_var*0.1 - penalty)))

def enroll_voice(user_id: str, audio: np.ndarray, model) -> str:
    waveform = torch.tensor(audio).unsqueeze(0)
    with torch.no_grad():
        emb = model.encode_batch(waveform).squeeze().numpy()
    VOICE_PASSPORTS[user_id] = emb
    return hashlib.sha256(emb.tobytes()).hexdigest()

def score_biometric(user_id: str, audio: np.ndarray, model) -> float:
    if user_id not in VOICE_PASSPORTS:
        return 50.0
    waveform = torch.tensor(audio).unsqueeze(0)
    with torch.no_grad():
        live = model.encode_batch(waveform).squeeze().numpy()
    sim = 1 - cosine(live, VOICE_PASSPORTS[user_id])
    return max(0, min(100, sim * 100))

def compute_verdict(cnn, codec, bio, liveness=75.0) -> dict:
    score = W_CNN*cnn + W_CODEC*codec + W_BIO*bio + W_LIVENESS*liveness
    if score < THRESHOLD_BLOCK:
        verdict, action, color = "DEEPFAKE", "BLOCKED — Transaction Destroyed", "#FF0040"
    elif score < THRESHOLD_SUSPICIOUS:
        verdict, action, color = "SUSPICIOUS", "ESCALATED — Secondary Challenge", "#FF8C00"
    else:
        verdict, action, color = "AUTHENTIC", "VERIFIED — Proceed to ZK Layer", "#00FF88"
    return {
        "trust_score": round(score, 2), "verdict": verdict,
        "action": action, "color": color,
        "breakdown": {"deepfake_cnn": round(cnn,2), "codec_artifacts": round(codec,2),
                      "speaker_biometric": round(bio,2), "liveness": round(liveness,2)}
    }

def analyze_chunk(audio_b64: str, user_id: str, models: dict, session_id: str = "demo") -> dict:
    t0 = time.time()
    audio = decode_audio_b64(audio_b64)
    mel = compute_mel(audio)
    result = compute_verdict(
        score_cnn(mel, models["deepfake_clf"]),
        score_codec(audio),
        score_biometric(user_id, audio, models["ecapa"])
    )
    result["latency_ms"] = int((time.time() - t0) * 1000)
    result["session_id"] = session_id
    result["spectrogram_data"] = mel.tolist()
    return result
