# backend/config.py
import os
import torch
from dotenv import load_dotenv

# Tải các biến môi trường từ file .env
load_dotenv()

# Cấu hình chung 
MODELS_DIR = os.getenv("MODELS_DIR", "models")
WEIGHTS_FILENAME = "resnet50_proj512_best.pt"
WEIGHTS_PATH = os.path.join(MODELS_DIR, WEIGHTS_FILENAME)
WEIGHTS_GDRIVE_ID = "1eUhNvt3r6I1oPJ58fDjH6LLBG4UdeiaJ"

# Cấu hình DeepLearning Model AI 
EMBED_DIM = 512
AUTO_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DEVICE = os.getenv("DEVICE", AUTO_DEVICE)

# Cấu hình MongoDB Atlas 
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "Polyvore_outfits")

if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in the environment variables. Please create a .env file.")

# Collection in MongoDB
METADATA_COLLECTION = "Metadata"
IMAGES_COLLECTION = "Images"
EMBEDDINGS_COLLECTION = "Embeddings_Feature1"
OUTFIT_MAPPING_COLLECTION = "Outfit_mapping_Feature2"

# Cấu hình CORS 
ORIGINS = ["http://localhost:3000", "https://yame-clone-animated.vercel.app"]