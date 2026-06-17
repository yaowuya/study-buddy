import logging
from pathlib import Path


def setup_logging(log_dir: str = "/app/logs") -> None:
    """
    统一日志配置：同时输出到 stderr 和持久化文件。
    在 app.main 启动时调用一次即可，所有模块通过
    logging.getLogger(__name__) 获取 logger 自动继承此配置。
    """
    _log_dir = Path(log_dir)
    _log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        handlers=[
            logging.StreamHandler(),                          # stderr（docker logs 可见）
            logging.FileHandler(_log_dir / "app.log"),        # 持久化到挂载目录
        ],
    )
