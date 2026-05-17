import os
import uuid
from pathlib import Path

import edge_tts
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/tts", tags=["tts"])

# 临时音频文件目录
TMP_DIR = Path(__file__).parent.parent.parent.parent / "tmp"
TMP_DIR.mkdir(exist_ok=True)

# 中文音色映射
VOICE_MAP = {
    "xiaoxiao": "zh-CN-XiaoxiaoNeural",
    "yunxi": "zh-CN-YunxiNeural",
    "yunjian": "zh-CN-YunjianNeural",
    "xiaoyi": "zh-CN-XiaoyiNeural",
    "yunxiang": "zh-CN-YunxiangNeural",
    "xiaochen": "zh-CN-XiaochenNeural",
    "xiaohan": "zh-CN-XiaohanNeural",
    "xiaomeng": "zh-CN-XiaomengNeural",
    "xiaomo": "zh-CN-XiaomoNeural",
    "xiaorui": "zh-CN-XiaoruiNeural",
    "xiaoshuang": "zh-CN-XiaoshuangNeural",
    "xiaoxuan": "zh-CN-XiaoxuanNeural",
    "yunhao": "zh-CN-YunhaoNeural",
    "yunxia": "zh-CN-YunxiaNeural",
    "yunye": "zh-CN-YunyeNeural",
    "yunze": "zh-CN-YunzeNeural",
}

DEFAULT_VOICE = "yunxiang"


@router.get("/voices")
def list_voices():
    """列出可用的中文音色"""
    return [{"id": k, "name": k} for k in VOICE_MAP.keys()]


@router.get("/speak")
async def speak(text: str, voice: str = DEFAULT_VOICE, rate: float = 1.0):
    """
    将文本转换为语音并返回音频文件

    - text: 要朗读的文本
    - voice: 音色ID (默认云扬)
    - rate: 语速 (0.5-2.0, 默认1.0)
    """
    if not text:
        raise HTTPException(400, "text is required")

    if len(text) > 5000:
        raise HTTPException(400, "text too long (max 5000 chars)")

    voice_name = VOICE_MAP.get(voice, VOICE_MAP[DEFAULT_VOICE])

    # 语速转换: edge-tts 使用 "+0%" 或 "-0%" 格式
    rate_percent = int((rate - 1) * 100)
    rate_str = f"+{rate_percent}%" if rate_percent >= 0 else f"{rate_percent}%"

    # 生成唯一文件名
    filename = f"tts_{uuid.uuid4().hex}.mp3"
    temp_path = TMP_DIR / filename

    try:
        communicate = edge_tts.Communicate(text, voice_name, rate=rate_str)
        await communicate.save(str(temp_path))

        if not temp_path.exists() or temp_path.stat().st_size == 0:
            raise HTTPException(500, "TTS generated empty file")

        return FileResponse(
            path=str(temp_path),
            media_type="audio/mpeg",
            filename=filename,
        )

    except edge_tts.exceptions.NoAudioReceived:
        raise HTTPException(500, "TTS service unavailable, please check network")
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        raise HTTPException(500, f"TTS failed: {str(e)}")
