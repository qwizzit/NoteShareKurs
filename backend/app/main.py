import json
import random
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mail import ConnectionConfig, MessageSchema, FastMail, MessageType
from sqlalchemy.orm import Session
from .database import engine
from . import models, schemas, database
from .models import note_tags, Note
from .schemas import TokenConfirmSchema
from .utils import hash_password, verify_password
from .config import settings
from fastapi import HTTPException, status
import httpx

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conf = ConnectionConfig(
    MAIL_USERNAME = settings.mail_username,
    MAIL_PASSWORD = settings.mail_password,
    MAIL_FROM = settings.mail_from,
    MAIL_PORT = settings.mail_port,
    MAIL_SERVER = settings.mail_server,

    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = True,

    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, note_id: int):
        await websocket.accept()
        if note_id not in self.active_connections:
            self.active_connections[note_id] = []
        self.active_connections[note_id].append(websocket)

    def disconnect(self, websocket: WebSocket, note_id: int):
        if note_id in self.active_connections:
            self.active_connections[note_id].remove(websocket)
            if not self.active_connections[note_id]:
                del self.active_connections[note_id]

    async def broadcast(self, message: str, note_id: int, sender: WebSocket):
        if note_id in self.active_connections:
            for connection in self.active_connections[note_id]:
                if connection != sender:
                    try:
                        await connection.send_text(message)
                    except Exception:
                        pass

manager = ConnectionManager()

@app.websocket("/ws/notes/{note_id}")
async def websocket_endpoint(websocket: WebSocket, note_id: int):
    await manager.connect(websocket, note_id)
    try:
        while True:
            raw_data = await websocket.receive_text()

            try:
                incoming_json = json.loads(raw_data)

                msg_type = incoming_json.get("type")

                if msg_type == "color_update":
                    payload = {
                        "type": "color_update",
                        "color": incoming_json.get("color")
                    }
                    await manager.broadcast(json.dumps(payload), note_id, sender=websocket)

                elif msg_type == "rename_update":
                    payload = {
                        "type": "rename_update",
                        "name": incoming_json.get("name")
                    }
                    await manager.broadcast(json.dumps(payload), note_id, sender=websocket)

                elif msg_type == "tags_update":
                    payload = {
                        "type": "tags_update",
                        "tags": incoming_json.get("tags")
                    }
                    await manager.broadcast(json.dumps(payload), note_id, sender=websocket)

                else:
                    await manager.broadcast(raw_data, note_id, sender=websocket)

            except (json.JSONDecodeError, TypeError, AttributeError):
                await manager.broadcast(raw_data, note_id, sender=websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket, note_id)

@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(note_id: int, db: Session = Depends(database.get_db)):
    note = db.query(models.Note).filter_by(id=note_id).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    payload = {
        "type": "collaborators_update",
        "collaborators": []
    }

    try:
        await manager.broadcast(json.dumps(payload), note_id, sender=None)
    except Exception as e:
        print(f"Ошибка WS при удалении: {e}")

    db.delete(note)
    db.commit()
    return None

@app.delete("/notes/{note_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag_completely(note_id: int, tag_id: int, db: Session = Depends(database.get_db)):
    note = db.query(models.Note).filter_by(id=note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Заметка не найдена")

    tag = db.query(models.Tag).filter_by(id=tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Тег не найден")

    if tag in note.tags:
        note.tags.remove(tag)
    else:
        raise HTTPException(status_code=400, detail="Этот тег не привязан к данной заметке")

    db.commit()
    db.refresh(note)

    payload = {
        "type": "tags_update",
        "tags": [{"id": t.id, "name": t.name} for t in note.tags]
    }
    await manager.broadcast(json.dumps(payload), note_id, sender=None)

    return None

@app.post("/login")
async def login(user_data: schemas.UserLogin, db: Session = Depends(database.get_db)):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://www.google.com/recaptcha/api/siteverify",
                data={
                    "secret": settings.recaptcha_secret_key,
                    "response": user_data.captchaToken
                },
                timeout = 3.0
            )
            result = response.json()
    except Exception:
        raise HTTPException(status_code=503, detail="Captcha service unavailable")

    if not result.get("success") or result.get("score", 0) < 0.5:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Security check failed"
        )

    user = db.query(models.User).filter_by(email=user_data.email).first()

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Пожалуйста, подтвердите вашу почту перед входом")

    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=400, detail="Неверный логин или пароль")

    return {"message": "Успешный вход", "user_id": str(user.id)}

@app.post("/notes", response_model=schemas.NoteResponse)
def create_note(user_id: int, note_title: str = 'New note', note_content: str = '', db: Session = Depends(database.get_db)):
    new_note = models.Note(userId=user_id, title=note_title, content=note_content)

    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    return new_note

@app.post("/send-email-code")
async def send_email_code(data: schemas.EmailSchema, db: Session = Depends(database.get_db)):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://www.google.com/recaptcha/api/siteverify",
                data={
                    "secret": settings.recaptcha_secret_key,
                    "response": data.captchaToken
                },
                timeout=3.0
            )
            result = response.json()
    except Exception:
        raise HTTPException(status_code=503, detail="Captcha service unavailable")

    if not result.get("success") or result.get("score", 0) < 0.5:
        raise HTTPException(status_code=403, detail="Security check failed")

    user = db.query(models.User).filter_by(email=data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь с такой почтой не найден")

    verification_code = f"{random.randint(100000, 999999)}"
    user.otp_code = verification_code
    user.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    db.commit()

    message = MessageSchema(
        subject="Код подтверждения для Online Notes",
        recipients=[data.email],
        body=f"Ваш проверочный код: {verification_code}",
        subtype=MessageType.plain
    )
    fm = FastMail(conf)

    try:
        await fm.send_message(message)
        return {"status": "success", "message": "Код отправлен"}
    except Exception as e:
        print(f"MAIL ERROR: {e}")
        raise HTTPException(status_code=500, detail="Ошибка отправки почты")

@app.post("/verify-otp")
async def verify_otp(data: schemas.VerifyOTP, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter_by(email=data.email).first()

    if not user or not user.otp_code:
        raise HTTPException(status_code=400, detail="Код не запрашивался")

    if datetime.now(timezone.utc) > user.otp_expires_at:
        raise HTTPException(status_code=400, detail="Срок действия кода истек")

    if user.otp_code != data.code:
        raise HTTPException(status_code=400, detail="Неверный код")

    user.otp_code = None
    user.otp_expires_at = None
    db.commit()

    return {"message": "Успешный вход", "user_id": str(user.id)}

@app.patch("/notes/{note_id}", response_model=schemas.NoteResponse)
async def update_note(
        note_id: int,
        note_data: schemas.NoteUpdate,
        db: Session = Depends(database.get_db)
):
    db_note = db.query(models.Note).filter_by(id=note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    update_dict = note_data.model_dump(exclude_unset=True)

    for key, value in update_dict.items():
        if key in ["id", "created_at"]:
            continue

        if key == "tag":
            if not value:
                continue

            tag = db.query(models.Tag).filter_by(name=value).first()
            if not tag:
                tag = models.Tag(name=value)
                db.add(tag)
                db.flush()

            if tag not in db_note.tags:
                db_note.tags.append(tag)

            payload = {
                "type": "tags_update",
                "tags": [{"id": t.id, "name": t.name} for t in db_note.tags]
            }
            await manager.broadcast(json.dumps(payload), note_id, sender=None)

        else:
            setattr(db_note, key, value)

            if key == "content":
                payload = {"type": "text_update", "content": value}
                await manager.broadcast(json.dumps(payload), note_id, sender=None)

            elif key == "color":
                payload = {"type": "color_update", "color": value}
                await manager.broadcast(json.dumps(payload), note_id, sender=None)

            elif key == "title":
                payload = {"type": "rename_update", "name": value}
                await manager.broadcast(json.dumps(payload), note_id, sender=None)

    db.commit()
    db.refresh(db_note)
    return db_note

@app.get("/notes", response_model=list[schemas.NoteShortResponse])
def get_notes(db: Session = Depends(database.get_db)):
    return db.query(models.Note).all()

@app.get("/notes/{note_id}")
def get_note_content(note_id: int, db: Session = Depends(database.get_db)):
    db_note = db.query(models.Note).filter_by(id=note_id).first()
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"content": db_note.content, "tags": db_note.tags}

@app.get("/notes/user/{user_id}", response_model=list[schemas.NoteShortResponse])
def get_user_notes_short(user_id: int, db: Session = Depends(database.get_db)):
    own_notes = db.query(models.Note).filter_by(userId=user_id).all()

    user = db.query(models.User).filter_by(id=user_id).first()
    shared_notes = user.shared_notes if user else []

    all_notes = own_notes + shared_notes
    return all_notes

@app.get("/notes/user/{user_id}/full", response_model=list[schemas.NoteResponse])
def get_user_notes_full(user_id: int, db: Session = Depends(database.get_db)):
    notes = db.query(models.Note).filter_by(userId=user_id).all()
    return notes

@app.post("/register-request")
async def register_request(data: schemas.UserCreate, db: Session = Depends(database.get_db)):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://www.google.com/recaptcha/api/siteverify",
                data={
                    "secret": settings.recaptcha_secret_key,
                    "response": data.captchaToken
                },
                timeout=3.0
            )
            result = response.json()
    except Exception:
        raise HTTPException(status_code=503, detail="Captcha service unavailable")

    if not result.get("success") or result.get("score", 0) < 0.5:
        raise HTTPException(status_code=403, detail="Security check failed")

    existing_user = db.query(models.User).filter_by(email=data.email, is_active=True).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь с такой почтой уже существует")

    verification_code = f"{random.randint(100000, 999999)}"
    hashed_password = hash_password(data.password)

    unconfirmed_user = db.query(models.User).filter_by(email=data.email, is_active=False).first()

    if unconfirmed_user:
        unconfirmed_user.password = hashed_password
        unconfirmed_user.otp_code = verification_code
        unconfirmed_user.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    else:
        unconfirmed_user = models.User(
            email=data.email,
            password=hashed_password,
            otp_code=verification_code,
            otp_expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
            is_active=False
        )
        db.add(unconfirmed_user)

    db.commit()

    # СЮДА СТАВИМ ТЕКСТ ОДИН В ОДИН ИЗ ТВОЕГО РАБОЧЕГО МЕТОДА
    message = MessageSchema(
        subject="Код подтверждения для Online Notes",
        recipients=[data.email],
        body=f"Ваш проверочный код: {verification_code}",
        subtype=MessageType.plain
    )
    fm = FastMail(conf)

    try:
        await fm.send_message(message)
        return {"status": "success", "message": "Код отправлен"}
    except Exception as e:
        print(f"MAIL ERROR: {e}")
        raise HTTPException(status_code=500, detail="Ошибка отправки почты")

@app.post("/confirm-registration", response_model=schemas.UserResponse)
async def confirm_registration(data: schemas.VerifyOTP, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter_by(email=data.email, is_active=False).first()

    if not user or not user.otp_code:
        raise HTTPException(status_code=400, detail="Код подтверждения не запрашивался")

    if datetime.utcnow() > user.otp_expires_at:
        raise HTTPException(status_code=400, detail="Срок действия кода истек")

    if user.otp_code != data.code:
        raise HTTPException(status_code=400, detail="Неверный код")

    user.is_active = True
    user.otp_code = None
    user.otp_expires_at = None
    db.commit()
    db.refresh(user)

    return user

@app.post("/users", response_model=schemas.UserResponse)
def create_user(user_data: schemas.UserCreate, db: Session = Depends(database.get_db)):
    hashed_password = hash_password(user_data.password)

    new_user = models.User(email=user_data.email, password=hashed_password, is_active=True)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.get("/users", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(database.get_db)):
    return db.query(models.User).all()

@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter_by(id=user_id).first()

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return db_user

@app.patch("/users/{user_id}/settings")
def update_user(user_id: int, settings_data: schemas.UserSettingsSchema, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter_by(id=user_id).first()
    print(settings_data)
    db_user.settings = {
        "note_display": settings_data.note_display,
        "note_sort": settings_data.note_sort,
        "tags_sort": settings_data.tags_sort,
        "theme": settings_data.theme
    }


    db.commit()
    db.refresh(db_user)
    print(db_user.settings)
    return db_user.settings

@app.get("/users/{user_id}/settings", response_model=schemas.UserSettingsSchema)
def get_user_settings(user_id: int, db: Session = Depends(database.get_db)):
    return db.query(models.User).filter_by(id=user_id).first().settings


@app.get("/users/{user_id}/tags", response_model=list[schemas.UserTagResponse])
def get_user_tags(user_id: int, db: Session = Depends(database.get_db)):
    tags = (
        db.query(models.Tag)
        .join(note_tags, models.Tag.id == note_tags.c.tag_id)
        .join(Note, note_tags.c.note_id == Note.id)
        .filter(
            (Note.userId == user_id) |
            (Note.collaborators.any(id=user_id))
        )
        .distinct()
        .all()
    )

    for tag in tags:
        valid_notes = []
        for note in tag.notes:
            is_owner = note.userId == user_id
            is_collaborator = any(collab.id == user_id for collab in note.collaborators)

            if is_owner or is_collaborator:
                valid_notes.append(note.id)

        tag.note_ids = valid_notes

    return tags

@app.post("/notes/{note_id}/share")
async def share_note_by_email(note_id: int, email: str, db: Session = Depends(database.get_db)):
    note = db.query(models.Note).filter_by(id=note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Заметка не найдена")

    invited_user = db.query(models.User).filter_by(email=email).first()
    if not invited_user:
        raise HTTPException(status_code=404, detail="Пользователь с таким email не зарегистрирован")

    if note.userId == invited_user.id:
        raise HTTPException(status_code=400, detail="Вы уже являетесь владельцем этой заметки")

    if invited_user in note.collaborators:
        raise HTTPException(status_code=400, detail="Этот пользователь уже имеет доступ")

    note.collaborators.append(invited_user)
    db.commit()

    payload = {"type": "collaborators_update"}
    await manager.broadcast(json.dumps(payload), note_id, sender=None)

    return {
        "status": "success",
        "message": "Доступ успешно предоставлен",
        "user": {
            "id": invited_user.id,
            "email": invited_user.email
        }
    }

@app.delete("/notes/{note_id}/share/{user_id}")
async def remove_collaborator(note_id: int, user_id: int, db: Session = Depends(database.get_db)):
    note = db.query(models.Note).filter_by(id=note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Заметка не найдена")

    user_to_remove = db.query(models.User).filter_by(id=user_id).first()
    if not user_to_remove:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user_to_remove not in note.collaborators:
        raise HTTPException(status_code=400, detail="У этого пользователя нет доступа к данной заметке")

    note.collaborators.remove(user_to_remove)
    db.commit()

    new_collaborators_list = [
        {"id": c.id, "email": c.email} for c in note.collaborators
    ]

    await manager.broadcast(
        json.dumps({
            "type": "collaborators_update",
            "collaborators": new_collaborators_list
        }),
        note_id,
        sender=None
    )

    return {"status": "success", "message": "Доступ успешно аннулирован"}

@app.get("/notes/{note_id}/collaborators")
def get_note_collaborators(note_id: int, db: Session = Depends(database.get_db)):
    note = db.query(models.Note).filter_by(id=note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Заметка не найдена")

    owner = db.query(models.User).filter_by(id=note.userId).first()

    result = {
        "owner": {"id": owner.id, "email": owner.email},
        "collaborators": [{"id": u.id, "email": u.email} for u in note.collaborators]
    }
    return result