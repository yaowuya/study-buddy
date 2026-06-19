import json
import logging
import uuid
from pathlib import Path
from urllib.parse import quote_plus, urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.core.config import settings

# 日志由 app.main 统一配置
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tts", tags=["tts"])

# 临时音频文件目录
TMP_DIR = Path(__file__).parent.parent.parent.parent / "tmp"
TMP_DIR.mkdir(exist_ok=True)

# 百度 TTS 配置
BAIDU_TTS_URL = "https://tsn.baidu.com/text2audio"
BAIDU_TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"

# 音色映射
VOICE_MAP = {
    # 基础音库
    "xiaomei": 0,       # 度小美 - 女声
    "xiaoyu": 1,        # 度小宇 - 男声
    "xiaoyao": 3,       # 度逍遥 - 男声
    "yaya": 4,          # 度丫丫 - 女声
    # 精品音库
    "xiaoyao_pro": 5003,  # 度逍遥（精品）
    "xiaolu": 5118,       # 度小鹿
    "bowen": 106,         # 度博文
    "xiaotong": 110,      # 度小童 - 儿童音
    "xiaomeng": 111,      # 度小萌 - 儿童音
    "miduo": 103,         # 度米朵
    "xiaojiao": 5,        # 度小娇
    # 臻品音库
    "xiaoyao_best": 4003,  # 度逍遥（臻品）
    "bowen_best": 4106,    # 度博文（臻品）
    "xiaoxian": 4115,      # 度小贤
    "xiaolu_best": 4119,   # 度小鹿（臻品）
    "linger": 4105,        # 度灵儿
    "xiaoqiao": 4117,      # 度小乔
    "xiaowen": 4100,       # 度小雯
    "miduo_best": 4103,    # 度米朵（臻品）
    "shanshan": 4144,      # 度姗姗
    "xiaobei": 4278,       # 度小贝
    "qingfeng": 4143,      # 度清风
    "xiaoxin": 4140,       # 度小新
    "xiaoyan": 4129,       # 度小彦
    "xinghe": 4149,        # 度星河
    "xiaoqing": 4254,      # 度小清
    # 大模型音库
    "hanzhu": 4189,        # 度涵竹
    "yanran": 4194,        # 度嫣然
    "zeyan": 4193,         # 度泽言
    "huaian": 4195,        # 度怀安
    "qingying": 4196,      # 度清影
    "qinyao": 4197,        # 度沁遥
    "xiaoyue": 20100,      # 度小粤
    "xiaoyun": 20101,      # 度晓芸
}

DEFAULT_VOICE = "yaya"

# Token 缓存
_token_cache = {"token": None, "expires_at": 0}


def _get_baidu_token() -> str:
    """获取百度 TTS access_token"""
    import time

    logger.info("[TTS] 获取百度 Token...")

    if _token_cache["token"] and _token_cache["expires_at"] > time.time() + 60:
        logger.info("[TTS] 使用缓存的 Token")
        return _token_cache["token"]

    api_key = settings.BAIDU_TTS_API_KEY
    secret_key = settings.BAIDU_TTS_SECRET_KEY

    logger.info(f"[TTS] API_KEY 配置状态: {'已配置' if api_key else '未配置'}")
    logger.info(f"[TTS] SECRET_KEY 配置状态: {'已配置' if secret_key else '未配置'}")

    if not api_key or not secret_key:
        logger.error("[TTS] 百度 TTS API Key 或 Secret Key 未配置")
        raise HTTPException(500, "Baidu TTS API key not configured")

    params = {
        "grant_type": "client_credentials",
        "client_id": api_key,
        "client_secret": secret_key,
    }

    try:
        url = BAIDU_TOKEN_URL + "?" + urlencode(params)
        logger.info(f"[TTS] 请求 Token URL: {BAIDU_TOKEN_URL}")

        req = Request(url)
        with urlopen(req, timeout=10) as f:
            result = json.loads(f.read().decode("utf-8"))

        logger.info(f"[TTS] Token 响应: {result}")

        if "access_token" not in result:
            logger.error(f"[TTS] Token 获取失败: {result}")
            raise HTTPException(500, f"Baidu token error: {result}")

        _token_cache["token"] = result["access_token"]
        _token_cache["expires_at"] = time.time() + result.get("expires_in", 86400)

        logger.info("[TTS] Token 获取成功")
        return result["access_token"]

    except URLError as e:
        logger.error(f"[TTS] Token 请求网络错误: {e}")
        raise HTTPException(500, f"Baidu token request failed: {e}")
    except Exception as e:
        logger.error(f"[TTS] Token 请求异常: {e}")
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
        # 基础音库
        "xiaomei": "度小美 - 女声，温柔",
        "xiaoyu": "度小宇 - 男声，年轻",
        "xiaoyao": "度逍遥 - 男声，磁性",
        "yaya": "度丫丫 - 女声，活泼",
        # 精品音库
        "xiaoyao_pro": "度逍遥（精品）- 男声",
        "xiaolu": "度小鹿 - 女声",
        "bowen": "度博文 - 男声",
        "xiaotong": "度小童 - 儿童音",
        "xiaomeng": "度小萌 - 儿童音",
        "miduo": "度米朵 - 女声",
        "xiaojiao": "度小娇 - 女声，甜美",
        # 臻品音库
        "xiaoyao_best": "度逍遥（臻品）- 男声",
        "bowen_best": "度博文（臻品）- 男声",
        "xiaoxian": "度小贤 - 女声",
        "xiaolu_best": "度小鹿（臻品）- 女声",
        "linger": "度灵儿 - 女声",
        "xiaoqiao": "度小乔 - 女声",
        "xiaowen": "度小雯 - 女声",
        "miduo_best": "度米朵（臻品）- 女声",
        "shanshan": "度姗姗 - 女声",
        "xiaobei": "度小贝 - 男声",
        "qingfeng": "度清风 - 男声",
        "xiaoxin": "度小新 - 男声",
        "xiaoyan": "度小彦 - 男声",
        "xinghe": "度星河 - 男声",
        "xiaoqing": "度小清 - 女声",
        # 大模型音库
        "hanzhu": "度涵竹 - 女声",
        "yanran": "度嫣然 - 女声",
        "zeyan": "度泽言 - 男声",
        "huaian": "度怀安 - 男声",
        "qingying": "度清影 - 女声",
        "qinyao": "度沁遥 - 女声",
        "xiaoyue": "度小粤 - 粤语女声",
        "xiaoyun": "度晓芸 - 女声",
    }
    return descriptions.get(voice_id, voice_id)


@router.get("/speak")
def speak(text: str, voice: str = None, rate: float = 1.0):
    """
    将文本转换为语音并返回音频文件

    - text: 要朗读的文本（不超过60个汉字）
    - voice: 音色ID (可选，默认使用环境变量配置)
    - rate: 语速 (0.5-2.0, 默认1.0)
    """
    logger.info(f"[TTS] 收到请求 - text: {text}, voice: {voice}, rate: {rate}")

    if not text:
        logger.error("[TTS] text 参数为空")
        raise HTTPException(400, "text is required")

    if len(text) > 60:
        logger.error(f"[TTS] text 长度超限: {len(text)}")
        raise HTTPException(400, "text too long (max 60 Chinese characters for Baidu TTS)")

    # 使用环境变量配置的默认语音
    default_voice = settings.BAIDU_TTS_DEFAULT_VOICE or DEFAULT_VOICE
    voice = voice or default_voice
    logger.info(f"[TTS] 使用语音: {voice} (默认: {default_voice})")

    # 获取 token
    try:
        token = _get_baidu_token()
    except Exception as e:
        logger.error(f"[TTS] 获取 Token 失败: {e}")
        raise

    per = VOICE_MAP.get(voice, VOICE_MAP.get(default_voice, 4))
    logger.info(f"[TTS] 音色编号 per: {per}")

    # 语速转换 (rate 0.5-2.0 -> spd 0-15, 1.0 对应 5)
    spd = int(max(0, min(15, (rate - 0.5) * 10)))

    # tex 需要 2 次 urlencode
    tex_encoded = quote_plus(quote_plus(text))

    # POST 请求，参数放在 body 中
    payload = f"tex={tex_encoded}&tok={token}&cuid=studybuddy&ctp=1&lan=zh&spd={spd}&pit=5&vol=9&per={per}&aue=3"
    logger.info(f"[TTS] 请求百度 API - per={per}, spd={spd}")

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    try:
        req = Request(BAIDU_TTS_URL, data=payload.encode("utf-8"), headers=headers)
        logger.info(f"[TTS] 发送请求到百度 TTS API...")

        with urlopen(req, timeout=30) as f:
            content = f.read()
            response_headers = dict((name.lower(), value) for name, value in f.headers.items())

        content_type = response_headers.get("content-type", "")
        content_length = len(content)
        logger.info(f"[TTS] 百度响应 - Content-Type: {content_type}, Length: {content_length}")

        if "audio" not in content_type:
            error_msg = content.decode("utf-8") if isinstance(content, bytes) else content
            logger.error(f"[TTS] 百度 TTS 返回错误: {error_msg}")
            raise HTTPException(500, f"Baidu TTS error: {error_msg}")

        filename = f"tts_{uuid.uuid4().hex}.mp3"
        temp_path = TMP_DIR / filename
        with open(temp_path, "wb") as f:
            f.write(content)

        logger.info(f"[TTS] 音频文件生成成功: {filename}")
        return FileResponse(
            path=str(temp_path),
            media_type="audio/mpeg",
            filename=filename,
        )

    except URLError as e:
        logger.error(f"[TTS] 百度 API 网络错误: {e}")
        raise HTTPException(500, f"Baidu TTS request failed: {e}")
    except Exception as e:
        logger.error(f"[TTS] 百度 API 请求异常: {e}")
        raise HTTPException(500, f"Baidu TTS request failed: {e}")
