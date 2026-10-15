import os
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
from PIL import Image, ImageOps, UnidentifiedImageError
from PySide6.QtGui import QImage, QPixmap


def load_image_with_exif(filepath: str | Path) -> Tuple[Optional[QPixmap], Optional[str], Dict[str, Any]]:
    """
    Carga una imagen respetando la orientación EXIF y la convierte a QPixmap para la interfaz.
    No mantiene el archivo abierto en disco ni satura la memoria.
    
    Args:
        filepath: Ruta del archivo de imagen.
        
    Returns:
        (pixmap, mensaje_error, metadata)
    """
    path = Path(filepath)
    if not path.exists():
        return None, f"El archivo no existe: {path}", {}

    metadata: Dict[str, Any] = {
        "filename": path.name,
        "path": str(path),
        "size_bytes": 0,
        "width": 0,
        "height": 0,
        "format": "Desconocido",
        "has_exif": False,
    }

    try:
        stat = path.stat()
        metadata["size_bytes"] = stat.st_size
    except OSError:
        pass

    try:
        # Abrimos con Pillow en modo seguro
        with Image.open(str(path)) as img:
            metadata["format"] = img.format or path.suffix.upper().lstrip(".")
            
            # Aplicar rotación/espejado según orientación EXIF
            try:
                transposed_img = ImageOps.exif_transpose(img)
                if transposed_img is not None:
                    img = transposed_img
                    metadata["has_exif"] = True
            except Exception:
                # Si falla leer EXIF, se continúa con la imagen original sin abortar
                pass

            metadata["width"] = img.width
            metadata["height"] = img.height

            # Convertir imagen para Qt
            # Si tiene canal alfa (transparencia) usamos RGBA, si no, RGB
            if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                img_conv = img.convert("RGBA")
                data = img_conv.tobytes("raw", "RGBA")
                qimage = QImage(
                    data,
                    img_conv.width,
                    img_conv.height,
                    img_conv.width * 4,
                    QImage.Format.Format_RGBA8888
                )
            else:
                img_conv = img.convert("RGB")
                data = img_conv.tobytes("raw", "RGB")
                # QImage requiere alineación de línea de 4 bytes o especificar bytes_per_line
                bytes_per_line = img_conv.width * 3
                qimage = QImage(
                    data,
                    img_conv.width,
                    img_conv.height,
                    bytes_per_line,
                    QImage.Format.Format_RGB888
                )

            # Crear copia del pixmap para desvincular del búfer de bytes temporal
            pixmap = QPixmap.fromImage(qimage.copy())
            return pixmap, None, metadata

    except UnidentifiedImageError:
        return None, "Formato de imagen no reconocido o archivo corrupto.", metadata
    except PermissionError:
        return None, "Permiso denegado al intentar leer el archivo.", metadata
    except OSError as e:
        return None, f"Error al abrir la imagen: {e}", metadata
    except Exception as e:
        return None, f"Error inesperado al procesar la imagen: {e}", metadata
