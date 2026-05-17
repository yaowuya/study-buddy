import json
import uuid
from pathlib import Path
from urllib.parse import quote_plus, urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.core.config import settings

router = APIRouter(prefix="/tts", tags=["tts"])

# 临时音频文件目录
TMP_DIR = Path(__file__).parent.parent.parent.parent / "tmp"
TMP_DIR.mkdir(exist_ok=True)

# 百度 TTS 配置
BAIDU_TTS_URL = "https://tsn.baidu.com/text2audio"
BAIDU_TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"

# 音色映射
VOICE_MAP = {
    "xiaomei": 0,     # 度小美 - 女声
    "xiaoyu": 1,      # 度小宇 - 男声
    "xiaoyao": 3,     # 度逍遥 - 男声
    "yaya": 4,        # 度丫丫 - 女声
    "xiaojiao": 5,    # 度小娇 - 女声
    "miduo": 103,     # 度米朵
    "bowen": 106,     # 度博文
    "xiaotong": 110,  # 度小童 - 儿童音
    "xiaomeng": 111,  # 度小萌 - 儿童音
}

DEFAULT_VOICE = "yaya"

# Token 缓存
_token_cache = {"token": None, "expires_at": 0}


def _get_baidu_token() -> str:
    """获取百度 TTS access_token"""
    import time

    if _token_cache["token"] and _token_cache["expires_at"] > time.time() + 60:
        return _token_cache["token"]

    if not settings.BAIDU_TTS_API_KEY or not settings.BAIDU_TTS_SECRET_KEY:
        raise HTTPException(500, "Baidu TTS API key not configured")

    params = {
        "grant_type": "client_credentials",
        "client_id": settings.BAIDU_TTS_API_KEY,
        "client_secret": settings.BAIDU_TTS_SECRET_KEY,
    }

    try:
        req = Request(BAIDU_TOKEN_URL + "?" + urlencode(params))
        with urlopen(req, timeout=10) as f:
            result = json.loads(f.read().decode("utf-8"))

        if "access_token" not in result:
            raise HTTPException(500, f"Baidu token error: {result}")

        _token_cache["token"] = result["access_token"]
        _token_cache["expires_at"] = time.time() + result.get("expires_in", 86400)

        return result["access_token"]

    except URLError as e:
        raise HTTPException(500, f"Baidu token request failed: {e}")


@router.get("/voices")
def list_voices():
    """列出可用的中文音色"""
    return [
        {"id": k, "name": k, "description": _get_voice_description(k)}
        for k in VOICE_MAP.keys()
    ]


def _get_voice_description(voice_id: str) -> str:
    descriptions = {
        "xiaomei": "度小美 - 女声，温柔",
        "xiaoyu": "度小宇 - 男声，年轻",
        "xiaoyao": "度逍遥 - 男声，磁性",
        "yaya": "度丫丫 - 女声，活泼",
        "xiaojiao": "度小娇 - 女声，甜美",
        "miduo": "度米朵 - 女声",
        "bowen": "度博文 - 男声",
        "xiaotong": "度小童 - 儿童音",
        "xiaomeng": "度小萌 - 儿童音",
    }
    return descriptions.get(voice_id, voice_id)


@router.get("/speak")
def speak(text: str, voice: str = DEFAULT_VOICE, rate: float = 1.0):
    """
    将文本转换为语音并返回音频文件

    - text: 要朗读的文本（不超过60个汉字）
    - voice: 音色ID (默认度逍遥)
    - rate: 语速 (0.5-2.0, 默认1.0)
    """
    if not text:
        raise HTTPException(400, "text is required")

    if len(text) > 60:
        raise HTTPException(400, "text too long (max 60 Chinese characters for Baidu TTS)")

    token = _get_baidu_token()
    per = VOICE_MAP.get(voice, VOICE_MAP[DEFAULT_VOICE])

    # 语速转换 (rate 0.5-2.0 -> spd 0-15, 1.0 对应 5)
    spd = int(max(0, min(15, (rate - 0.5) * 10)))

    # tex 需要 2 次 urlencode
    tex_encoded = quote_plus(quote_plus(text))

    # POST 请求，参数放在 body 中
    payload = f"tex={tex_encoded}&tok={token}&cuid=studybuddy&ctp=1&lan=zh&spd={spd}&pit=5&vol=9&per={per}&aue=3"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    try:
        req = Request(BAIDU_TTS_URL, data=payload.encode("utf-8"), headers=headers)
        with urlopen(req, timeout=30) as f:
            content = f.read()
            response_headers = dict((name.lower(), value) for name, value in f.headers.items())

        content_type = response_headers.get("content-type", "")
        if "audio" not in content_type:
            error_msg = content.decode("utf-8") if isinstance(content, bytes) else content
            raise HTTPException(500, f"Baidu TTS error: {error_msg}")

        filename = f"tts_{uuid.uuid4().hex}.mp3"
        temp_path = TMP_DIR / filename
        with open(temp_path, "wb") as f:
            f.write(content)

        return FileResponse(
            path=str(temp_path),
            media_type="audio/mpeg",
            filename=filename,
        )

    except URLError as e:
        raise HTTPException(500, f"Baidu TTS request failed: {e}")
