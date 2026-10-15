"""
Proveedor de iconos lineales estilo Lucide en formato vectorial SVG para PySide6.
Renderiza iconos nítidos en cualquier resolución y color sin dependencias pesadas.
"""

from typing import Dict, Optional
from PySide6.QtCore import QByteArray, QSize, Qt
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer

LUCIDE_PATHS: Dict[str, str] = {
    "folder": '<path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"/>',
    "play": '<polygon points="5 3 19 12 5 21 5 3"/>',
    "plus": '<path d="M5 12h14"/><path d="M12 5v14"/>',
    "pencil": '<path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/>',
    "trash": '<path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/>',
    "chevron-left": '<path d="m15 18-6-6 6-6"/>',
    "chevron-right": '<path d="m9 18 6-6-6-6"/>',
    "skip-forward": '<polygon points="5 4 15 12 5 20 5 4"/><line x1="19" x2="19" y1="5" y2="19"/>',
    "undo": '<path d="M9 14 4 9l5-5"/><path d="M4 9h10.5a5.5 5.5 0 0 1 5.5 5.5v0a5.5 5.5 0 0 1-5.5 5.5H11"/>',
    "check-circle": '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "fast-forward": '<polygon points="13 19 22 12 13 5 13 19"/><polygon points="2 19 11 12 2 5 2 19"/>',
    "alert-circle": '<circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/>',
    "image": '<rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>',
    "keyboard": '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="M6 8h.001"/><path d="M10 8h.001"/><path d="M14 8h.001"/><path d="M18 8h.001"/><path d="M8 12h.001"/><path d="M12 12h.001"/><path d="M16 12h.001"/><path d="M7 16h10"/>',
    "tag": '<path d="M12 2H2v10l9.29 9.29c.94.94 2.48.94 3.42 0l6.58-6.58c.94-.94.94-2.48 0-3.42L12 2Z"/><path d="M7 7h.01"/>',
}


def build_svg_xml(name: str, color: str = "#334155", stroke_width: float = 2.0) -> str:
    """Genera el contenido XML completo de un SVG de Lucide con color dinámico."""
    inner_path = LUCIDE_PATHS.get(name, LUCIDE_PATHS["image"])
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" '
        f'fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round">'
        f'{inner_path}'
        f'</svg>'
    )


def get_lucide_pixmap(name: str, color: str = "#334155", size: int = 24) -> QPixmap:
    """Renderiza un icono Lucide como QPixmap de alta resolución."""
    svg_str = build_svg_xml(name, color=color)
    renderer = QSvgRenderer(QByteArray(svg_str.encode("utf-8")))

    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    renderer.render(painter)
    painter.end()

    return pixmap


def get_lucide_icon(name: str, color: str = "#334155", size: int = 20) -> QIcon:
    """Genera un QIcon de PySide6 a partir de un icono lineal de Lucide."""
    pixmap = get_lucide_pixmap(name, color=color, size=size)
    return QIcon(pixmap)
