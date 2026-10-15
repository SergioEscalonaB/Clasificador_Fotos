import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

# Extensiones de imagen soportadas (en minúsculas)
SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".gif",
    ".tiff",
    ".tif",
    ".webp",
}


def natural_sort_key(s: str):
    """
    Clave de ordenamiento natural para que 'foto2.jpg' aparezca antes que 'foto10.jpg'.
    """
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]


def is_supported_image(filepath: str | Path) -> bool:
    """Verifica si la extensión del archivo corresponde a una imagen soportada."""
    path = Path(filepath)
    return path.suffix.lower() in SUPPORTED_EXTENSIONS


def scan_images(folder_path: str | Path, recursive: bool = True) -> List[str]:
    """
    Escanea la carpeta en busca de imágenes soportadas.
    
    Args:
        folder_path: Ruta a la carpeta de origen.
        recursive: Si es True, incluye subcarpetas. Si es False, solo el nivel raíz.
        
    Returns:
        Lista ordenada de rutas absolutas como cadenas de texto.
    """
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        return []

    found_images: List[str] = []

    if recursive:
        for root, dirs, files in os.walk(folder):
            # Filtrar carpetas ocultas o de sistema
            dirs[:] = [d for d in dirs if not d.startswith(".") and not d.startswith("$")]
            for file in files:
                if not file.startswith("."):
                    ext = os.path.splitext(file)[1].lower()
                    if ext in SUPPORTED_EXTENSIONS:
                        found_images.append(os.path.abspath(os.path.join(root, file)))
    else:
        try:
            with os.scandir(folder) as entries:
                for entry in entries:
                    if entry.is_file() and not entry.name.startswith("."):
                        ext = os.path.splitext(entry.name)[1].lower()
                        if ext in SUPPORTED_EXTENSIONS:
                            found_images.append(os.path.abspath(entry.path))
        except (PermissionError, OSError):
            return []

    # Ordenar de forma natural por la ruta
    found_images.sort(key=natural_sort_key)
    return found_images


def format_file_size(size_in_bytes: int) -> str:
    """Convierte bytes a formato legible (B, KB, MB, GB)."""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.1f} KB"
    elif size_in_bytes < 1024 * 1024 * 1024:
        return f"{size_in_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_in_bytes / (1024 * 1024 * 1024):.2f} GB"


def get_file_info(filepath: str | Path) -> Dict[str, Any]:
    """
    Obtiene información básica del archivo sin cargar su contenido a memoria.
    """
    path = Path(filepath)
    if not path.exists():
        return {
            "name": path.name,
            "path": str(path),
            "exists": False,
            "size_str": "No encontrado",
            "size_bytes": 0,
        }

    try:
        stat = path.stat()
        return {
            "name": path.name,
            "path": str(path),
            "exists": True,
            "size_bytes": stat.st_size,
            "size_str": format_file_size(stat.st_size),
            "modified_time": stat.st_mtime,
        }
    except OSError:
        return {
            "name": path.name,
            "path": str(path),
            "exists": True,
            "size_str": "Desconocido",
            "size_bytes": 0,
        }
