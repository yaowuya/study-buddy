import asyncio
import tempfile
from pathlib import Path

import edge_tts
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/tts", tags=["tts"])

# 中文音色映射
VOICE_MAP = {
    "xiaoxiao": "zh-CN-XiaoxiaoNeural",      # 晓晓 - 女声，温柔
    "yunxi": "zh-CN-YunxiNeural",             # 云希 - 男声，年轻
    "yunjian": "zh-CN-YunjianNeural",         # 云健 - 男声，成熟
    "xiaoyi": "zh-CN-XiaoyiNeural",           # 晓伊 - 女声，活泼
    "yunxiang": "zh-CN-YunxiangNeural",       # 云扬 - 男声，新闻播报风格
    "xiaochen": "zh-CN-XiaochenNeural",       # 晓辰 - 女声，新闻播报风格
    "xiaohan": "zh-CN-XiaohanNeural",         # 晓涵 - 女声，温暖
    "xiaomeng": "zh-CN-XiaomengNeural",       # 晓梦 - 女声，可爱
    "xiaomo": "zh-CN-XiaomoNeural",           # 晓墨 - 女声，知性
    "xiaorui": "zh-CN-XiaoruiNeural",         # 晓睿 - 女声，儿童
    "xiaoshuang": "zh-CN-XiaoshuangNeural",   # 晓双 - 女声，儿童
    "xiaoxuan": "zh-CN-XiaoxuanNeural",       # 晓萱 - 女声，温柔
    "yunhao": "zh-CN-YunhaoNeural",           # 云皓 - 男声，商务
    "yunxia": "zh-CN-YunxiaNeural",           # 云夏 - 女声，年轻
    "yunye": "zh-CN-YunyeNeural",             # 云野 - 男声，自然
    "yunze": "zh-CN-YunzeNeural",             # 云泽 - 男声，沉稳
}

DEFAULT_VOICE = "yunxiang"  # 默认使用云扬，适合听写


@router.get("/voices")
def list_voices():
    """列出可用的中文音色"""
    return [
        {"id": k, "name": k, "description": _get_voice_description(k)}
        for k in VOICE_MAP.keys()
    ]


def _get_voice_description(voice_id: str) -> str:
    descriptions = {
        "xiaoxiao": "晓晓 - 女声，温柔自然",
        "yunxi": "云希 - 男声，年轻活泼",
        "yunjian": "云健 - 男声，成熟稳重",
        "xiaoyi": "晓伊 - 女声，活泼可爱",
        "yunxiang": "云扬 - 男声，新闻播报风格",
        "xiaochen": "晓辰 - 女声，新闻播报风格",
        "xiaohan": "晓涵 - 女声，温暖亲切",
        "xiaomeng": "晓梦 - 女声，可爱甜美",
        "xiaomo": "晓墨 - 女声，知性优雅",
        "xiaorui": "晓睿 - 女声，儿童音",
        "xiaoshuang": "晓双 - 女声，儿童音",
        "xiaoxuan": "晓萱 - 女声，温柔细腻",
        "yunhao": "云皓 - 男声，商务专业",
        "yunxia": "云夏 - 女声，年轻清新",
        "yunye": "云野 - 男声，自然随和",
        "yunze": "云泽 - 男声，沉稳大气",
    }
    return descriptions.get(voice_id, voice_id)


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

    # 获取音色
    voice_name = VOICE_MAP.get(voice, VOICE_MAP[DEFAULT_VOICE])

    # 语速转换: edge-tts 使用 "+0%" 格式
    rate_str = f"{'+' if rate >= 1 else ''}{int((rate - 1) * 100)}%"

    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            temp_path = Path(f.name)

        # 使用 edge-tts 生成音频
        communicate = edge_tts.Communicate(text, voice_name, rate=rate_str)
        await communicate.save(str(temp_path))

        # 返回音频文件
        return FileResponse(
            path=str(temp_path),
            media_type="audio/mpeg",
            filename=f"tts_{hash(text) % 10000}.mp3",
            background=lambda: _cleanup_file(temp_path)
        )

    except Exception as e:
        raise HTTPException(500, f"TTS failed: {str(e)}")


def _cleanup_file(path: Path):
    """清理临时文件"""
    try:
        if path.exists():
            path.unlink()
    except Exception:
        pass
