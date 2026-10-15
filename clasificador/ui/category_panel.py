from typing import List, Dict, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QScrollArea,
    QInputDialog,
    QMessageBox,
    QFrame,
)

# Secuencia de teclas de atajo para asignar en orden
SHORTCUT_KEYS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"]


class CategoryPanel(QWidget):
    """
    Panel interactivo con los botones de categorías, atajos de teclado asignados
    y herramientas para añadir, renombrar o eliminar categorías.
    """

    category_selected = Signal(str)
    category_added = Signal(str)
    category_renamed = Signal(str, str)
    category_removed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._categories: List[str] = []
        self._shortcut_map: Dict[str, str] = {}  # Tecla -> Nombre de categoría

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Encabezado del panel
        header_layout = QHBoxLayout()
        title_label = QLabel("Categorías")
        title_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #0f172a;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        desc_label = QLabel("Haz clic o presiona el número/letra de atajo:")
        desc_label.setStyleSheet("color: #64748b; font-size: 11px;")
        desc_label.setWordWrap(True)
        main_layout.addWidget(desc_label)

        # Área con scroll para botones de categorías
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.scroll_content = QWidget()
        self.buttons_layout = QVBoxLayout(self.scroll_content)
        self.buttons_layout.setContentsMargins(0, 5, 0, 5)
        self.buttons_layout.setSpacing(6)
        self.buttons_layout.addStretch()

        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area, 1)

        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #e2e8f0;")
        main_layout.addWidget(sep)

        # Botones de gestión
        mgmt_layout = QHBoxLayout()
        mgmt_layout.setSpacing(6)

        self.btn_add = QPushButton("➕ Nueva")
        self.btn_add.setToolTip("Agregar una nueva categoría")
        self.btn_add.clicked.connect(self._on_add_category)

        self.btn_rename = QPushButton("✏️ Editar")
        self.btn_rename.setToolTip("Renombrar una categoría existente")
        self.btn_rename.clicked.connect(self._on_rename_category)

        self.btn_delete = QPushButton("🗑️ Quitar")
        self.btn_delete.setToolTip("Quitar categoría de la lista (no borra fotos)")
        self.btn_delete.clicked.connect(self._on_delete_category)

        mgmt_layout.addWidget(self.btn_add)
        mgmt_layout.addWidget(self.btn_rename)
        mgmt_layout.addWidget(self.btn_delete)
        main_layout.addLayout(mgmt_layout)

    def set_categories(self, categories: List[str]):
        """Actualiza la lista de categorías y regenera los botones y atajos."""
        self._categories = list(categories)
        self._rebuild_buttons()

    def _rebuild_buttons(self):
        # Limpiar botones anteriores
        while self.buttons_layout.count() > 1:
            item = self.buttons_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._shortcut_map.clear()

        for i, cat in enumerate(self._categories):
            shortcut = SHORTCUT_KEYS[i] if i < len(SHORTCUT_KEYS) else ""
            if shortcut:
                self._shortcut_map[shortcut.upper()] = cat

            btn = self._create_category_button(cat, shortcut)
            # Insertar antes del stretch al final
            self.buttons_layout.insertWidget(self.buttons_layout.count() - 1, btn)

    def _create_category_button(self, name: str, shortcut: str) -> QPushButton:
        btn = QPushButton()
        btn.setProperty("class", "categoryBtn")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # Layout interno del botón para mostrar texto y badge de atajo alineados
        btn_layout = QHBoxLayout(btn)
        btn_layout.setContentsMargins(10, 6, 10, 6)

        name_lbl = QLabel(name)
        name_lbl.setStyleSheet("font-weight: 600; font-size: 13px; color: #1e293b; background: transparent;")
        btn_layout.addWidget(name_lbl)
        btn_layout.addStretch()

        if shortcut:
            badge_lbl = QLabel(f"[{shortcut}]")
            badge_lbl.setStyleSheet(
                "background-color: #e2e8f0; color: #334155; font-weight: bold; "
                "border-radius: 4px; padding: 2px 6px; font-size: 11px;"
            )
            btn_layout.addWidget(badge_lbl)

        btn.clicked.connect(lambda _, c=name: self.category_selected.emit(c))
        return btn

    def get_category_for_key(self, key_text: str) -> Optional[str]:
        """Busca si la tecla presionada corresponde a un atajo de categoría."""
        return self._shortcut_map.get(key_text.upper())

    def _on_add_category(self):
        name, ok = QInputDialog.getText(
            self,
            "Nueva Categoría",
            "Introduce el nombre de la nueva categoría:",
        )
        if ok and name.strip():
            self.category_added.emit(name.strip())

    def _on_rename_category(self):
        if not self._categories:
            QMessageBox.information(self, "Aviso", "No hay categorías para editar.")
            return

        cat, ok = QInputDialog.getItem(
            self,
            "Editar Categoría",
            "Selecciona la categoría a renombrar:",
            self._categories,
            0,
            False,
        )
        if ok and cat:
            new_name, ok_name = QInputDialog.getText(
                self,
                "Renombrar Categoría",
                f"Introduce el nuevo nombre para '{cat}':",
                text=cat,
            )
            if ok_name and new_name.strip() and new_name.strip() != cat:
                self.category_renamed.emit(cat, new_name.strip())

    def _on_delete_category(self):
        if not self._categories:
            QMessageBox.information(self, "Aviso", "No hay categorías para eliminar.")
            return

        if len(self._categories) <= 1:
            QMessageBox.warning(self, "Aviso", "Debe mantenerse al menos una categoría.")
            return

        cat, ok = QInputDialog.getItem(
            self,
            "Eliminar Categoría",
            "Selecciona la categoría a quitar de la lista:",
            self._categories,
            0,
            False,
        )
        if ok and cat:
            confirm = QMessageBox.question(
                self,
                "Confirmar Eliminación",
                f"¿Deseas quitar la categoría '{cat}' de la lista de botones?\n\n"
                "Nota: Las imágenes ya clasificadas en esa carpeta NO se borrarán.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if confirm == QMessageBox.StandardButton.Yes:
                self.category_removed.emit(cat)
