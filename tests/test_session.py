import os
import json
import pytest
from pathlib import Path

from clasificador.core.session_manager import SessionManager, PROGRESS_FILENAME


def test_session_lifecycle_and_persistence(tmp_path):
    src_dir = tmp_path / "fotos_origen"
    src_dir.mkdir()
    dst_dir = tmp_path / "fotos_destino"
    dst_dir.mkdir()

    # Crear 3 imágenes de prueba
    (src_dir / "foto1.jpg").write_text("foto 1")
    (src_dir / "foto2.jpg").write_text("foto 2")
    (src_dir / "foto3.jpg").write_text("foto 3")

    session = SessionManager()
    total = session.initialize_session(
        source_folder=str(src_dir),
        destination_folder=str(dst_dir),
        recursive=False,
        move_mode=False,
        categories=["Familia", "Trabajo"],
    )

    assert total == 3
    assert session.current_index == 0

    stats = session.get_stats()
    assert stats["total"] == 3
    assert stats["pending"] == 3
    assert stats["classified"] == 0
    assert stats["skipped"] == 0

    # 1. Clasificar primera foto
    ok, err = session.classify_current("Familia")
    assert ok is True
    assert err is None

    # Verificar avance automático a la siguiente
    assert session.current_index == 1
    stats = session.get_stats()
    assert stats["classified"] == 1
    assert stats["pending"] == 2

    # Verificar que el archivo JSON de progreso se creó en destino
    progress_file = dst_dir / PROGRESS_FILENAME
    assert progress_file.exists()

    # 2. Saltar segunda foto
    skip_ok = session.skip_current()
    assert skip_ok is True
    assert session.current_index == 2
    stats = session.get_stats()
    assert stats["skipped"] == 1
    assert stats["pending"] == 1

    # 3. Deshacer última acción (revertir salto)
    undo_ok, undo_err = session.undo_last()
    assert undo_ok is True
    assert session.current_index == 1  # Volvió a la foto 2
    stats = session.get_stats()
    assert stats["skipped"] == 0
    assert stats["pending"] == 2

    # 4. Deshacer clasificación de foto 1
    undo_ok, undo_err = session.undo_last()
    assert undo_ok is True
    assert session.current_index == 0  # Volvió a foto 1
    stats = session.get_stats()
    assert stats["classified"] == 0
    assert stats["pending"] == 3

    # Verificar que en la carpeta 'Familia' ya no está la copia
    familia_dir = dst_dir / "Familia"
    if familia_dir.exists():
        assert len(list(familia_dir.iterdir())) == 0


def test_resume_existing_session(tmp_path):
    src_dir = tmp_path / "fotos_origen"
    src_dir.mkdir()
    dst_dir = tmp_path / "fotos_destino"
    dst_dir.mkdir()

    f1 = src_dir / "a.jpg"
    f2 = src_dir / "b.jpg"
    f3 = src_dir / "c.jpg"
    f1.write_text("a")
    f2.write_text("b")
    f3.write_text("c")

    # Sesión 1: Clasificar 'a.jpg' en 'Mami'
    session1 = SessionManager()
    session1.initialize_session(
        source_folder=str(src_dir),
        destination_folder=str(dst_dir),
        categories=["Mami", "Papi"],
    )
    ok, _ = session1.classify_current("Mami")
    assert ok is True
    assert session1.get_stats()["classified"] == 1

    # Simular cierre y reapertura con nueva instancia
    assert SessionManager.has_existing_session(str(dst_dir)) is True
    summary = SessionManager.read_session_summary(str(dst_dir))
    assert summary["classified"] == 1
    assert summary["total"] == 3

    session2 = SessionManager()
    session2.initialize_session(
        source_folder=str(src_dir),
        destination_folder=str(dst_dir),
        resume_existing=True,
    )

    stats2 = session2.get_stats()
    assert stats2["total"] == 3
    assert stats2["classified"] == 1
    assert stats2["pending"] == 2
    # El current_index debe apuntar a la primera pendiente (b.jpg, índice 1)
    assert session2.current_index == 1
    curr = session2.get_current_item()
    assert curr["src_path"] == str(f2)


def test_category_management_safety(tmp_path):
    src_dir = tmp_path / "fotos_origen"
    src_dir.mkdir()
    dst_dir = tmp_path / "fotos_destino"
    dst_dir.mkdir()

    (src_dir / "foto.jpg").write_text("dummy")

    session = SessionManager()
    session.initialize_session(str(src_dir), str(dst_dir), categories=["CatA", "CatB"])

    # Clasificar en CatA
    session.classify_current("CatA")

    # Renombrar CatA a CatNueva
    ok, err = session.rename_category("CatA", "CatNueva")
    assert ok is True
    assert "CatNueva" in session.categories
    assert "CatA" not in session.categories

    # Verificar que el ítem ahora referencia la nueva categoría
    assert session.items[0]["category"] == "CatNueva"

    # Eliminar CatB
    ok_del, _ = session.remove_category("CatB")
    assert ok_del is True
    assert "CatB" not in session.categories

    # Permitir eliminar la categoría dejando la lista limpia
    ok_last, err_last = session.remove_category("CatNueva")
    assert ok_last is True
    assert len(session.categories) == 0
    assert err_last is None
