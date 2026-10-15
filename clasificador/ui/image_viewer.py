from typing import Optional
from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import QPainter, QPixmap, QColor, QFont, QPen
from PySide6.QtWidgets import QWidget, QSizePolicy


class ImageViewer(QWidget):
    """
    Visor de imágenes optimizado que escala la imagen dinámicamente preservando
    su relación de aspecto original sin deformaciones ni consumo excesivo de memoria.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap: Optional[QPixmap] = None
        self._error_message: Optional[str] = None
        self._placeholder_message: str = "Selecciona las carpetas para comenzar."

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(400, 300)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)

    def set_image(self, pixmap: Optional[QPixmap]):
        """Establece la imagen actual a mostrar."""
        self._pixmap = pixmap
        self._error_message = None
        self.update()

    def set_error(self, message: str):
        """Establece un mensaje de error si la imagen no se pudo cargar."""
        self._pixmap = None
        self._error_message = message
        self.update()

    def set_placeholder(self, message: str):
        """Establece el texto guía cuando no hay imagen activa."""
        self._pixmap = None
        self._error_message = None
        self._placeholder_message = message
        self.update()

    def clear(self):
        """Limpia el visor."""
        self._pixmap = None
        self._error_message = None
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        rect = self.rect()

        # Fondo del visor (un tono gris neutro profesional para resaltar fotos)
        painter.fillRect(rect, QColor("#1e293b"))

        # Caso 1: Hay imagen válida
        if self._pixmap and not self._pixmap.isNull():
            # Escalar manteniendo la relación de aspecto exacta
            scaled = self._pixmap.scaled(
                rect.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )

            # Centrar dentro del área disponible
            x = rect.x() + (rect.width() - scaled.width()) // 2
            y = rect.y() + (rect.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)

        # Caso 2: Hubo error al cargar la imagen
        elif self._error_message:
            self._draw_message_card(
                painter,
                rect,
                title="⚠️ No se pudo abrir la imagen",
                subtitle=self._error_message,
                hint="Presiona 'Saltar' (Espacio) o 'Siguiente' para continuar.",
                is_error=True,
            )

        # Caso 3: Estado inicial o completado
        else:
            self._draw_message_card(
                painter,
                rect,
                title="📷 Visor de Fotos",
                subtitle=self._placeholder_message,
                hint="Selecciona la carpeta origen y presiona 'Cargar imágenes'.",
                is_error=False,
            )

    def _draw_message_card(self, painter: QPainter, rect: QRect, title: str, subtitle: str, hint: str, is_error: bool):
        """Dibuja una tarjeta con mensaje centrado amigable."""
        card_width = min(500, rect.width() - 40)
        card_height = 180
        card_x = rect.x() + (rect.width() - card_width) // 2
        card_y = rect.y() + (rect.height() - card_height) // 2

        card_rect = QRect(card_x, card_y, card_width, card_height)

        # Fondo tarjeta
        painter.setPen(QPen(QColor("#ef4444" if is_error else "#475569"), 1))
        painter.setBrush(QColor("#0f172a"))
        painter.drawRoundedRect(card_rect, 10, 10)

        # Título
        title_font = QFont("Segoe UI", 14, QFont.Weight.Bold)
        painter.setFont(title_font)
        painter.setPen(QColor("#f87171" if is_error else "#e2e8f0"))
        title_rect = QRect(card_x + 20, card_y + 20, card_width - 40, 30)
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, title)

        # Subtítulo (detalle)
        sub_font = QFont("Segoe UI", 11)
        painter.setFont(sub_font)
        painter.setPen(QColor("#cbd5e1"))
        sub_rect = QRect(card_x + 20, card_y + 55, card_width - 40, 50)
        painter.drawText(sub_rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, subtitle)

        # Consejo / Hint
        hint_font = QFont("Segoe UI", 10, QFont.Weight.Medium)
        painter.setFont(hint_font)
        painter.setPen(QColor("#94a3b8"))
        hint_rect = QRect(card_x + 20, card_y + 115, card_width - 40, 30)
        painter.drawText(hint_rect, Qt.AlignmentFlag.AlignCenter, hint)
