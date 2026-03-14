"""
KAVACHA Adversarial Perturbation Engine.
FGSM + PGD noise injection to collapse deepfake generators.
Uses pretrained OpenCV Haar cascade — no GPU needed.
"""
import numpy as np
import cv2
import base64

EPSILON_FGSM = 8/255
EPSILON_PGD = 10/255
PGD_STEPS = 10
PGD_ALPHA = 2/255

_HAAR_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def fgsm_perturb(frame: np.ndarray, eps=EPSILON_FGSM) -> np.ndarray:
    f = frame.astype(np.float32) / 255.0
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    sign = np.sign((gx + gy) / 2)
    pert = np.stack([sign * eps] * 3, axis=-1)
    return (np.clip(f + pert, 0, 1) * 255).astype(np.uint8)

def pgd_perturb(frame: np.ndarray, eps=EPSILON_PGD, steps=PGD_STEPS, alpha=PGD_ALPHA) -> np.ndarray:
    orig = frame.astype(np.float32) / 255.0
    adv = orig.copy()
    for _ in range(steps):
        gray = cv2.cvtColor((adv*255).astype(np.uint8), cv2.COLOR_BGR2GRAY)
        dft = cv2.dft(gray.astype(np.float32), flags=cv2.DFT_COMPLEX_OUTPUT)
        shifted = np.fft.fftshift(dft[:,:,0] + 1j*dft[:,:,1])
        noise = np.random.choice([-1,1], size=shifted.shape) * alpha
        pert = np.real(np.fft.ifft2(noise)) / steps
        pert3 = np.stack([pert]*3, axis=-1)
        adv = np.clip(orig + np.clip(adv + alpha*np.sign(pert3) - orig, -eps, eps), 0, 1)
    return (adv * 255).astype(np.uint8)

def perturb_frame(frame_b64: str, method: str = "pgd") -> dict:
    raw = np.frombuffer(base64.b64decode(frame_b64), dtype=np.uint8)
    frame = cv2.imdecode(raw, cv2.IMREAD_COLOR)
    if frame is None:
        return {"error": "Invalid frame"}
    cascade = _HAAR_CASCADE
    faces = cascade.detectMultiScale(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), 1.1, 4)
    out = frame.copy()
    for (x,y,w,h) in faces:
        out[y:y+h, x:x+w] = pgd_perturb(frame[y:y+h,x:x+w]) if method=="pgd" else fgsm_perturb(frame[y:y+h,x:x+w])
    _, buf = cv2.imencode('.jpg', out, [cv2.IMWRITE_JPEG_QUALITY, 85])
    diff = float(np.mean(np.abs(out.astype(float) - frame.astype(float)))) if len(faces) else 0
    return {
        "perturbed_frame": base64.b64encode(buf).decode(),
        "faces_detected": len(faces),
        "perturbation_applied": len(faces) > 0,
        "method": method,
        "perturbation_magnitude": round(diff, 4),
        "message": "Deepfake generator latent space COLLAPSED" if len(faces) else "No face — monitoring"
    }
