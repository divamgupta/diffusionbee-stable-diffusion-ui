from __future__ import annotations

import os
import random
import sys
from dataclasses import asdict, dataclass
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Callable

from PIL import Image


@dataclass
class GeneratedImage:
    generated_img_path: str
    aux_output_image_path: str | None = None


@dataclass
class GenerationResult:
    images: list[GeneratedImage]


ProgressCallback = Callable[[str, float], str | None]


def _ensure_backend_import_paths() -> Path:
    backend_root = Path(__file__).resolve().parent
    model_converter_root = backend_root.parent / "model_converter"
    model_interface_path = os.environ.get("MODEL_INTERFACE_PATH") or "../stable_diffusion_tf_models"
    model_interface_root = (backend_root / model_interface_path).resolve()

    for path in (model_converter_root, model_interface_root):
        path_str = str(path)
        if path_str not in sys.path:
            sys.path.append(path_str)

    return backend_root


def get_projects_root() -> Path:
    projects_root = Path.home() / ".diffusionbee"
    projects_root.mkdir(parents=True, exist_ok=True)
    return projects_root


def get_default_output_dir() -> Path:
    output_dir = get_projects_root() / "images"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def get_debug_output_path() -> str | None:
    if str(os.environ.get("DEBUG")) != "1":
        return None

    debug_output_dir = get_projects_root() / "debug_outs"
    debug_output_dir.mkdir(parents=True, exist_ok=True)
    return str(debug_output_dir)


def _load_convert_model():
    _ensure_backend_import_paths()
    from convert_model import convert_model

    return convert_model


def _load_model_interface(use_dummy_interface: bool):
    backend_root = _ensure_backend_import_paths()
    if use_dummy_interface:
        module_path = backend_root / "fake_interface" / "interface.py"
        module_name = "diffusionbee_fake_interface"
    else:
        model_interface_path = os.environ.get("MODEL_INTERFACE_PATH") or "../stable_diffusion_tf_models"
        module_path = (backend_root / model_interface_path / "interface.py").resolve()
        module_name = "diffusionbee_model_interface"

    spec = spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load ModelInterface from {module_path}")

    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.ModelInterface


def _load_generator_dependencies():
    _ensure_backend_import_paths()
    from stable_diffusion.stable_diffusion import ModelContainer, StableDiffusion
    from stable_diffusion.utils.utils import get_sd_run_from_dict

    return ModelContainer, StableDiffusion, get_sd_run_from_dict


class DiffusionBeeService:
    def __init__(
        self,
        *,
        use_dummy_interface: bool = False,
        output_dir: str | Path | None = None,
        image_writer: Callable[[object, str], None] | None = None,
        random_int: Callable[[int, int], int] | None = None,
        generator_factory: Callable[[Callable[[str, float], str | None]], object] | None = None,
        sd_run_factory: Callable[[dict], object] | None = None,
    ) -> None:
        self.use_dummy_interface = use_dummy_interface
        self.output_dir = Path(output_dir) if output_dir is not None else get_default_output_dir()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.image_writer = image_writer or self._default_image_writer
        self.random_int = random_int or random.randint
        self._generator_factory = generator_factory
        self._sd_run_factory = sd_run_factory
        self._progress_callback: ProgressCallback | None = None
        self._generator = None
        self._model_container = None

    def _default_image_writer(self, image_array: object, output_path: str) -> None:
        Image.fromarray(image_array).save(output_path)

    def _handle_progress(self, state: str = "", progress: float = -1) -> str | None:
        if self._progress_callback is None:
            return None
        return self._progress_callback(state, progress)

    def _get_generator(self):
        if self._generator is not None:
            return self._generator

        if self._generator_factory is not None:
            self._generator = self._generator_factory(self._handle_progress)
            return self._generator

        ModelContainer, StableDiffusion, _ = _load_generator_dependencies()
        ModelInterface = _load_model_interface(self.use_dummy_interface)

        self._model_container = ModelContainer()
        self._generator = StableDiffusion(
            self._model_container,
            ModelInterface,
            None,
            model_name=None,
            callback=self._handle_progress,
            debug_output_path=get_debug_output_path(),
        )
        return self._generator

    def get_model_container(self):
        if self._model_container is not None:
            return self._model_container

        generator = self._get_generator()
        model_container = getattr(generator, "model_container", None)
        if model_container is None:
            raise RuntimeError("Generator does not expose a model_container")
        return model_container

    def _build_sd_run(self, request: dict):
        if self._sd_run_factory is not None:
            return self._sd_run_factory(request)

        _, _, get_sd_run_from_dict = _load_generator_dependencies()
        return get_sd_run_from_dict(request)

    def _make_output_path(self, prompt: str) -> Path:
        stem = "".join(filter(str.isalnum, prompt[:30])) or "image"
        return self.output_dir / f"{stem}_{self.random_int(0, 100000000)}.png"

    def generate_images(
        self,
        request: dict,
        *,
        progress_callback: ProgressCallback | None = None,
    ) -> GenerationResult:
        if "prompt" not in request or not str(request["prompt"]).strip():
            raise ValueError("prompt must not be empty")

        self._progress_callback = progress_callback
        generator = self._get_generator()
        sd_run = self._build_sd_run(request)
        total_images = int(request.get("num_imgs", 1) or 1)
        images: list[GeneratedImage] = []

        for image_index in range(total_images):
            sd_run.img_id = image_index
            outs = generator.generate(sd_run)
            if outs is None or outs.get("img") is None:
                break

            for image_array in outs["img"]:
                output_path = self._make_output_path(str(request["prompt"]))
                self.image_writer(image_array, str(output_path))
                images.append(
                    GeneratedImage(
                        generated_img_path=str(output_path),
                        aux_output_image_path=outs.get("aux_img"),
                    )
                )

        return GenerationResult(images=images)

    def convert_model(self, checkpoint_path: str, output_path: str) -> dict:
        if not checkpoint_path.strip():
            raise ValueError("checkpoint_path must not be empty")
        if not output_path.strip():
            raise ValueError("output_path must not be empty")

        convert_model = _load_convert_model()
        result = convert_model(checkpoint_path, output_path)
        if result is None:
            return {"output_path": output_path}
        return result


def generation_result_payload(result: GenerationResult) -> dict:
    return {"images": [asdict(image) for image in result.images]}
