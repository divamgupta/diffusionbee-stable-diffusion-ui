"""Thin service layer for the Diffusion Bee MCP bundle.

These functions define the intended stable boundary for the MCP server.
They currently fail clearly because the Electron-specific backend flow has
not been extracted into reusable headless services yet.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class BundleStatus:
    implementation_status: str
    bundle_root: str
    backend_root: str
    notes: list[str]


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
    raise NotImplementedError(
        "generate_image is not implemented yet. Extract a reusable Python "
        "service from backends/stable_diffusion/diffusionbee_backend.py that "
        f"accepts structured requests like: {request!r}"
    )


def convert_model(*, checkpoint_path: str, output_path: str) -> dict:
    if not checkpoint_path.strip():
        raise ValueError("checkpoint_path must not be empty")
    if not output_path.strip():
        raise ValueError("output_path must not be empty")

    raise NotImplementedError(
        "convert_model is not implemented yet. Wrap the existing conversion "
        "path behind a reusable function before exposing it through MCP."
    )


def bundle_status_payload(status: BundleStatus) -> dict:
    return asdict(status)
