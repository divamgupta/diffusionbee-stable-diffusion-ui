from __future__ import annotations

import unittest
from unittest import mock

from mcp_bundle.server.service import (
    BundleStatus,
    bundle_status_payload,
    convert_model,
    generate_image,
)


class BundleStatusPayloadTests(unittest.TestCase):
    def test_bundle_status_payload_serializes_dataclass(self) -> None:
        status = BundleStatus(
            implementation_status="experimental",
            bundle_root="/tmp/bundle",
            backend_root="/tmp/backend",
            notes=["note-1", "note-2"],
        )

        payload = bundle_status_payload(status)

        self.assertEqual(
            payload,
            {
                "implementation_status": "experimental",
                "bundle_root": "/tmp/bundle",
                "backend_root": "/tmp/backend",
                "notes": ["note-1", "note-2"],
            },
        )


class GenerateImageTests(unittest.TestCase):
    def test_generate_image_rejects_empty_prompt(self) -> None:
        with self.assertRaisesRegex(ValueError, "prompt must not be empty"):
            generate_image(
                prompt="   ",
                negative_prompt="",
                width=512,
                height=512,
                steps=25,
                guidance_scale=7.5,
                seed=0,
                num_images=1,
                model_tdict_path="",
            )

    @mock.patch("mcp_bundle.server.service._get_backend_service")
    def test_generate_image_forwards_request_to_backend_service(self, get_backend_service: mock.Mock) -> None:
        backend_service = get_backend_service.return_value
        backend_service.generate_images.return_value = mock.Mock(
            images=[mock.Mock(generated_img_path="/tmp/out.png", aux_output_image_path=None)]
        )

        with mock.patch(
            "mcp_bundle.server.service.generation_result_payload",
            return_value={"images": [{"generated_img_path": "/tmp/out.png", "aux_output_image_path": None}]},
        ):
            payload = generate_image(
                prompt="a lighthouse in fog",
                negative_prompt="low quality",
                width=640,
                height=768,
                steps=30,
                guidance_scale=8.0,
                seed=123,
                num_images=2,
                model_tdict_path="/models/default.tdict",
            )

        backend_service.generate_images.assert_called_once_with(
            {
                "prompt": "a lighthouse in fog",
                "negative_prompt": "low quality",
                "img_width": 640,
                "img_height": 768,
                "num_steps": 30,
                "guidance_scale": 8.0,
                "seed": 123,
                "num_imgs": 2,
                "model_tdict_path": "/models/default.tdict",
            }
        )
        self.assertEqual(payload["images"][0]["generated_img_path"], "/tmp/out.png")
        self.assertEqual(payload["request"]["img_width"], 640)


class ConvertModelTests(unittest.TestCase):
    def test_convert_model_requires_checkpoint_path(self) -> None:
        with self.assertRaisesRegex(ValueError, "checkpoint_path must not be empty"):
            convert_model(checkpoint_path=" ", output_path="/tmp/out")

    def test_convert_model_requires_output_path(self) -> None:
        with self.assertRaisesRegex(ValueError, "output_path must not be empty"):
            convert_model(checkpoint_path="/tmp/in.ckpt", output_path=" ")

    @mock.patch("mcp_bundle.server.service._get_backend_service")
    def test_convert_model_delegates_to_backend_service(self, get_backend_service: mock.Mock) -> None:
        backend_service = get_backend_service.return_value
        backend_service.convert_model.return_value = {"output_path": "/tmp/model.tdict"}

        payload = convert_model(
            checkpoint_path="/tmp/model.ckpt",
            output_path="/tmp/model.tdict",
        )

        backend_service.convert_model.assert_called_once_with(
            "/tmp/model.ckpt",
            "/tmp/model.tdict",
        )
        self.assertEqual(payload["output_path"], "/tmp/model.tdict")


if __name__ == "__main__":
    unittest.main()
