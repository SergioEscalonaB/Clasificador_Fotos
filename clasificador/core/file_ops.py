import os
import shutil
import re
from pathlib import Path
from typing import Tuple, Optional, Dict, Any


def sanitize_category_name(category_name: str) -> str:
    """
    Limpia el nombre de la categoría para que sea un nombre de carpeta válido en Windows.
    Reemplaza caracteres no permitidos: < > : " / \\ | ? *
    """
    clean = re.sub(r'[<>:"/\\|?*]', '_', category_name.strip())
    # Evitar nombres vacíos o solo puntos
    clean = clean.strip('. ')
    return clean if clean else "Sin_Categoria"


def get_unique_destination_path(dest_dir: Path | str, original_filename: str) -> Path:
    """
    Calcula una ruta de destino única para evitar sobrescribir archivos existentes.
    Si 'foto.jpg' existe, prueba con 'foto (1).jpg', 'foto (2).jpg', etc.
    """
    dest_path_dir = Path(dest_dir)
    original_path = Path(original_filename)
    stem = original_path.stem
    suffix = original_path.suffix

    candidate = dest_path_dir / f"{stem}{suffix}"
    counter = 1

    while candidate.exists():
        candidate = dest_path_dir / f"{stem} ({counter}){suffix}"
        counter += 1

    return candidate


def classify_file(
    src_path: str | Path,
    dest_root_dir: str | Path,
    category_name: str,
    move_file: bool = False
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Copia o mueve una imagen a la subcarpeta de la categoría especificada.
    
    Args:
        src_path: Ruta del archivo original.
        dest_root_dir: Carpeta de destino principal.
        category_name: Nombre de la categoría elegida.
        move_file: Si es False (predeterminado), COPIA. Si es True, MUEVE.
        
    Returns:
        (éxito: bool, ruta_final_en_destino: Optional[str], mensaje_error: Optional[str])
    """
    source = Path(src_path)
    if not source.exists():
        return False, None, f"El archivo de origen no existe: {source}"

    if not source.is_file():
        return False, None, f"La ruta de origen no es un archivo: {source}"

    try:
        clean_category = sanitize_category_name(category_name)
        target_dir = Path(dest_root_dir) / clean_category
        target_dir.mkdir(parents=True, exist_ok=True)

        target_path = get_unique_destination_path(target_dir, source.name)

        if move_file:
            # Mover archivo
            shutil.move(str(source), str(target_path))
        else:
            # Copiar archivo preservando metadatos (fechas, etc.)
            shutil.copy2(str(source), str(target_path))

        return True, str(target_path), None

    except PermissionError as e:
        return False, None, f"Permiso denegado al {'mover' if move_file else 'copiar'}: {e}"
    except OSError as e:
        return False, None, f"Error del sistema de archivos: {e}"
    except Exception as e:
        return False, None, f"Error inesperado: {e}"


def undo_classification(action_record: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Revierte una acción de clasificación previa.
    
    Args:
        action_record: Diccionario con la información de la acción realizada:
            - "operation": "copy" o "move"
            - "src_path": ruta original de origen
            - "dest_path": ruta donde se guardó en destino
            
    Returns:
        (éxito: bool, mensaje_error: Optional[str])
    """
    operation = action_record.get("operation", "copy")
    dest_path_str = action_record.get("dest_path")
    src_path_str = action_record.get("src_path")

    if not dest_path_str:
        return False, "Registro de acción inválido: falta dest_path."

    dest_file = Path(dest_path_str)

    if operation == "copy":
        # En modo copia, revertir implica borrar la copia generada en la carpeta de destino
        if dest_file.exists():
            try:
                dest_file.unlink()
                return True, None
            except OSError as e:
                return False, f"No se pudo eliminar el archivo copiado en destino: {e}"
        else:
            # Si el archivo en destino ya no existe, consideramos el deshacer como completado
            return True, None

    elif operation == "move":
        # En modo mover, revertir implica devolver el archivo a la ruta de origen
        if not src_path_str:
            return False, "Falta ruta de origen para restaurar archivo movido."
        
        src_file = Path(src_path_str)
        if not dest_file.exists():
            return False, f"El archivo movido ya no existe en el destino: {dest_file}"

        try:
            # Asegurar que el directorio de origen existe
            src_file.parent.mkdir(parents=True, exist_ok=True)

            # Si ya existe un archivo con ese nombre en origen (caso extremo), obtener nombre seguro
            final_src_path = src_file
            if src_file.exists():
                final_src_path = get_unique_destination_path(src_file.parent, src_file.name)

            shutil.move(str(dest_file), str(final_src_path))
            return True, None
        except OSError as e:
            return False, f"Error al devolver el archivo a su origen: {e}"

    return False, f"Operación desconocida: {operation}"
