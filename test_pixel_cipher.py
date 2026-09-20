"""Unit tests for the PixelCrypt transformation."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from PIL import Image

from pixel_cipher import process_image, transform_image


class PixelCipherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.image = Image.new("RGBA", (8, 8))
        self.image.putdata(
            [
                ((x * 31) % 256, (y * 47) % 256, ((x + y) * 19) % 256, 80 + x * 10)
                for y in range(8)
                for x in range(8)
            ]
        )

    def test_round_trip_restores_pixels(self) -> None:
        encrypted = transform_image(self.image, "correct horse battery staple")
        decrypted = transform_image(encrypted, "correct horse battery staple")
        self.assertEqual(decrypted.tobytes(), self.image.tobytes())

    def test_encryption_changes_rgb_values(self) -> None:
        encrypted = transform_image(self.image, "demo-key")
        self.assertNotEqual(encrypted.tobytes(), self.image.tobytes())

    def test_alpha_channel_is_preserved(self) -> None:
        encrypted = transform_image(self.image, "demo-key")
        original_alpha = self.image.getchannel("A").tobytes()
        encrypted_alpha = encrypted.getchannel("A").tobytes()
        self.assertEqual(encrypted_alpha, original_alpha)

    def test_wrong_key_does_not_restore_image(self) -> None:
        encrypted = transform_image(self.image, "first-key")
        incorrect = transform_image(encrypted, "second-key")
        self.assertNotEqual(incorrect.tobytes(), self.image.tobytes())

    def test_empty_key_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            transform_image(self.image, "")

    def test_file_round_trip(self) -> None:
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            original = folder / "original.png"
            encrypted = folder / "encrypted.png"
            decrypted = folder / "decrypted.png"
            self.image.save(original)

            process_image(original, encrypted, "file-key")
            process_image(encrypted, decrypted, "file-key")

            with Image.open(decrypted) as restored:
                self.assertEqual(restored.convert("RGBA").tobytes(), self.image.tobytes())

    def test_png_output_is_required(self) -> None:
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            original = folder / "original.png"
            self.image.save(original)
            with self.assertRaises(ValueError):
                process_image(original, folder / "output.jpg", "key")


if __name__ == "__main__":
    unittest.main()
