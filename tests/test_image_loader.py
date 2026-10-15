import sys
import pytest
from pathlib import Path
from PIL import Image
from PySide6.QtWidgets import QApplication

from clasificador.core.image_loader import load_image_with_exif


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_load_valid_rgb_image(tmp_path, qapp):
    img_path = tmp_path / "test.jpg"
    im = Image.new("RGB", (200, 100), color="blue")
    im.save(str(img_path))

    pixmap, err, meta = load_image_with_exif(img_path)
    assert err is None
    assert pixmap is not None
    assert not pixmap.isNull()
    assert meta["width"] == 200
    assert meta["height"] == 100
    assert meta["format"].upper() == "JPEG"


def test_load_valid_rgba_image(tmp_path, qapp):
    img_path = tmp_path / "test_alpha.png"
    im = Image.new("RGBA", (80, 120), color=(255, 0, 0, 128))
    im.save(str(img_path))

    pixmap, err, meta = load_image_with_exif(img_path)
    assert err is None
    assert pixmap is not None
    assert not pixmap.isNull()
    assert meta["width"] == 80
    assert meta["height"] == 120


def test_load_corrupted_image(tmp_path, qapp):
    bad_img = tmp_path / "corrupto.jpg"
    bad_img.write_bytes(b"esto no es una imagen jpg valida")

    pixmap, err, meta = load_image_with_exif(bad_img)
    assert pixmap is None
    assert err is not None
    assert "no reconocido o archivo corrupto" in err.lower() or "error" in err.lower()


def test_load_nonexistent_image(tmp_path, qapp):
    fake_path = tmp_path / "fantasma.png"
    pixmap, err, meta = load_image_with_exif(fake_path)
    assert pixmap is None
    assert err is not None
    assert "no existe" in err.lower()
