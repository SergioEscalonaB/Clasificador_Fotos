import pytest
from PySide6.QtWidgets import QApplication
from clasificador.ui.lucide_icons import build_svg_xml, get_lucide_pixmap, get_lucide_icon, LUCIDE_PATHS


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_build_svg_xml():
    xml = build_svg_xml("folder", color="#2563eb", stroke_width=2.5)
    assert '<svg' in xml
    assert 'stroke="#2563eb"' in xml
    assert 'stroke-width="2.5"' in xml
    assert 'viewBox="0 0 24 24"' in xml


def test_get_lucide_pixmap_and_icon(qapp):
    for icon_name in ["folder", "play", "plus", "pencil", "trash", "skip-forward", "undo", "image"]:
        pixmap = get_lucide_pixmap(icon_name, size=24)
        assert pixmap is not None
        assert not pixmap.isNull()
        assert pixmap.width() == 24
        assert pixmap.height() == 24

        icon = get_lucide_icon(icon_name, size=20)
        assert icon is not None
        assert not icon.isNull()
