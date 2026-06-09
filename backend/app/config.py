from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    app_name: str = "notes-backend"
    debug: bool = True
    database_url: str = "sqlite:///notes.db"

    recaptcha_secret_key: str
    mail_password: str

    cors_origins: list = [
        "http://localhost:8000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ]
    static_dir: str = "static"
    images_dir: str = "static/images"

    mail_username: str = "qwizzitnotes@gmail.com"
    mail_from: str = "qwizzitnotes@gmail.com"

    mail_port: int = 465 

    mail_server: str = "smtp.gmail.com"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

        case_sensitive = False

settings = Settings()