import os
import sys
import io
import uuid
import logging
import datetime
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv

# 1. ROBUST .ENV LOADING
# Calculate absolute path to .env file in the same directory as this script
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    # Force override any existing environment variables (important for dev)
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    print(f"DEBUG: Successfully loaded .env from {ENV_PATH}")
else:
    print(f"WARNING: .env not found at {ENV_PATH}. Using current environment variables.")

# Verify the read value (masking for security)
google_key = os.getenv("GOOGLE_API_KEY")
if google_key:
    print(f"DEBUG: GOOGLE_API_KEY detected: {google_key[:6]}...{google_key[-4:]}")
else:
    print("DEBUG: GOOGLE_API_KEY not found in environment!")

# ==========================================
# 0. WINDOWS DLL BOOTSTRAP (FIX FOR c10.dll)
# ==========================================
try:
    import torch
    torch_lib_path = os.path.join(os.path.dirname(torch.__file__), "lib")
    if os.path.exists(torch_lib_path):
        if hasattr(os, "add_dll_directory"):
            os.add_dll_directory(torch_lib_path)
        else:
            os.environ["PATH"] = torch_lib_path + os.pathsep + os.environ["PATH"]
except Exception as e:
    print(f"DLL Bootstrap Warning: {e}")

from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from PIL import Image
from sqlalchemy.orm import Session

# Import local modules
from database import engine, get_db, Base
import models as db_models

# 1. AI & Machine Learning Imports (with Resilience)
TORCH_AVAILABLE = False
model = None
model_loaded = False
device = None
transform = None

try:
    import torch.nn as nn
    from torchvision import models, transforms
    TORCH_AVAILABLE = True
    device = torch.device("cpu")
except Exception as e:
    print(f"PyTorch loading failed: {e}. Prediction feature will run in fallback mode.")

# 2. AI Logic Setup (Gemini/Groq/PDF)
try:
    from ai.gemini import generate_explanation
    from ai.groq_chat import chat_with_bot
    from utils.pdf_generator import generate_pdf_report
    from utils.cost_calculator import get_damage_details
except Exception:
    generate_explanation = lambda p, c: "AI explanation currently unavailable."
    chat_with_bot = lambda m, ctx=None: "AI chat currently unavailable."
    generate_pdf_report = None

# Env is already loaded at the top

# ==========================================
# 3. ML MODEL DEFINITION & LOADING
# ==========================================
CLASSES = [
    "F_Breakage", "F_Crushed", "F_Normal", 
    "R_Breakage", "R_Crushed", "R_Normal"
]

if TORCH_AVAILABLE:
    class CarClassifierResNet(nn.Module):
        def __init__(self, num_classes):
            super().__init__()
            self.model = models.resnet50(weights=None)
            self.model.fc = nn.Sequential(
                nn.Dropout(0.2),
                nn.Linear(self.model.fc.in_features, num_classes)
            )
        def forward(self, x): return self.model(x)

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

def load_prediction_model():
    global model, model_loaded
    if not TORCH_AVAILABLE: return
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # Model is in the root directory relative to 'backend'
    MODEL_PATH = os.path.join(os.path.dirname(BASE_DIR), "saved_model.pth")
    
    if not os.path.exists(MODEL_PATH):
        print(f"Warning: {MODEL_PATH} not found. Prediction will fail.")
        return

    try:
        base_model = CarClassifierResNet(num_classes=len(CLASSES))
        state_dict = torch.load(MODEL_PATH, map_location=device)
        if isinstance(state_dict, dict) and ('model_state_dict' in state_dict or 'state_dict' in state_dict):
            state_dict = state_dict.get('state_dict', state_dict.get('model_state_dict'))
        base_model.load_state_dict(state_dict)
        model = base_model.to(device)
        model.eval()
        model_loaded = True
        print(f"SUCCESS: AI Model loaded on {device}")
    except Exception as e:
        print(f"ERROR: Error loading AI model: {e}")

load_prediction_model()

# ==========================================
# 4. DATABASE INITIALIZATION
# ==========================================
try:
    Base.metadata.create_all(bind=engine)
    print("SUCCESS: MySQL Database tables synchronized!")
except Exception as dbe:
    print(f"ERROR: MySQL Initialization Error: {dbe}")

# ==========================================
# 5. FASTAPI SETUP
# ==========================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
if not os.path.exists(REPORTS_DIR): os.makedirs(REPORTS_DIR)

app = FastAPI(title="Car Damage Detection Advanced API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key_123")
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ==========================================
# 6. PYDANTIC SCHEMAS
# ==========================================
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    class Config: from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class HistoryCreate(BaseModel):
    prediction: str
    confidence: float
    explanation: Optional[str] = None
    cost_estimation: Optional[float] = None
    damage_percentage: Optional[int] = None
    image_data: Optional[str] = None

class HistoryResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    prediction: Optional[str] = None
    confidence: Optional[float] = None
    explanation: Optional[str] = None
    damage_percentage: Optional[int] = None
    image_data: Optional[str] = None
    cost: Optional[float] = None
    report_path: Optional[str] = None
    timestamp: Optional[datetime.datetime] = None
    class Config: from_attributes = True

class ExplainRequest(BaseModel):
    prediction: str
    confidence: float

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None

class ReportRequest(BaseModel):
    prediction: str
    confidence: float
    explanation: str
    image_data: Optional[str] = None
    estimated_cost: Optional[float] = None
    recommendations: Optional[str] = None

# ==========================================
# 7. AUTH UTILS
# ==========================================
def create_access_token(user_id: int, email: str):
    expire = datetime.datetime.utcnow() + datetime.timedelta(days=7)
    return jwt.encode({"sub": email, "id": user_id, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        user = db.query(db_models.User).filter(db_models.User.email == email).first()
        if not user: raise HTTPException(status_code=401)
        return user
    except JWTError: raise HTTPException(status_code=401)

# ==========================================
# 8. API ENDPOINTS
# ==========================================

@app.get("/")
def health(): return {"status": "LIVE", "ai_model": "LOADED" if model_loaded else "OFFLINE"}

@app.post("/register", response_model=UserResponse)
def register(req: UserCreate, db: Session = Depends(get_db)):
    if db.query(db_models.User).filter(
        (db_models.User.email == req.email) | (db_models.User.username == req.username)
    ).first():
        raise HTTPException(status_code=400, detail="Email or username already registered")
    
    new_user = db_models.User(
        username=req.username,
        email=req.email,
        hashed_password=pwd_context.hash(req.password),
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(db_models.User).filter(
        (db_models.User.email == form_data.username) | 
        (db_models.User.username == form_data.username)
    ).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_access_token(user.id, user.email), "token_type": "bearer"}

@app.get("/me", response_model=UserResponse)
def get_me(user: db_models.User = Depends(get_current_user)): return user

# --- AI PREDICTION ---
@app.post("/predict")
async def predict(file: UploadFile = File(...), token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = await get_current_user(token, db)
    if not model_loaded: raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI Model not loaded")
    
    try:
        img_bytes = await file.read()
        image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        input_tensor = transform(image).unsqueeze(0).to(device)
        with torch.no_grad():
            output = model(input_tensor)
        probs = torch.nn.functional.softmax(output[0], dim=0)
        conf, idx = torch.max(probs, 0)
        
        prediction_result = CLASSES[idx.item()]
        confidence_val = float(conf.item())
        damage_pct = int(confidence_val * 100)
        est_cost = int(confidence_val * 10000)
        
        try:
            new_pred = db_models.Prediction(
                user_id=user.id,
                input=file.filename or "uploaded_image",
                damage_percentage=damage_pct,
                cost=est_cost,
                prediction_result=prediction_result,
            )
            db.add(new_pred)
            db.commit()
            print(f"SUCCESS: Prediction saved for user {user.id}")
        except Exception as db_err:
            db.rollback()
            print(f"WARNING: DB save failed: {db_err}")
        
        return {"prediction": prediction_result, "confidence": confidence_val}
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail="AI Analysis failed")

# --- AI EXPLAIN & CHAT ---
@app.post("/explain")
def get_explanation(req: ExplainRequest):
    return {"explanation": generate_explanation(req.prediction, req.confidence)}

@app.post("/chat")
def get_chat(req: ChatRequest):
    return {"reply": chat_with_bot(req.message, req.context)}

# --- HISTORY & REPORTS ---
@app.post("/history", response_model=HistoryResponse)
def save_history(req: HistoryCreate, user: db_models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    cost = req.cost_estimation if req.cost_estimation is not None else (req.confidence * 10000)
    
    report_path = None
    try:
        if generate_pdf_report:
            explanation_text = req.explanation or ""
            pdf_buffer = generate_pdf_report(
                req.prediction, req.confidence, explanation_text,
                image_base64=req.image_data, estimated_cost=cost,
                damage_percentage=req.damage_percentage
            )
            report_filename = f"report_{uuid.uuid4().hex[:8]}.pdf"
            relative_path = os.path.join("reports", report_filename)
            full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)
            with open(full_path, "wb") as f:
                f.write(pdf_buffer.getbuffer())
            report_path = relative_path
            print(f"SUCCESS: PDF saved: {report_path}")
    except Exception as pdf_err:
        print(f"WARNING: PDF generation failed: {pdf_err}")

    try:
        new_history = db_models.History(
            user_id=user.id,
            prediction=req.prediction,
            confidence=req.confidence,
            damage_percentage=req.damage_percentage,
            cost=cost,
            explanation=req.explanation,
            image_data=req.image_data,
        )
        db.add(new_history)
        db.commit()
        db.refresh(new_history)
        
        if report_path:
            last_pred = db.query(db_models.Prediction).filter(
                db_models.Prediction.user_id == user.id
            ).order_by(db_models.Prediction.id.desc()).first()
            if last_pred:
                last_pred.report_path = report_path
                last_pred.explanation = req.explanation
                db.commit()
        
        return HistoryResponse(
            id=new_history.id,
            user_id=new_history.user_id,
            prediction=new_history.prediction,
            confidence=new_history.confidence,
            explanation=new_history.explanation,
            cost=cost,
            report_path=report_path,
            timestamp=new_history.timestamp
        )
    except Exception as e:
        logger.error(f"Save history failed: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save results: {str(e)}")

@app.get("/history", response_model=List[HistoryResponse])
def get_history(user: db_models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_history = db.query(db_models.History).filter(
        db_models.History.user_id == user.id
    ).order_by(db_models.History.id.desc()).all()
    
    result_list = []
    for h in db_history:
        # Fallback logic for historical data
        est_damage = h.damage_percentage
        est_cost = h.cost
        
        # Priority 1: If it's a Normal car, it's ALWAYS 0 damage and 0 cost
        if h.prediction and 'normal' in h.prediction.lower():
            est_damage = 0
            est_cost = 0
        # Priority 2: Use professional estimation for missing data in older records
        elif est_damage is None or est_cost is None:
            details = get_damage_details(h.prediction)
            if est_damage is None: est_damage = details["damage"]
            if est_cost is None: est_cost = details["cost"]
            
        result_list.append(HistoryResponse(
            id=h.id,
            user_id=h.user_id,
            prediction=h.prediction,
            confidence=h.confidence,
            damage_percentage=est_damage if est_damage is not None else int(h.confidence * 100),
            explanation=h.explanation,
            image_data=h.image_data,
            cost=est_cost if est_cost is not None else (h.confidence * 10000),
            timestamp=h.timestamp
        ))
    return result_list

@app.delete("/history/{hid}")
def delete_history_item(hid: int, user: db_models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    h = db.query(db_models.History).filter(db_models.History.id == hid, db_models.History.user_id == user.id).first()
    if not h: raise HTTPException(status_code=404, detail="Not found")
    db.delete(h)
    db.commit()
    return {"status": "deleted"}

@app.delete("/history")
def delete_all_history(user: db_models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(db_models.History).filter(db_models.History.user_id == user.id).delete()
    db.commit()
    return {"status": "all history deleted"}

@app.post("/generate-report")
def create_pdf(req: ReportRequest):
    if not generate_pdf_report: raise HTTPException(status_code=503, detail="PDF service unavailable")
    pdf_buffer = generate_pdf_report(
        req.prediction, 
        req.confidence, 
        req.explanation,
        image_base64=req.image_data,
        estimated_cost=req.estimated_cost,
        recommendations=req.recommendations
    )
    return StreamingResponse(pdf_buffer, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=report.pdf"})

@app.get("/download-report/{rid}")
def get_pdf(rid: int, db: Session = Depends(get_db)):
    h = db.query(db_models.History).filter(db_models.History.id == rid).first()
    if not h or not h.report: raise HTTPException(status_code=404, detail="No report found")
    f_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), h.report)
    if not os.path.exists(f_path): raise HTTPException(status_code=404, detail="File lost")
    return FileResponse(f_path, media_type="application/pdf", filename=os.path.basename(f_path))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
