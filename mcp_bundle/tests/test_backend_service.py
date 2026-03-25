from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from backends.stable_diffusion.service import (
    DiffusionBeeService,
    GenerationResult,
    GeneratedImage,
    generation_result_payload,
)


class FakeGenerator:
    def __init__(self, callback):
        self.callback = callback
        self.calls = []
        self.model_container = object()

    def generate(self, sd_run):
        self.calls.append(sd_run.img_id)
        self.callback("Generating", 50.0)
        return {"img": [object()], "aux_img": "/tmp/aux.png"}


class BackendServiceTests(unittest.TestCase):
    def test_generation_result_payload_serializes_images(self) -> None:
        payload = generation_result_payload(
            GenerationResult(images=[GeneratedImage(generated_img_path="/tmp/out.png")])
        )

        self.assertEqual(
            payload,
            {"images": [{"generated_img_path": "/tmp/out.png", "aux_output_image_path": None}]},
        )

    def test_generate_images_saves_outputs_and_reports_progress(self) -> None:
        written_paths: list[str] = []
        progress_events: list[tuple[str, float]] = []

        def image_writer(_image, output_path: str) -> None:
            written_paths.append(output_path)

        with tempfile.TemporaryDirectory() as temp_dir:
            service = DiffusionBeeService(
                output_dir=temp_dir,
                image_writer=image_writer,
                random_int=lambda _a, _b: 42,
                generator_factory=lambda callback: FakeGenerator(callback),
                sd_run_factory=lambda _request: SimpleNamespace(img_id=None),
            )

            result = service.generate_images(
                {"prompt": "hello world", "num_imgs": 2},
                progress_callback=lambda state, progress: progress_events.append((state, progress)),
            )

        self.assertEqual(len(result.images), 2)
        self.assertEqual(len(written_paths), 2)
        self.assertTrue(all(path.endswith("helloworld_42.png") for path in written_paths))
        self.assertEqual(progress_events, [("Generating", 50.0), ("Generating", 50.0)])

    @mock.patch("backends.stable_diffusion.service._load_convert_model")
    def test_convert_model_delegates_to_converter(self, load_convert_model: mock.Mock) -> None:
        load_convert_model.return_value = mock.Mock(
            return_value={"output_path": "/tmp/model.tdict", "model_metadata": {"type": "sd_model"}}
        )
        service = DiffusionBeeService(output_dir=Path("/tmp"))

        payload = service.convert_model("/tmp/in.ckpt", "/tmp/model.tdict")

        load_convert_model.return_value.assert_called_once_with("/tmp/in.ckpt", "/tmp/model.tdict")
        self.assertEqual(payload["model_metadata"]["type"], "sd_model")


if __name__ == "__main__":
    unittest.main()
