"""FastMCP entry point for the Diffusion Bee MCP bundle."""

from __future__ import annotations

import sys
from pathlib import Path

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover - import guard for local setup
    FastMCP = None
    FASTMCP_IMPORT_ERROR = exc
else:
    FASTMCP_IMPORT_ERROR = None

try:
    from .service import BundleStatus, convert_model, generate_image
except ImportError:
    from service import BundleStatus, convert_model, generate_image


ROOT_DIR = Path(__file__).resolve().parents[1]


def _build_server() -> "FastMCP":
    server = FastMCP(
        "Diffusion Bee Local",
        instructions=(
            "High-level local image generation tools for Diffusion Bee. "
            "This server is intentionally opinionated and does not expose "
            "Electron-specific transport details."
        ),
    )

    @server.tool()
    def bundle_status() -> BundleStatus:
        """Describe the current state of the Diffusion Bee MCP bundle."""
        return BundleStatus(
            implementation_status="scaffold",
            bundle_root=str(ROOT_DIR),
            backend_root=str(ROOT_DIR.parent / "backends" / "stable_diffusion"),
            notes=[
                "FastMCP server scaffold is in place.",
                "The MCP layer delegates to extracted backend services.",
                "Use this server as a thin wrapper over shared backend services.",
            ],
        )

    @server.tool()
    def generate_image_tool(
        prompt: str,
        negative_prompt: str = "",
        width: int = 512,
        height: int = 512,
        steps: int = 25,
        guidance_scale: float = 7.5,
        seed: int = 0,
        num_images: int = 1,
        model_tdict_path: str = "",
    ) -> dict:
        """Generate images from a prompt using an Easy Diffusion-style API."""
        return generate_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            steps=steps,
            guidance_scale=guidance_scale,
            seed=seed,
            num_images=num_images,
            model_tdict_path=model_tdict_path,
        )

    @server.tool()
    def convert_model_tool(
        checkpoint_path: str,
        output_path: str,
    ) -> dict:
        """Convert a checkpoint into Diffusion Bee's runtime format."""
        return convert_model(
            checkpoint_path=checkpoint_path,
            output_path=output_path,
        )

    return server


def main() -> int:
    if FastMCP is None:
        sys.stderr.write(
            "FastMCP is not installed. Install dependencies from "
            "mcp_bundle/requirements.txt before running this server.\n"
        )
        sys.stderr.write(f"Import error: {FASTMCP_IMPORT_ERROR}\n")
        return 1

    server = _build_server()
    server.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
