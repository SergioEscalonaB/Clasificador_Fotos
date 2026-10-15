import os
import pytest
from pathlib import Path

from clasificador.core.file_ops import (
    sanitize_category_name,
    get_unique_destination_path,
    classify_file,
    undo_classification,
)


def test_sanitize_category_name():
    assert sanitize_category_name("Mami") == "Mami"
    assert sanitize_category_name("Obras: 2024 / Terminadas?") == "Obras_ 2024 _ Terminadas_"
    assert sanitize_category_name('Fotos*<Familia>|"Nueva"') == "Fotos__Familia___Nueva_"
    assert sanitize_category_name("   ") == "Sin_Categoria"


def test_get_unique_destination_path(tmp_path):
    dest_dir = tmp_path / "categoria"
    dest_dir.mkdir()

    # Primer archivo no existe aún -> usa nombre directo
    p1 = get_unique_destination_path(dest_dir, "foto.jpg")
    assert p1.name == "foto.jpg"

    # Si se crea el archivo 'foto.jpg', el siguiente debe ser 'foto (1).jpg'
    p1.write_text("dummy 1")
    p2 = get_unique_destination_path(dest_dir, "foto.jpg")
    assert p2.name == "foto (1).jpg"

    # Si se crea 'foto (1).jpg', el siguiente debe ser 'foto (2).jpg'
    p2.write_text("dummy 2")
    p3 = get_unique_destination_path(dest_dir, "foto.jpg")
    assert p3.name == "foto (2).jpg"


def test_classify_copy_mode(tmp_path):
    src_dir = tmp_path / "origen"
    src_dir.mkdir()
    dst_dir = tmp_path / "destino"
    dst_dir.mkdir()

    src_file = src_dir / "retrato.jpg"
    src_file.write_text("contenido original")

    # Copiar archivo a categoría 'Familia'
    success, final_dest, err = classify_file(
        src_path=src_file,
        dest_root_dir=dst_dir,
        category_name="Familia",
        move_file=False,
    )

    assert success is True
    assert err is None
    assert final_dest is not None

    # Verificar que el original sigue intacto (modo copia)
    assert src_file.exists()
    assert src_file.read_text() == "contenido original"

    # Verificar que se creó en la subcarpeta de categoría
    dest_path = Path(final_dest)
    assert dest_path.exists()
    assert dest_path.parent.name == "Familia"
    assert dest_path.read_text() == "contenido original"


def test_classify_move_mode(tmp_path):
    src_dir = tmp_path / "origen"
    src_dir.mkdir()
    dst_dir = tmp_path / "destino"
    dst_dir.mkdir()

    src_file = src_dir / "paisaje.png"
    src_file.write_text("contenido para mover")

    # Mover archivo a categoría 'Viajes'
    success, final_dest, err = classify_file(
        src_path=src_file,
        dest_root_dir=dst_dir,
        category_name="Viajes",
        move_file=True,
    )

    assert success is True
    assert err is None
    assert final_dest is not None

    # En modo mover, el original ya no debe existir en origen
    assert not src_file.exists()

    # Debe existir en la subcarpeta de categoría
    dest_path = Path(final_dest)
    assert dest_path.exists()
    assert dest_path.parent.name == "Viajes"
    assert dest_path.read_text() == "contenido para mover"


def test_undo_copy(tmp_path):
    src_dir = tmp_path / "origen"
    src_dir.mkdir()
    dst_dir = tmp_path / "destino"
    dst_dir.mkdir()

    src_file = src_dir / "foto.jpg"
    src_file.write_text("original")

    success, final_dest, _ = classify_file(src_file, dst_dir, "Familia", move_file=False)
    assert success is True
    assert Path(final_dest).exists()

    # Revertir
    action = {
        "operation": "copy",
        "src_path": str(src_file),
        "dest_path": final_dest,
    }
    undo_ok, undo_err = undo_classification(action)
    assert undo_ok is True
    assert undo_err is None

    # La copia en destino debe haber sido eliminada
    assert not Path(final_dest).exists()
    # El archivo original debe seguir intacto
    assert src_file.exists()


def test_undo_move(tmp_path):
    src_dir = tmp_path / "origen"
    src_dir.mkdir()
    dst_dir = tmp_path / "destino"
    dst_dir.mkdir()

    src_file = src_dir / "foto_a_mover.jpg"
    src_file.write_text("contenido valioso")

    success, final_dest, _ = classify_file(src_file, dst_dir, "Familia", move_file=True)
    assert success is True
    assert not src_file.exists()
    assert Path(final_dest).exists()

    # Revertir movimiento
    action = {
        "operation": "move",
        "src_path": str(src_file),
        "dest_path": final_dest,
    }
    undo_ok, undo_err = undo_classification(action)
    assert undo_ok is True
    assert undo_err is None

    # El archivo debe haber regresado a su ruta de origen original
    assert src_file.exists()
    assert src_file.read_text() == "contenido valioso"
    assert not Path(final_dest).exists()


def test_classify_nonexistent_file(tmp_path):
    dst_dir = tmp_path / "destino"
    dst_dir.mkdir()
    fake_file = tmp_path / "no_existe.jpg"

    success, final_dest, err = classify_file(fake_file, dst_dir, "Test", move_file=False)
    assert success is False
    assert final_dest is None
    assert "no existe" in err.lower()
