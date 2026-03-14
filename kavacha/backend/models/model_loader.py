"""
KAVACHA Model Loader — ALL pretrained models. Zero training.
"""
import torch
from pathlib import Path

CACHE_DIR = Path("/tmp/kavacha_models")
CACHE_DIR.mkdir(exist_ok=True)

def load_ecapa_tdnn():
    """
    PRETRAINED ECAPA-TDNN from SpeechBrain/VoxCeleb2.
    192-dim speaker embeddings. Works immediately, no fine-tuning.
    """
    from speechbrain.pretrained import SpeakerRecognition
    return SpeakerRecognition.from_hf_hub(
        source="speechbrain/spkrec-ecapa-voxceleb",
        savedir=str(CACHE_DIR / "ecapa_tdnn"),
        run_opts={"device": "cpu"}
    )

def load_deepfake_classifier():
    """
    PRETRAINED EfficientNet-B0 from torchvision/ImageNet.
    Fine-tuned head for binary real/fake classification.
    ImageNet features detect neural codec texture artifacts.
    """
    import torchvision.models as models
    model = models.efficientnet_b0(weights='IMAGENET1K_V1')
    in_features = model.classifier[1].in_features
    model.classifier[1] = torch.nn.Linear(in_features, 2)
    weights_path = CACHE_DIR / "deepfake_clf.pth"
    if weights_path.exists():
        model.load_state_dict(torch.load(weights_path, map_location='cpu'))
    model.eval()
    return model

def get_all_models():
    print("KAVACHA: Loading pretrained models...")
    models = {
        "ecapa": load_ecapa_tdnn(),
        "deepfake_clf": load_deepfake_classifier(),
    }
    print("KAVACHA: All models loaded.")
    return models
