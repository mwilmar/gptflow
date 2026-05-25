import os
import uuid
import json
from datetime import datetime, timedelta, timezone
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, DateTime, Boolean, Integer, JSON, select, update
from jose import jwt, JWTError
from openai import AsyncOpenAI
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


# === CONFIG ===
class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://gptflow:gptflow123@localhost:5432/gptflow"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "dev-secret-key"
    jwt_expire_minutes: int = 60 * 24  # 24h for dev
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    ai_provider: str = "groq"  # "groq", "openai", or "hybrid"
    ig_app_id: str = ""
    ig_app_secret: str = ""
    unsplash_access_key: str = ""
    debug: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()


# === DATABASE ===
engine = create_async_engine(settings.database_url, echo=settings.debug)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(20), default="creator")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    groq_api_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    openai_api_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ig_app_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ig_app_secret: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ig_access_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Content(Base):
    __tablename__ = "contents"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    creator_id: Mapped[str] = mapped_column(String(36), index=True)
    content_type: Mapped[str] = mapped_column(String(20))  # feed, carousel, reels, story
    status: Mapped[str] = mapped_column(String(30), default="draft")
    topic: Mapped[str] = mapped_column(String(500))
    audience: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    tone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    hook: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cta: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    caption: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hashtags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    slides: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    reels_script: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    approved_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    reject_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# === AUTH ===
import bcrypt as _bcrypt
security = HTTPBearer()

def hash_password(password: str) -> str:
    return _bcrypt.hashpw(password.encode(), _bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return _bcrypt.checkpw(plain.encode(), hashed.encode())

def create_token(user_id: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    return jwt.encode({"sub": user_id, "role": role, "exp": expire}, settings.jwt_secret, algorithm="HS256")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=["HS256"])
        return {"id": payload["sub"], "role": payload["role"]}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_db():
    async with SessionLocal() as session:
        yield session


# === SCHEMAS ===
class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str

class LoginRequest(BaseModel):
    email: str
    password: str

class GenerateRequest(BaseModel):
    topic: str
    audience: str = "Umum"
    tone: str = "casual_edukatif"
    content_type: str = "feed"  # feed, carousel, reels, story
    additional_context: str = ""

class ScheduleRequest(BaseModel):
    content_id: str
    scheduled_at: str  # ISO format

class ApprovalRequest(BaseModel):
    notes: str = ""


# === AI GENERATION ===
from groq import AsyncGroq

openai_client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
groq_client = AsyncGroq(api_key=settings.groq_api_key) if settings.groq_api_key else None

SYSTEM_PROMPTS = {
    "feed": """Kamu content strategist Instagram edukasi. Buat caption Instagram.
Output JSON: {"hook":"...","body":"...","cta":"...","caption":"hook+body+cta gabungan","hashtags":["#tag1",...]}
Aturan: Bahasa Indonesia, engaging, edukatif, max 300 kata, 15-20 hashtag.""",

    "carousel": """Kamu content designer Instagram carousel edukasi.
Output JSON: {"hook":"...","slides":[{"number":1,"heading":"...","body":"..."}],"cta":"...","caption":"...","hashtags":["#tag1",...]}
Aturan: 5-8 slides, max 40 kata/slide, slide 1=cover hook, slide terakhir=CTA.""",

    "reels": """Kamu scriptwriter Instagram Reels edukasi.
Output JSON: {"hook":{"text":"...","duration":"3s"},"scenes":[{"text":"...","visual":"...","duration":"10s"}],"cta":{"text":"...","duration":"5s"},"caption":"...","hashtags":["#tag1",...]}
Aturan: Total 30-60 detik, hook 3 detik pertama, energetic.""",

    "story": """Kamu social media manager. Buat konten Instagram Story.
Output JSON: {"frames":[{"type":"text/poll/quiz","content":"..."}],"caption":"...","hashtags":["#tag1",...]}
Aturan: 2-4 frames, interactive (poll/quiz), casual."""
}

async def generate_content(req: GenerateRequest) -> dict:
    system = SYSTEM_PROMPTS[req.content_type]
    user_msg = f"Topik: {req.topic}\nAudiens: {req.audience}\nTone: {req.tone}"
    if req.additional_context:
        user_msg += f"\nKonteks: {req.additional_context}"

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_msg}
    ]

    # Hybrid: try Groq first (fast+free), fallback to OpenAI
    result = None
    if settings.ai_provider in ("groq", "hybrid") and groq_client:
        try:
            response = await groq_client.chat.completions.create(
                model=settings.groq_model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=1500,
            )
            result = json.loads(response.choices[0].message.content)
        except Exception:
            if settings.ai_provider == "groq":
                raise
            # hybrid mode: fall through to OpenAI

    if result is None and openai_client:
        response = await openai_client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=1500,
        )
        result = json.loads(response.choices[0].message.content)

    if result is None:
        raise HTTPException(500, "No AI provider available")

    return result


# === APP ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="GPTFlow", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")


# === ROUTES: Pages ===
@app.get("/")
async def index():
    return FileResponse("static/index.html")


# === ROUTES: Image Search (Unsplash) ===
import httpx

@app.get("/api/images/search")
async def search_images(query: str, count: int = 3, user: dict = Depends(get_current_user)):
    if not settings.unsplash_access_key:
        raise HTTPException(500, "Unsplash API key not configured")
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.unsplash.com/search/photos",
            params={"query": query, "per_page": count, "orientation": "squarish"},
            headers={"Authorization": f"Client-ID {settings.unsplash_access_key}"}
        )
    data = resp.json()
    images = [{"id": r["id"], "url": r["urls"]["regular"], "thumb": r["urls"]["small"], "alt": r.get("alt_description", "")} for r in data.get("results", [])]
    return {"data": images}


# === ROUTES: Auth ===
@app.post("/api/auth/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == req.email))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Email already registered")
    user = User(email=req.email, password_hash=hash_password(req.password), name=req.name)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_token(user.id, user.role)
    return {"data": {"token": token, "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role}}}

@app.post("/api/auth/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    token = create_token(user.id, user.role)
    return {"data": {"token": token, "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role}}}


# === ROUTES: Settings ===
@app.get("/api/settings")
async def get_settings(user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user["id"]))
    u = result.scalar_one()
    def mask(v):
        if not v or len(v) < 8: return ""
        return v[:4] + "••••" + v[-4:]
    return {"data": {"groq_api_key": mask(u.groq_api_key), "openai_api_key": mask(u.openai_api_key), "ig_app_id": mask(u.ig_app_id), "ig_app_secret": mask(u.ig_app_secret), "ig_access_token": mask(u.ig_access_token)}}

@app.get("/api/settings/verify")
async def verify_settings(user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user["id"]))
    u = result.scalar_one()
    groq_ok, openai_ok, ig_ok = False, False, False
    # Verify Groq
    key = u.groq_api_key or settings.groq_api_key
    if key:
        try:
            async with httpx.AsyncClient() as c:
                r = await c.get("https://api.groq.com/openai/v1/models", headers={"Authorization": f"Bearer {key}"}, timeout=5.0)
                groq_ok = r.status_code == 200
        except: pass
    # Verify OpenAI
    key = u.openai_api_key or settings.openai_api_key
    if key:
        try:
            async with httpx.AsyncClient() as c:
                r = await c.get("https://api.openai.com/v1/models", headers={"Authorization": f"Bearer {key}"}, timeout=5.0)
                openai_ok = r.status_code == 200
        except: pass
    # Verify IG
    if u.ig_access_token:
        try:
            async with httpx.AsyncClient() as c:
                r = await c.get(f"https://graph.instagram.com/me?access_token={u.ig_access_token}", timeout=5.0)
                ig_ok = r.status_code == 200
        except: pass
    return {"data": {"groq": groq_ok, "openai": openai_ok, "ig": ig_ok}}

@app.put("/api/settings")
async def update_settings(request: Request, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    body = await request.json()
    result = await db.execute(select(User).where(User.id == user["id"]))
    u = result.scalar_one()
    if "groq_api_key" in body: u.groq_api_key = body["groq_api_key"]
    if "openai_api_key" in body: u.openai_api_key = body["openai_api_key"]
    if "ig_app_id" in body: u.ig_app_id = body["ig_app_id"]
    if "ig_app_secret" in body: u.ig_app_secret = body["ig_app_secret"]
    if "ig_access_token" in body: u.ig_access_token = body["ig_access_token"]
    await db.commit()
    return {"data": "ok"}

# === ROUTES: AI Image Generation ===
@app.get("/api/unsplash/search")
async def unsplash_search(q: str, user: dict = Depends(get_current_user)):
    if not settings.unsplash_access_key:
        return {"data": []}
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://api.unsplash.com/search/photos?query={q}&per_page=9&client_id={settings.unsplash_access_key}", timeout=10.0)
        data = resp.json()
        results = [{"thumb": r["urls"]["thumb"], "url": r["urls"]["regular"]} for r in data.get("results", [])[:9]]
        return {"data": results}

@app.post("/api/generate-image")
async def generate_image(request: Request, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    body = await request.json()
    prompt = body.get("prompt", "")
    if not prompt:
        raise HTTPException(400, "Prompt required")
    # Get user's OpenAI key or fallback to system key
    result = await db.execute(select(User).where(User.id == user["id"]))
    u = result.scalar_one()
    api_key = u.openai_api_key or settings.openai_api_key
    if not api_key:
        raise HTTPException(400, "OpenAI API key belum diset. Buka menu ⚙️ Config untuk mengisi API key.")
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=api_key)
        resp = await client.images.generate(model="gpt-image-1", prompt=prompt, size="1024x1024", n=1, quality="low")
        if resp.data[0].url:
            return {"data": {"url": resp.data[0].url}}
        elif resp.data[0].b64_json:
            return {"data": {"url": f"data:image/png;base64,{resp.data[0].b64_json}"}}
        else:
            raise HTTPException(500, "No image returned")
    except Exception as e:
        err_msg = str(e)
        if "billing" in err_msg.lower() or "quota" in err_msg.lower() or "insufficient" in err_msg.lower():
            raise HTTPException(402, "OpenAI quota habis. Silakan top-up di https://platform.openai.com/account/billing")
        raise HTTPException(500, f"Gagal generate gambar: {err_msg}")

# === ROUTES: User Management ===
@app.get("/api/users")
async def list_users(user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if user["role"] not in ("admin", "manager"):
        raise HTTPException(403, "Only admin/manager can view users")
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return {"data": [{"id": u.id, "email": u.email, "name": u.name, "role": u.role, "is_active": u.is_active} for u in result.scalars().all()]}

class RoleUpdate(BaseModel):
    role: str

@app.put("/api/users/{user_id}/role")
async def update_user_role(user_id: str, req: RoleUpdate, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if user["role"] != "admin":
        raise HTTPException(403, "Only admin can change roles")
    if req.role not in ("creator", "manager", "admin"):
        raise HTTPException(400, "Invalid role")
    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(404, "User not found")
    target.role = req.role
    await db.commit()
    return {"data": {"id": target.id, "role": target.role}}

# === ROUTES: Content Generation ===
@app.post("/api/suggest/{field}")
async def suggest_field(field: str, request: Request, user: dict = Depends(get_current_user)):
    body = await request.json()
    topic = body.get("topic", "")
    audience = body.get("audience", "")
    tone = body.get("tone", "")
    content_type = body.get("content_type", "")
    ctx = body.get("context", "")

    filled = []
    if topic: filled.append(f"Topik: {topic}")
    if audience: filled.append(f"Audiens: {audience}")
    if tone: filled.append(f"Gaya: {tone}")
    if content_type: filled.append(f"Tipe: {content_type}")
    if ctx: filled.append(f"Konteks: {ctx}")
    context_str = "\n".join(filled) if filled else "Belum ada field yang diisi"

    prompts = {
        "topic": f"Berdasarkan konteks berikut:\n{context_str}\n\nBerikan 5 ide topik konten Instagram yang relevan dan engaging. Format: satu topik per baris, tanpa numbering, tanpa penjelasan.",
        "audience": f"Berdasarkan konteks berikut:\n{context_str}\n\nBerikan 5 pilihan target audiens yang spesifik dan relevan. Format: satu audiens per baris, tanpa numbering.",
        "context": f"Berdasarkan konteks berikut:\n{context_str}\n\nBerikan 5 instruksi/konteks tambahan yang bisa memperkaya konten ini. Format: satu konteks per baris, tanpa numbering.",
    }
    if field not in prompts:
        raise HTTPException(400, "Invalid field")
    messages = [{"role": "user", "content": prompts[field]}]
    try:
        if groq_client:
            resp = await groq_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=messages, temperature=0.8, max_tokens=200)
            text = resp.choices[0].message.content
        elif openai_client:
            resp = await openai_client.chat.completions.create(model="gpt-4o-mini", messages=messages, temperature=0.8, max_tokens=200)
            text = resp.choices[0].message.content
        else:
            text = ""
        suggestions = [s.strip().lstrip('•-123456789. ') for s in text.strip().split('\n') if s.strip()][:5]
        return {"data": suggestions}
    except Exception:
        return {"data": []}
@app.post("/api/suggest-manual/{field}")
async def suggest_manual_field(field: str, request: Request, user: dict = Depends(get_current_user)):
    body = await request.json()
    topic = body.get("topic", "")
    content_type = body.get("content_type", "feed")
    caption = body.get("caption", "")
    ctx = f"Tipe: {content_type}"
    if topic: ctx += f", Topik: {topic}"
    if caption: ctx += f", Caption: {caption[:100]}"

    prompts = {
        "topic": f"Konteks: {ctx}\nBerikan 5 ide topik/judul untuk konten Instagram {content_type}. Satu per baris, tanpa numbering.",
        "caption": f"Konteks: {ctx}\nBerikan 3 variasi caption Instagram yang engaging. Satu per baris, tanpa numbering.",
        "hashtags": f"Konteks: {ctx}\nBerikan 5 set hashtag (masing-masing 5-7 hashtag) yang relevan. Satu set per baris.",
        "cta": f"Konteks: {ctx}\nBerikan 5 CTA (call to action) yang engaging untuk Instagram. Satu per baris, tanpa numbering.",
        "hook": f"Konteks: {ctx}\nBerikan 5 hook/kalimat pembuka yang menarik untuk reels (3 detik pertama). Satu per baris.",
        "script": f"Konteks: {ctx}\nBerikan 3 variasi script pendek (30-60 detik) untuk reels. Satu per baris.",
        "visual": f"Konteks: {ctx}\nBerikan 5 ide visual direction/transisi untuk reels. Satu per baris.",
        "interaction": f"Konteks: {ctx}\nBerikan 5 ide poll/quiz/question untuk Instagram Story. Satu per baris.",
    }
    if field not in prompts:
        raise HTTPException(400, "Invalid field")
    messages = [{"role": "user", "content": prompts[field]}]
    try:
        if groq_client:
            resp = await groq_client.chat.completions.create(model="llama-3.3-70b-versatile", messages=messages, temperature=0.8, max_tokens=300)
            text = resp.choices[0].message.content
        elif openai_client:
            resp = await openai_client.chat.completions.create(model="gpt-4o-mini", messages=messages, temperature=0.8, max_tokens=300)
            text = resp.choices[0].message.content
        else:
            text = ""
        suggestions = [s.strip().lstrip('•-123456789. ') for s in text.strip().split('\n') if s.strip()][:5]
        return {"data": suggestions}
    except Exception:
        return {"data": []}

@app.post("/api/content/manual")
async def create_manual_content(request: Request, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    body = await request.json()
    content = Content(
        creator_id=user["id"],
        content_type=body.get("content_type", "feed"),
        topic=body.get("topic", ""),
        body=body.get("body", ""),
        image_url=body.get("image_url", None),
        status="draft",
    )
    db.add(content)
    await db.commit()
    await db.refresh(content)
    return {"data": _content_to_dict(content)}

@app.post("/api/content/generate")
async def api_generate(req: GenerateRequest, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await generate_content(req)
    content = Content(
        creator_id=user["id"],
        content_type=req.content_type,
        topic=req.topic,
        audience=req.audience,
        tone=req.tone,
        hook=result.get("hook", "") if isinstance(result.get("hook"), str) else result.get("hook", {}).get("text", "") if isinstance(result.get("hook"), dict) else "",
        body=result.get("body", ""),
        cta=result.get("cta", "") if isinstance(result.get("cta"), str) else result.get("cta", {}).get("text", "") if isinstance(result.get("cta"), dict) else "",
        caption=result.get("caption", ""),
        hashtags=json.dumps(result.get("hashtags", [])),
        slides=json.dumps(result.get("slides")) if result.get("slides") else None,
        reels_script=json.dumps({"hook": result.get("hook"), "scenes": result.get("scenes"), "cta": result.get("cta")}) if req.content_type == "reels" else None,
    )
    db.add(content)
    await db.commit()
    await db.refresh(content)
    return {"data": _content_to_dict(content)}


# === ROUTES: Content CRUD ===
@app.get("/api/content")
async def list_content(status: Optional[str] = None, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if user["role"] in ("admin", "manager"):
        q = select(Content).order_by(Content.created_at.desc())
    else:
        q = select(Content).where(Content.creator_id == user["id"]).order_by(Content.created_at.desc())
    if status:
        q = q.where(Content.status == status)
    result = await db.execute(q)
    contents = result.scalars().all()
    return {"data": [_content_to_dict(c) for c in contents]}

@app.get("/api/content/{content_id}")
async def get_content(content_id: str, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    content = await _get_content(content_id, db)
    return {"data": _content_to_dict(content)}

@app.delete("/api/content/{content_id}")
async def delete_content(content_id: str, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    content = await _get_content(content_id, db)
    if content.creator_id != user["id"] and user["role"] != "admin":
        raise HTTPException(403, "Not authorized")
    await db.delete(content)
    await db.commit()
    return {"data": {"deleted": True}}


class SetImageRequest(BaseModel):
    image_url: str

@app.put("/api/content/{content_id}/image")
async def set_content_image(content_id: str, req: SetImageRequest, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    content = await _get_content(content_id, db)
    content.image_url = req.image_url
    await db.commit()
    return {"data": _content_to_dict(content)}


from fastapi import UploadFile, File
import shutil

@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    os.makedirs("static/uploads", exist_ok=True)
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    filepath = f"static/uploads/{filename}"
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"data": {"url": f"/static/uploads/{filename}"}}


# === ROUTES: Approval ===
@app.post("/api/content/{content_id}/submit")
async def submit_for_approval(content_id: str, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    content = await _get_content(content_id, db)
    if content.status not in ("draft", "rejected"):
        raise HTTPException(400, "Can only submit draft or rejected content")
    content.status = "pending_approval"
    await db.commit()
    return {"data": _content_to_dict(content)}

@app.post("/api/content/{content_id}/approve")
async def approve_content(content_id: str, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if user["role"] not in ("admin", "manager"):
        raise HTTPException(403, "Only manager/admin can approve")
    content = await _get_content(content_id, db)
    if content.status != "pending_approval":
        raise HTTPException(400, "Content not pending approval")
    content.status = "approved"
    content.approved_by = user["id"]
    content.approved_at = datetime.utcnow()
    await db.commit()
    return {"data": _content_to_dict(content)}

@app.post("/api/content/{content_id}/reject")
async def reject_content(content_id: str, req: ApprovalRequest, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if user["role"] not in ("admin", "manager"):
        raise HTTPException(403, "Only manager/admin can reject")
    content = await _get_content(content_id, db)
    if content.status != "pending_approval":
        raise HTTPException(400, "Content not pending approval")
    content.status = "rejected"
    content.reject_notes = req.notes
    await db.commit()
    return {"data": _content_to_dict(content)}


# === ROUTES: Schedule ===
@app.post("/api/content/{content_id}/schedule")
async def schedule_content(content_id: str, req: ScheduleRequest, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    content = await _get_content(content_id, db)
    if content.status != "approved":
        raise HTTPException(400, "Only approved content can be scheduled")
    content.status = "scheduled"
    content.scheduled_at = datetime.fromisoformat(req.scheduled_at)
    await db.commit()
    return {"data": _content_to_dict(content)}

@app.get("/api/schedule")
async def list_scheduled(user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Content).where(Content.status == "scheduled").order_by(Content.scheduled_at)
    )
    return {"data": [_content_to_dict(c) for c in result.scalars().all()]}

@app.get("/api/schedule/calendar")
async def calendar_view(month: int = None, year: int = None, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    now = datetime.utcnow()
    m = month or now.month
    y = year or now.year
    start = datetime(y, m, 1)
    end = datetime(y, m + 1, 1) if m < 12 else datetime(y + 1, 1, 1)
    result = await db.execute(
        select(Content).where(
            Content.scheduled_at >= start,
            Content.scheduled_at < end,
            Content.status.in_(["scheduled", "posted"])
        ).order_by(Content.scheduled_at)
    )
    return {"data": [_content_to_dict(c) for c in result.scalars().all()]}


# === ROUTES: Dashboard Stats ===
@app.get("/api/dashboard")
async def dashboard(user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    from sqlalchemy import func
    total = (await db.execute(select(func.count(Content.id)))).scalar() or 0
    drafts = (await db.execute(select(func.count(Content.id)).where(Content.status == "draft"))).scalar() or 0
    pending = (await db.execute(select(func.count(Content.id)).where(Content.status == "pending_approval"))).scalar() or 0
    approved = (await db.execute(select(func.count(Content.id)).where(Content.status == "approved"))).scalar() or 0
    scheduled = (await db.execute(select(func.count(Content.id)).where(Content.status == "scheduled"))).scalar() or 0
    return {"data": {"total": total, "drafts": drafts, "pending_approval": pending, "approved": approved, "scheduled": scheduled, "ig_connected": bool(settings.ig_app_id)}}


# === HELPERS ===
async def _get_content(content_id: str, db: AsyncSession) -> Content:
    result = await db.execute(select(Content).where(Content.id == content_id))
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(404, "Content not found")
    return content

def _content_to_dict(c: Content) -> dict:
    return {
        "id": c.id, "content_type": c.content_type, "status": c.status,
        "topic": c.topic, "audience": c.audience, "tone": c.tone,
        "hook": c.hook, "body": c.body, "cta": c.cta, "caption": c.caption,
        "hashtags": json.loads(c.hashtags) if c.hashtags else [],
        "slides": json.loads(c.slides) if c.slides else None,
        "reels_script": json.loads(c.reels_script) if c.reels_script else None,
        "image_url": c.image_url,
        "scheduled_at": c.scheduled_at.isoformat() if c.scheduled_at else None,
        "approved_by": c.approved_by, "reject_notes": c.reject_notes,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }
