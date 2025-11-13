# backend/ml_model.py
import os
import gdown
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional
from PIL import Image
from fastapi import HTTPException
import torchvision.transforms as T
from torchvision import models

from . import config

# Biến global để giữ model đã được tải
_model: Optional[nn.Module] = None

# Định nghĩa class model
class FineTuneModel(nn.Module):
    def __init__(self, out_dim=config.EMBED_DIM):
        super().__init__()
        resnet = models.resnet50(weights=None)
        self.backbone = nn.Sequential(*list(resnet.children())[:-1])
        self.proj = nn.Linear(2048, out_dim)
    
    def forward(self, x):
        x = self.backbone(x).view(x.size(0), -1)
        return F.normalize(self.proj(x), p=2, dim=1)

# Hàm để tải model
def load_model():
    """Tải và khởi tạo model AI, trả về instance của model."""
    global _model
    
    model_dir = os.path.dirname(config.WEIGHTS_PATH)
    if not os.path.exists(model_dir):
        os.makedirs(model_dir, exist_ok=True)
    
    if not os.path.exists(config.WEIGHTS_PATH):
        print(f"Downloading model weights: {config.WEIGHTS_PATH}")
        gdown.download(url=f'https://drive.google.com/uc?id={config.WEIGHTS_GDRIVE_ID}', output=config.WEIGHTS_PATH, quiet=False)
    
    try:
        model_instance = FineTuneModel(out_dim=config.EMBED_DIM).to(config.DEVICE).eval()
        ckpt = torch.load(config.WEIGHTS_PATH, map_location=config.DEVICE)
        state = ckpt.get("state_dict", ckpt)
        filtered = {k: v for k, v in state.items() if k.startswith(("backbone.", "proj."))}
        model_instance.load_state_dict(filtered, strict=False)
        _model = model_instance
        print("--- Model loaded successfully. ---")
    except Exception as e:
        print(f"--- Failed to load model weights: {e} ---")
        _model = None
        raise

# Preprocess ảnh đầu vào
preprocess = T.Compose([T.Resize((224, 224)), T.ToTensor(), T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])

# Image to vector embedding
@torch.inference_mode()
def image_to_vec(img: Image.Image) -> list:
    if not _model:
        raise HTTPException(503, "Image search disabled: model not loaded.")
    img_rgb = img.convert("RGB")
    x = preprocess(img_rgb).unsqueeze(0).to(config.DEVICE)
    return _model(x)[0].cpu().numpy().tolist()

# Get model instance
def get_model() -> nn.Module:
    if _model is None:
        raise RuntimeError("Model has not been loaded.")
    return _model