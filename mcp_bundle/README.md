# Diffusion Bee MCP Bundle

This directory is the starting point for a standalone MCP Bundle target.

It is intentionally separate from the Electron desktop application in
[`electron_app/`](../electron_app) and the existing UI-to-backend bridge. The
goal is to expose a narrow, headless MCP server surface that can reuse backend
generation logic without depending on Electron process management or the
`b2py`/`sdbk` string protocol.

## Current Status

This now contains an experimental FastMCP-based server backed by a shared Python service
module in [`backends/stable_diffusion/service.py`](../backends/stable_diffusion/service.py).

Included here:

- `manifest.json`: provisional MCPB manifest for a Python-based local server
- `requirements.txt`: pins the Python MCP SDK to the stable v1 line
- `server/main.py`: FastMCP entry point and tool registration
- `server/service.py`: thin MCP-to-backend adapter
- `tests/`: unit tests for both the MCP adapter and backend service seam

Not included yet:

- packaged Python dependencies
- bundle build/validation automation

## FastMCP

This bundle is scaffolded around FastMCP rather than a hand-rolled MCP
transport.

Install the Python dependency from this directory with:

```bash
pip install -r mcp_bundle/requirements.txt
```

The current dependency target is `mcp[cli]<2` so the bundle stays on the
stable v1 SDK line instead of the pre-alpha v2 branch.

Run the server directly with:

```bash
python mcp_bundle/server/main.py
```

Run the current tests with:

```bash
python -m unittest discover -s mcp_bundle/tests -p 'test_*.py'
```

## V0 Tool Surface

The initial tool shape follows an Easy Diffusion-style approach: a small number
of high-level, opinionated tools rather than a graph API.

Current tools:

- `bundle_status`: working introspection tool for checking scaffold status
- `generate_image_tool`: forwards requests into the extracted backend service
- `convert_model_tool`: forwards model conversion requests into the extracted backend service

The `generate_image_tool` parameters are intentionally close to the existing
frontend request shape:

- `prompt`
- `negative_prompt`
- `width`
- `height`
- `steps`
- `guidance_scale`
- `seed`
- `num_images`
- `model_tdict_path`

## Intended Architecture

The MCP bundle should depend on extracted backend modules, not on Electron app
code. In particular, it should not import or mimic:

- `electron_app/src/bridge.js`
- `electron_app/src/py_vue_bridge.js`
- renderer state update messages like `utds` or `sdbk`

Instead, the extraction path should look like:

1. Move generation and model-management operations behind a Python service API.
2. Keep CLI / stdio / MCP request handling inside `mcp_bundle/`.
3. Have the MCP server call shared backend functions directly.

## Extracted Service

The shared backend service now lives under `backends/stable_diffusion/` with a
small, explicit API centered on:

- `generate_images(request) -> list[GeneratedImage]`
- `convert_model(checkpoint_path, output_path) -> ConversionResult`

The Electron stdin backend and the FastMCP server both call into that shared
service. `mcp_bundle/server/main.py` stays transport-only, while
`mcp_bundle/server/service.py` is a narrow adapter that translates MCP tool
arguments into backend service requests.
