from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "SortStream AI API"
    app_version: str = "1.0.0"
    environment: str = "production"
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://*.vercel.app",
        "https://*.onrender.com",
        "*",
    ]


settings = Settings()
