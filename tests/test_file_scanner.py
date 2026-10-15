import os
import pytest
from pathlib import Path

from clasificador.core.file_scanner import scan_images, is_supported_image, natural_sort_key


def test_is_supported_image():
    assert is_supported_image("foto.jpg")
    assert is_supported_image("imagen.JPEG")
    assert is_supported_image("foto.png")
    assert is_supported_image("foto.bmp")
    assert is_supported_image("foto.gif")
    assert is_supported_image("foto.tiff")
    assert is_supported_image("foto.tif")
    assert is_supported_image("foto.webp")
    assert not is_supported_image("documento.pdf")
    assert not is_supported_image("script.py")
    assert not is_supported_image("datos.json")


def test_natural_sort():
    filenames = ["foto10.jpg", "foto2.jpg", "foto1.jpg", "foto20.jpg"]
    sorted_files = sorted(filenames, key=natural_sort_key)
    assert sorted_files == ["foto1.jpg", "foto2.jpg", "foto10.jpg", "foto20.jpg"]


def test_scan_images_flat_and_recursive(tmp_path):
    # Crear estructura de prueba
    root_img1 = tmp_path / "img1.jpg"
    root_img2 = tmp_path / "img2.PNG"
    root_txt = tmp_path / "readme.txt"
    root_img1.write_text("dummy")
    root_img2.write_text("dummy")
    root_txt.write_text("ignore me")

    sub_dir = tmp_path / "subcarpeta"
    sub_dir.mkdir()
    sub_img = sub_dir / "img3.webp"
    sub_img.write_text("dummy")

    # Escaneo sin recursividad
    flat_results = scan_images(tmp_path, recursive=False)
    flat_names = [os.path.basename(p) for p in flat_results]
    assert "img1.jpg" in flat_names
    assert "img2.PNG" in flat_names
    assert "img3.webp" not in flat_names
    assert "readme.txt" not in flat_names
    assert len(flat_results) == 2

    # Escaneo con recursividad
    rec_results = scan_images(tmp_path, recursive=True)
    rec_names = [os.path.basename(p) for p in rec_results]
    assert "img1.jpg" in rec_names
    assert "img2.PNG" in rec_names
    assert "img3.webp" in rec_names
    assert "readme.txt" not in rec_names
    assert len(rec_results) == 3


def test_scan_empty_directory(tmp_path):
    empty_dir = tmp_path / "vacia"
    empty_dir.mkdir()
    assert scan_images(empty_dir) == []
    assert scan_images(tmp_path / "inexistente") == []
