"""
Estilos visuales modernos para la interfaz en PySide6.
Optimizado para Windows 10/11 con tipografía limpia y diseño visual equilibrado.
"""

import os
import tempfile


def ensure_check_icon_path() -> str:
    """
    Garantiza la existencia de un icono SVG vectorial nítido con el 'chulo' (marca de verificación)
    blanco para los selectores (QCheckBox) tanto en modo desarrollo como en el .exe compilado.
    """
    temp_dir = tempfile.gettempdir()
    icon_path = os.path.join(temp_dir, "clasificador_check_icon.svg")
    svg_content = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" '
        'fill="none" stroke="white" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round">'
        '<polyline points="20 6 9 17 4 12"/>'
        '</svg>'
    )
    try:
        with open(icon_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
    except Exception:
        pass
    return icon_path.replace("\\", "/")


def get_app_stylesheet() -> str:
    check_svg = ensure_check_icon_path()
    return f"""
QMainWindow {{
    background-color: #f4f6f9;
}}

QWidget {{
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    font-size: 13px;
    color: #1e293b;
}}

/* Encabezados y barras superiores */
#headerCard {{
    background-color: #ffffff;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
}}

#statsCard {{
    background-color: #ffffff;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
}}

#categoriesCard {{
    background-color: #ffffff;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
}}

#infoBar {{
    background-color: #ffffff;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    padding: 6px 12px;
}}

/* Campos de texto */
QLineEdit {{
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 6px 10px;
    color: #0f172a;
}}
QLineEdit:focus {{
    border: 1px solid #3b82f6;
    background-color: #f8fafc;
}}
QLineEdit:disabled {{
    background-color: #f1f5f9;
    color: #94a3b8;
}}

/* Botones principales y secundarios */
QPushButton {{
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 500;
    color: #334155;
}}
QPushButton:hover {{
    background-color: #f8fafc;
    border-color: #94a3b8;
}}
QPushButton:pressed {{
    background-color: #f1f5f9;
}}
QPushButton:disabled {{
    background-color: #f1f5f9;
    color: #cbd5e1;
    border-color: #e2e8f0;
}}

/* Botones primarios (Acción principal) */
QPushButton#primaryButton {{
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    font-weight: 600;
    padding: 8px 18px;
}}
QPushButton#primaryButton:hover {{
    background-color: #1d4ed8;
}}
QPushButton#primaryButton:pressed {{
    background-color: #1e40af;
}}

/* Botón Saltar */
QPushButton#skipButton {{
    background-color: #f1f5f9;
    color: #475569;
    border: 1px solid #cbd5e1;
    font-weight: 500;
}}
QPushButton#skipButton:hover {{
    background-color: #e2e8f0;
    color: #1e293b;
}}

/* Botón Deshacer */
QPushButton#undoButton {{
    background-color: #fff7ed;
    color: #c2410c;
    border: 1px solid #fed7aa;
    font-weight: 600;
}}
QPushButton#undoButton:hover {{
    background-color: #ffedd5;
    border-color: #fdba74;
}}
QPushButton#undoButton:disabled {{
    background-color: #f8fafc;
    color: #cbd5e1;
    border-color: #e2e8f0;
}}

/* Botones de Categorías */
QPushButton.categoryBtn {{
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 14px;
    font-weight: 600;
    color: #1e293b;
    text-align: left;
}}
QPushButton.categoryBtn:hover {{
    background-color: #eff6ff;
    border-color: #3b82f6;
    color: #1d4ed8;
}}
QPushButton.categoryBtn:pressed {{
    background-color: #dbeafe;
}}

/* Atajo visual (Badge) */
QLabel.shortcutBadge {{
    background-color: #e2e8f0;
    color: #334155;
    font-weight: bold;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 11px;
}}

/* Barra de progreso */
QProgressBar {{
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    background-color: #e2e8f0;
    height: 14px;
    text-align: center;
    font-size: 11px;
    font-weight: 600;
    color: #1e293b;
}}
QProgressBar::chunk {{
    background-color: #10b981;
    border-radius: 5px;
}}

/* Casillas de selección (Checkboxes) con icono visible al seleccionar */
QCheckBox {{
    spacing: 8px;
    font-size: 13px;
    color: #334155;
    font-weight: 500;
}}
QCheckBox::indicator {{
    width: 19px;
    height: 19px;
    border-radius: 5px;
    border: 1.5px solid #94a3b8;
    background-color: #ffffff;
}}
QCheckBox::indicator:hover {{
    border-color: #2563eb;
    background-color: #f8fafc;
}}
QCheckBox::indicator:checked {{
    background-color: #2563eb;
    border-color: #2563eb;
    image: url({check_svg});
}}
QCheckBox::indicator:checked:hover {{
    background-color: #1d4ed8;
    border-color: #1d4ed8;
}}

/* Scroll area */
QScrollArea {{
    border: none;
    background-color: transparent;
}}

/* Tooltips */
QToolTip {{
    background-color: #0f172a;
    color: #f8fafc;
    border: none;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
}}
"""


APP_STYLESHEET = get_app_stylesheet()
