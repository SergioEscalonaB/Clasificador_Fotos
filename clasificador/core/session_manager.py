import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from clasificador.core.file_ops import classify_file, undo_classification, sanitize_category_name
from clasificador.core.file_scanner import scan_images

PROGRESS_FILENAME = "clasificador_progreso.json"

DEFAULT_CATEGORIES = []



class SessionManager:
    """
    Gestiona el estado completo de la sesión de clasificación, historial de deshacer y persistencia en JSON.
    """

    def __init__(self):
        self.source_folder: str = ""
        self.destination_folder: str = ""
        self.recursive_scan: bool = True
        self.move_mode: bool = False
        self.categories: List[str] = list(DEFAULT_CATEGORIES)
        
        # Lista de ítems: cada uno es un dict con:
        # { "src_path": str, "status": "pending"|"classified"|"skipped", "category": str|None, "dest_path": str|None, "updated_at": float }
        self.items: List[Dict[str, Any]] = []
        
        # Índice actual en la lista de items (0 a len(items)-1)
        self.current_index: int = 0
        
        # Pila de historial para Deshacer
        # { "action": "classify"|"skip", "index": int, "previous_status": str, "src_path": str, "dest_path": str|None, "operation": "copy"|"move", "category": str|None }
        self.history: List[Dict[str, Any]] = []

    @classmethod
    def get_progress_filepath(cls, dest_dir: str | Path) -> Path:
        """Devuelve la ruta al archivo de progreso dentro del directorio de destino."""
        return Path(dest_dir) / PROGRESS_FILENAME

    @classmethod
    def has_existing_session(cls, dest_dir: str | Path) -> bool:
        """Verifica si ya existe un archivo de progreso válido en la carpeta de destino."""
        if not dest_dir:
            return False
        p = cls.get_progress_filepath(dest_dir)
        return p.is_file()

    @classmethod
    def read_session_summary(cls, dest_dir: str | Path) -> Optional[Dict[str, Any]]:
        """Lee un resumen rápido de la sesión existente sin cargarla por completo."""
        filepath = cls.get_progress_filepath(dest_dir)
        if not filepath.is_file():
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            items = data.get("items", [])
            total = len(items)
            classified = sum(1 for it in items if it.get("status") == "classified")
            skipped = sum(1 for it in items if it.get("status") == "skipped")
            pending = total - classified - skipped
            return {
                "source_folder": data.get("source_folder", ""),
                "destination_folder": data.get("destination_folder", ""),
                "total": total,
                "classified": classified,
                "pending": pending,
                "skipped": skipped,
                "categories": data.get("categories", []),
                "move_mode": data.get("move_mode", False),
            }
        except Exception:
            return None

    def initialize_session(
        self,
        source_folder: str,
        destination_folder: str,
        recursive: bool = True,
        move_mode: bool = False,
        categories: Optional[List[str]] = None,
        resume_existing: bool = True,
    ) -> int:
        """
        Inicia o reanuda una sesión de clasificación.
        
        Args:
            source_folder: Carpeta origen con las imágenes.
            destination_folder: Carpeta destino para organizar.
            recursive: Si busca recursivamente en subcarpetas de origen.
            move_mode: Si mueve en vez de copiar.
            categories: Lista opcional de categorías.
            resume_existing: Si busca y respeta clasificaciones previas guardadas en destino.
            
        Returns:
            Número total de imágenes disponibles.
        """
        self.source_folder = os.path.abspath(source_folder)
        self.destination_folder = os.path.abspath(destination_folder)
        self.recursive_scan = recursive
        self.move_mode = move_mode
        self.history = []

        if categories:
            self.categories = list(categories)

        # Escanear imágenes de origen
        scanned_paths = scan_images(self.source_folder, recursive=self.recursive_scan)
        
        # Mapeo de progreso previo si existe
        existing_items_map: Dict[str, Dict[str, Any]] = {}
        if resume_existing and self.has_existing_session(self.destination_folder):
            try:
                progress_file = self.get_progress_filepath(self.destination_folder)
                with open(progress_file, "r", encoding="utf-8") as f:
                    saved_data = json.load(f)
                    
                # Restaurar categorías guardadas si no se especificaron nuevas
                if not categories and saved_data.get("categories"):
                    self.categories = saved_data["categories"]
                    
                for it in saved_data.get("items", []):
                    src = it.get("src_path")
                    if src:
                        existing_items_map[os.path.abspath(src)] = it
                        
            except Exception:
                # Si el archivo está corrupto, continuar escaneando en limpio
                pass

        # Construir lista combinada
        self.items = []
        for path in scanned_paths:
            abs_path = os.path.abspath(path)
            if abs_path in existing_items_map:
                # Mantener estado previo
                prev = existing_items_map[abs_path]
                self.items.append({
                    "src_path": abs_path,
                    "status": prev.get("status", "pending"),
                    "category": prev.get("category"),
                    "dest_path": prev.get("dest_path"),
                    "updated_at": prev.get("updated_at", time.time()),
                })
            else:
                self.items.append({
                    "src_path": abs_path,
                    "status": "pending",
                    "category": None,
                    "dest_path": None,
                    "updated_at": None,
                })

        # Posicionarse en la primera imagen pendiente
        self.current_index = 0
        self.seek_first_pending_or_start()

        # Guardar estado inicial
        self.save_progress()
        return len(self.items)

    def seek_first_pending_or_start(self):
        """Posiciona current_index en la primera imagen que esté pendiente."""
        for i, item in enumerate(self.items):
            if item.get("status") == "pending":
                self.current_index = i
                return
        # Si ninguna está pendiente, se queda en la primera o 0
        self.current_index = 0 if self.items else -1

    def get_current_item(self) -> Optional[Dict[str, Any]]:
        """Retorna el ítem actual o None si no hay imágenes."""
        if 0 <= self.current_index < len(self.items):
            return self.items[self.current_index]
        return None

    def get_stats(self) -> Dict[str, Any]:
        """Calcula estadísticas actuales para la interfaz."""
        total = len(self.items)
        classified = sum(1 for it in self.items if it.get("status") == "classified")
        skipped = sum(1 for it in self.items if it.get("status") == "skipped")
        pending = total - classified - skipped

        current_display = self.current_index + 1 if (0 <= self.current_index < total) else 0

        return {
            "total": total,
            "classified": classified,
            "skipped": skipped,
            "pending": pending,
            "current_index": self.current_index,
            "current_display": current_display,
            "has_next": self.current_index < total - 1,
            "has_previous": self.current_index > 0,
            "can_undo": len(self.history) > 0,
        }

    def classify_current(self, category_name: str) -> Tuple[bool, Optional[str]]:
        """
        Clasifica la imagen actual en la categoría dada.
        
        Returns:
            (éxito: bool, mensaje_error: Optional[str])
        """
        item = self.get_current_item()
        if not item:
            return False, "No hay ninguna imagen seleccionada para clasificar."

        if not self.destination_folder:
            return False, "No se ha configurado la carpeta de destino."

        src_path = item["src_path"]
        previous_status = item["status"]
        previous_category = item["category"]
        previous_dest_path = item["dest_path"]

        # Ejecutar la operación en disco (copiar o mover)
        success, final_dest, err = classify_file(
            src_path=src_path,
            dest_root_dir=self.destination_folder,
            category_name=category_name,
            move_file=self.move_mode,
        )

        if not success:
            # NO avanzar ni cambiar estado si falló la operación
            return False, err

        # Registrar en la pila de historial para permitir deshacer
        action_record = {
            "action": "classify",
            "index": self.current_index,
            "previous_status": previous_status,
            "previous_category": previous_category,
            "previous_dest_path": previous_dest_path,
            "src_path": src_path,
            "dest_path": final_dest,
            "operation": "move" if self.move_mode else "copy",
            "category": category_name,
        }
        self.history.append(action_record)

        # Actualizar ítem
        item["status"] = "classified"
        item["category"] = category_name
        item["dest_path"] = final_dest
        item["updated_at"] = time.time()

        # Avanzar automáticamente a la siguiente imagen pendiente o siguiente disponible
        self.advance_to_next()

        # Persistir progreso
        self.save_progress()

        return True, None

    def skip_current(self) -> bool:
        """
        Marca la imagen actual como saltada y avanza a la siguiente.
        """
        item = self.get_current_item()
        if not item:
            return False

        action_record = {
            "action": "skip",
            "index": self.current_index,
            "previous_status": item["status"],
            "previous_category": item["category"],
            "previous_dest_path": item["dest_path"],
            "src_path": item["src_path"],
            "dest_path": None,
            "operation": "none",
            "category": None,
        }
        self.history.append(action_record)

        item["status"] = "skipped"
        item["updated_at"] = time.time()

        self.advance_to_next()
        self.save_progress()
        return True

    def undo_last(self) -> Tuple[bool, Optional[str]]:
        """
        Revierte la última acción realizada (clasificación o salto).
        """
        if not self.history:
            return False, "No hay acciones para deshacer."

        last_action = self.history.pop()
        target_index = last_action["index"]

        if not (0 <= target_index < len(self.items)):
            return False, "Índice de acción inválido en el historial."

        item = self.items[target_index]

        # Si fue clasificación, revertir archivo en disco
        if last_action["action"] == "classify":
            success, err = undo_classification(last_action)
            if not success:
                # Devolver la acción al historial para no perder coherencia
                self.history.append(last_action)
                return False, err

        # Restaurar estado previo del ítem
        item["status"] = last_action["previous_status"]
        item["category"] = last_action["previous_category"]
        item["dest_path"] = last_action["previous_dest_path"]
        item["updated_at"] = time.time()

        # Posicionarse de nuevo en esa imagen
        self.current_index = target_index

        self.save_progress()
        return True, None

    def advance_to_next(self):
        """Avanza a la siguiente imagen buscando primero pendientes."""
        if not self.items:
            return
        
        # Buscar la siguiente imagen pendiente a partir de la posición actual + 1
        for i in range(self.current_index + 1, len(self.items)):
            if self.items[i].get("status") == "pending":
                self.current_index = i
                return

        # Si no hay pendientes hacia adelante, avanzar un índice si no estamos al final
        if self.current_index < len(self.items) - 1:
            self.current_index += 1

    def go_previous(self) -> bool:
        """Navega a la imagen anterior."""
        if self.current_index > 0:
            self.current_index -= 1
            return True
        return False

    def go_next(self) -> bool:
        """Navega a la imagen siguiente."""
        if self.current_index < len(self.items) - 1:
            self.current_index += 1
            return True
        return False

    def go_to_index(self, index: int) -> bool:
        """Navega directamente al índice solicitado."""
        if 0 <= index < len(self.items):
            self.current_index = index
            return True
        return False

    # --- Gestión de Categorías ---

    def add_category(self, name: str) -> Tuple[bool, Optional[str]]:
        """Añade una categoría nueva si no existe."""
        clean = name.strip()
        if not clean:
            return False, "El nombre de la categoría no puede estar vacío."
        
        if clean in self.categories:
            return False, f"La categoría '{clean}' ya existe."

        self.categories.append(clean)
        self.save_progress()
        return True, None

    def rename_category(self, old_name: str, new_name: str) -> Tuple[bool, Optional[str]]:
        """
        Renombra una categoría existente.
        Nota de seguridad: NO renombra ni elimina archivos existentes en disco automáticamente
        para evitar corrupción o pérdidas no deseadas.
        """
        new_clean = new_name.strip()
        if not new_clean:
            return False, "El nuevo nombre no puede estar vacío."
        
        if old_name not in self.categories:
            return False, f"La categoría '{old_name}' no existe."

        if new_clean in self.categories and new_clean != old_name:
            return False, f"Ya existe una categoría con el nombre '{new_clean}'."

        idx = self.categories.index(old_name)
        self.categories[idx] = new_clean

        # Actualizar referencias en los ítems clasificados
        for item in self.items:
            if item.get("category") == old_name:
                item["category"] = new_clean

        self.save_progress()
        return True, None

    def remove_category(self, name: str) -> Tuple[bool, Optional[str]]:
        """
        Elimina una categoría de la lista activa.
        Nota de seguridad: Los archivos ya clasificados en esa categoría en disco
        NO se borran.
        """
        if name not in self.categories:
            return False, f"La categoría '{name}' no existe."

        self.categories.remove(name)
        self.save_progress()
        return True, None

    # --- Persistencia Atómica ---

    def save_progress(self) -> bool:
        """
        Guarda el estado actual en 'clasificador_progreso.json' dentro de la carpeta destino.
        Usa escritura atómica mediante archivo temporal.
        """
        if not self.destination_folder:
            return False

        try:
            dest_dir = Path(self.destination_folder)
            dest_dir.mkdir(parents=True, exist_ok=True)

            filepath = self.get_progress_filepath(dest_dir)
            temp_filepath = dest_dir / f"{PROGRESS_FILENAME}.tmp"

            payload = {
                "version": 1,
                "saved_at": time.time(),
                "source_folder": self.source_folder,
                "destination_folder": self.destination_folder,
                "recursive_scan": self.recursive_scan,
                "move_mode": self.move_mode,
                "categories": self.categories,
                "current_index": self.current_index,
                "items": self.items,
                "history": self.history[-50:],  # Guardar los últimos 50 pasos de historial
            }

            with open(temp_filepath, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)

            # Reemplazo atómico para evitar corrupción de archivo
            temp_filepath.replace(filepath)
            return True

        except Exception as e:
            # Si falla guardar, no detenemos de manera catastrófica pero registramos
            print(f"[Error guardando progreso]: {e}")
            return False
