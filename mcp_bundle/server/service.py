"""Thin service layer for the Diffusion Bee MCP bundle.

These functions keep the FastMCP layer thin by delegating to the extracted
backend service module.
"""

from __future__ import annotations

import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backends.stable_diffusion.service import DiffusionBeeService, generation_result_payload


@dataclass
class BundleStatus:
    implementation_status: str
    bundle_root: str
    backend_root: str
    notes: list[str]


_BACKEND_SERVICE: DiffusionBeeService | None = None


def _get_backend_service() -> DiffusionBeeService:
    global _BACKEND_SERVICE
    if _BACKEND_SERVICE is None:
        _BACKEND_SERVICE = DiffusionBeeService()
    return _BACKEND_SERVICE


def generate_image(
    *,
    prompt: str,
    negative_prompt: str,
    width: int,
    height: int,
    steps: int,
    guidance_scale: float,
    seed: int,
    num_images: int,
    model_tdict_path: str,
) -> dict:
    if not prompt.strip():
        raise ValueError("prompt must not be empty")

    request = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "img_width": width,
        "img_height": height,
        "num_steps": steps,
        "guidance_scale": guidance_scale,
        "seed": seed,
        "num_imgs": num_images,
        "model_tdict_path": model_tdict_path,
    }
    result = _get_backend_service().generate_images(request)
    payload = generation_result_payload(result)
    payload["request"] = request
    return payload


def convert_model(*, checkpoint_path: str, output_path: str) -> dict:
    if not checkpoint_path.strip():
        raise ValueError("checkpoint_path must not be empty")
    if not output_path.strip():
        raise ValueError("output_path must not be empty")

    return _get_backend_service().convert_model(checkpoint_path, output_path)


def bundle_status_payload(status: BundleStatus) -> dict:
    return asdict(status)
