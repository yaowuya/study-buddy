from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:root@localhost:3306/studybuddy"
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # 百度 TTS 配置
    BAIDU_TTS_API_KEY: str = ""
    BAIDU_TTS_SECRET_KEY: str = ""
    BAIDU_TTS_DEFAULT_VOICE: str = "yaya"  # 默认语音：yaya(度丫丫), xiaoyao(度逍遥) 等

    model_config = {"env_file": ".env"}


settings = Settings()
