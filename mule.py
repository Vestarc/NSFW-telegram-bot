import base64
import mimetypes
import os
import time
from typing import Any, Dict, List, Optional, Tuple

import requests


MULEROUTER_API_BASE = os.getenv("MULEROUTER_API_BASE", "https://api.mulerouter.ai")
# this is the default prompt
#here you are required to provide a prompt that will be used to enhance the image. The prompt should be clear and specific about how you want the image to be altered or improve or changed rember this api is nsfw capable so you can edit images to suit any nsfw needs
DEFAULT_ENHANCE_PROMPT = (
	"alter the appearance of the image."
)

class MuleRouterError(RuntimeError):
	pass


def build_enhance_prompt(user_prompt: Optional[str]) -> str:
	#as mentioned in main.py  Caption/user prompt is intentionally ignored
	return DEFAULT_ENHANCE_PROMPT


def _auth_headers(api_key: str) -> Dict[str, str]:
	return {"Authorization": f"Bearer {api_key}"}


def _guess_mime_from_path(file_path: Optional[str]) -> str:
	if file_path:
		mime, _ = mimetypes.guess_type(file_path)
		if mime:
			return mime
	return "image/jpeg"


def telegram_download_photo_bytes(telegram_bot_token: str, file_id: str, timeout_s: int = 30) -> Tuple[bytes, str]:
	get_file_url = f"https://api.telegram.org/bot{telegram_bot_token}/getFile"
	r = requests.post(get_file_url, json={"file_id": file_id}, timeout=timeout_s)
	r.raise_for_status()
	payload = r.json()
	if not payload.get("ok"):
		raise MuleRouterError(f"Telegram getFile failed: {payload}")

	result = payload.get("result") or {}
	file_path = result.get("file_path")
	if not file_path:
		raise MuleRouterError(f"Telegram getFile returned no file_path: {payload}")

	file_url = f"https://api.telegram.org/file/bot{telegram_bot_token}/{file_path}"
	fr = requests.get(file_url, timeout=timeout_s)
	fr.raise_for_status()
	return fr.content, file_path


def bytes_to_data_url(image_bytes: bytes, mime: str) -> str:
	b64 = base64.b64encode(image_bytes).decode("ascii")
	return f"data:{mime};base64,{b64}"


def qwen_image_edit_spicy_create_task(
	api_key: str,
	*,
	image: str,
	prompt: str,
	seed: Optional[int] = None,
	timeout_s: int = 60,
) -> str:
	url = f"{MULEROUTER_API_BASE.rstrip('/')}/vendors/carrothub/v1/qwen-image-edit-spicy/generation"
	body: Dict[str, Any] = {"image": image, "prompt": prompt}
	if seed is not None:
		body["seed"] = seed

	r = requests.post(url, headers=_auth_headers(api_key), json=body, timeout=timeout_s)
	r.raise_for_status()
	data = r.json() or {}
	task_info = (data.get("task_info") or {})
	task_id = task_info.get("id")
	if not task_id:
		raise MuleRouterError(f"Unexpected task create response: {data}")
	return task_id


def qwen_image_edit_spicy_get_task(
	api_key: str,
	*,
	task_id: str,
	timeout_s: int = 60,
) -> Dict[str, Any]:
	url = (
		f"{MULEROUTER_API_BASE.rstrip('/')}/vendors/carrothub/v1/qwen-image-edit-spicy/generation/{task_id}"
	)
	r = requests.get(url, headers=_auth_headers(api_key), timeout=timeout_s)
	r.raise_for_status()
	return r.json() or {}


def qwen_image_edit_spicy_wait_for_result(
	api_key: str,
	*,
	task_id: str,
	poll_interval_s: float = 2.0,
	timeout_s: float = 90.0,
) -> List[str]:
	deadline = time.time() + timeout_s
	last_payload: Dict[str, Any] = {}

	while time.time() < deadline:
		last_payload = qwen_image_edit_spicy_get_task(api_key, task_id=task_id)
		task_info = (last_payload.get("task_info") or {})
		status = task_info.get("status")

		if status == "completed":
			images = last_payload.get("images") or []
			if not isinstance(images, list) or not images:
				raise MuleRouterError(f"Task completed but no images returned: {last_payload}")
			return [str(u) for u in images]

		if status == "failed":
			raise MuleRouterError(f"Task failed: {last_payload}")

		time.sleep(poll_interval_s)

	raise MuleRouterError(f"Timed out waiting for task result: {task_id} (last={last_payload})")


def enhance_telegram_photo(
	*,
	mule_api_key: str,
	telegram_bot_token: str,
	file_id: str,
	user_prompt: Optional[str] = None,
	seed: Optional[int] = None,
) -> str:
	
	if not mule_api_key:
		raise MuleRouterError("MULE_API_KEY is not set")

	img_bytes, file_path = telegram_download_photo_bytes(telegram_bot_token, file_id)
	mime = _guess_mime_from_path(file_path)
	data_url = bytes_to_data_url(img_bytes, mime)
	prompt = build_enhance_prompt(user_prompt)

	task_id = qwen_image_edit_spicy_create_task(api_key=mule_api_key, image=data_url, prompt=prompt, seed=seed)
	images = qwen_image_edit_spicy_wait_for_result(api_key=mule_api_key, task_id=task_id)
	return images[0]

