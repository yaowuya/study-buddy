import uuid
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse

router = APIRouter(prefix="/tts", tags=["tts"])

# 临时音频文件目录
TMP_DIR = Path(__file__).parent.parent.parent.parent / "tmp"
TMP_DIR.mkdir(exist_ok=True)

# 中文音色映射 (Edge-TTS)
VOICE_MAP = {
    "xiaoxiao": "zh-CN-XiaoxiaoNeural",
    "yunxi": "zh-CN-YunxiNeural",
    "yunxiang": "zh-CN-YunxiangNeural",
}

DEFAULT_VOICE = "yunxiang"

# 尝试导入 edge-tts
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False


@router.get("/voices")
def list_voices():
    """列出可用的中文音色"""
    return [{"id": k, "name": k} for k in VOICE_MAP.keys()]


@router.get("/speak")
async def speak(text: str, voice: str = DEFAULT_VOICE, rate: float = 1.0):
    """
    将文本转换为语音并返回音频文件
    优先使用 Edge-TTS，失败则使用备用在线 TTS
    """
    if not text:
        raise HTTPException(400, "text is required")

    if len(text) > 5000:
        raise HTTPException(400, "text too long (max 5000 chars)")

    filename = f"tts_{uuid.uuid4().hex}.mp3"
    temp_path = TMP_DIR / filename

    # 尝试 Edge-TTS
    if EDGE_TTS_AVAILABLE:
        try:
            voice_name = VOICE_MAP.get(voice, VOICE_MAP[DEFAULT_VOICE])
            rate_percent = int((rate - 1) * 100)
            rate_str = f"+{rate_percent}%" if rate_percent >= 0 else f"{rate_percent}%"

            communicate = edge_tts.Communicate(text, voice_name, rate=rate_str)
            await communicate.save(str(temp_path))

            if temp_path.exists() and temp_path.stat().st_size > 0:
                return FileResponse(
                    path=str(temp_path),
                    media_type="audio/mpeg",
                    filename=filename,
                )
        except Exception as e:
            print(f"[TTS] Edge-TTS failed: {e}")
            # 继续尝试备用方案

    # 备用方案：使用有道 TTS（国内可用，无需 API Key）
    try:
        return await _tts_youdao(text, rate)
    except Exception as e:
        raise HTTPException(500, f"All TTS services failed: {str(e)}")


async def _tts_youdao(text: str, rate: float = 1.0):
    """使用有道 TTS（国内可用，免费）"""
    # 有道 TTS URL
    encoded_text = quote(text)
    url = f"https://tts.youdao.com/listen?le=zh&text={encoded_text}&keyfrom=studybuddy"

    # 流式返回音频
    import httpx
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, follow_redirects=True)
        if response.status_code != 200:
            raise HTTPException(500, "Youdao TTS failed")

        return StreamingResponse(
            iter([response.content]),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=tts.mp3"}
        )
