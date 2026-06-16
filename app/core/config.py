from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:root@localhost:3306/studybuddy"
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ADMIN_TOKEN_EXPIRE_MINUTES: int = 60 * 8         # 管理员 token 8 小时
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:5174"]

    # 百度 TTS 配置
    BAIDU_TTS_API_KEY: str = ""
    BAIDU_TTS_SECRET_KEY: str = ""
    BAIDU_TTS_DEFAULT_VOICE: str = "yaya"  # 默认语音：yaya(度丫丫), xiaoyao(度逍遥) 等

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_must_be_changed(cls, v: str) -> str:
        if v == "change-me-in-production":
            import os
            if os.environ.get("APP_ENV", "development") == "production":
                raise ValueError(
                    "SECRET_KEY must be set to a secure value in production. "
                    "Set APP_ENV=development to skip this check in development."
                )
        return v

    model_config = {"env_file": ".env"}


settings = Settings()
