import os
import requests
from loguru import logger

from app.config import config
from app.utils import utils


def generate_from_model(prompt: str) -> str:
    """Generate a video from a custom model.

    Args:
        prompt: Text prompt to generate the video.

    Returns:
        Path to the saved video file or an empty string if failed.
    """
    endpoint = config.video_model.get("endpoint", "").strip()
    api_key = config.video_model.get("api_key", "").strip()

    if not endpoint:
        raise ValueError("video_model.endpoint is not set in config.toml")

    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    payload = {"prompt": prompt}

    for i in range(3):
        try:
            logger.info(f"start video model generation, try: {i + 1}")
            response = requests.post(endpoint, json=payload, headers=headers, stream=True)
            if response.status_code == 200:
                video_dir = utils.storage_dir("model_videos", create=True)
                video_path = os.path.join(video_dir, f"{utils.md5(prompt)}.mp4")
                with open(video_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                logger.success(f"video model generation succeeded: {video_path}")
                return video_path
            else:
                logger.error(
                    f"video model failed with status {response.status_code}: {response.text}"
                )
        except Exception as e:
            logger.error(f"video model generation error: {str(e)}")
    return ""
