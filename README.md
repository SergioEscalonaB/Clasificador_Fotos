# Clasificador Manual de Fotos

Aplicación de escritorio moderna desarrollada con **Python** y **PySide6 (Qt)** para clasificar grandes volúmenes de fotos de manera manual, rápida y segura en Windows 10/11.

---

## 🎯 Características Principales

- **Visualización Optimizada:** Muestra una imagen a la vez ajustada al espacio disponible manteniendo la relación de aspecto sin deformaciones.
- **Soporte EXIF Automático:** Corrige y respeta la orientación EXIF de las fotos capturadas con cámaras o teléfonos móviles.
- **Amplio Soporte de Formatos:** Admite imágenes en formato `JPG`, `JPEG`, `PNG`, `BMP`, `GIF`, `TIFF`, `TIF` y `WEBP`.
- **Máxima Seguridad de Archivos:**
  - **Copia por defecto:** Nunca modifica ni elimina las fotos originales salvo que actives explícitamente la casilla de mover.
  - **Evita sobrescritura:** Si en la categoría destino ya existe un archivo con el mismo nombre, genera nombres seguros tipo `foto (1).jpg`.
  - **Tolerancia a fallos:** Si ocurre un error de disco o permisos, la aplicación alerta al usuario y no avanza la imagen.
- **Reanudación Automática de Sesión:**
  - Guarda el avance en `clasificador_progreso.json` dentro de la carpeta de destino de forma atómica.
  - Al reabrir la carpeta de destino, detecta el trabajo previo y permite continuar sin duplicar trabajo.
- **Atajos de Teclado Ultra Rápidos:** Clasifica con teclas directas (`1`-`9`, `0`, `Q`-`P`), salta con `Espacio`, navega con flechas y deshace con `Ctrl + Z`.
- **Bajo Consumo de Memoria:** Carga únicamente la foto visible en memoria; ideal para colecciones con miles de imágenes.

---

## 📁 Estructura del Proyecto

```text
Clasificador/
├── clasificador/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── file_scanner.py       # Búsqueda recursiva/plana, filtros y orden natural
│   │   ├── file_ops.py           # Copia segura, mover, resolución de colisiones y deshacer
│   │   ├── session_manager.py    # Gestión de estado, persistencia JSON y pila de historial
│   │   └── image_loader.py       # Carga con orientación EXIF y conversión a QPixmap
│   └── ui/
│       ├── __init__.py
│       ├── main_window.py        # Ventana principal, control de eventos y navegación
│       ├── image_viewer.py       # Visor con escalado proporcional y tarjetas de estado
│       ├── category_panel.py     # Botones dinámicos de categorías, atajos y gestión
│       └── styles.py             # Hoja de estilos moderna adaptada a Windows 10/11
├── tests/
│   ├── __init__.py
│   ├── test_file_scanner.py      # Pruebas de detección de formatos y escaneo
│   ├── test_file_ops.py          # Pruebas de copia, mover, colisiones y deshacer
│   ├── test_session.py           # Pruebas de guardado/reanudación y categorías
│   └── test_image_loader.py      # Pruebas de carga, transparencia y archivos corruptos
├── main.py                       # Punto de entrada de la aplicación
├── requirements.txt              # Dependencias del proyecto
└── README.md                     # Documentación de uso y compilación
```

---

## 🚀 Requisitos e Instalación

### Requisitos previos
- Windows 10 o Windows 11.
- Python 3.10 o superior (recomendado 3.10, 3.11, 3.12, 3.13 o 3.14).

### 1. Clonar o descargar el código
Abre una terminal (PowerShell o CMD) en la carpeta del proyecto:
```powershell
cd "c:\Users\Sergio Luis\Desktop\Clasificador"
```

### 2. (Opcional) Crear un entorno virtual
```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias
```powershell
pip install -r requirements.txt
```

---

## 💻 Ejecución de la Aplicación

Para iniciar la aplicación directamente:
```powershell
python main.py
```

---

## 📖 Guía de Uso Paso a Paso

1. **Seleccionar Carpeta de Origen:**
   - Haz clic en `Examinar...` junto a "Carpeta Origen" y selecciona la carpeta con tus fotos.
   - Marca o desmarca **"Incluir subcarpetas"** según si deseas buscar en todas las subcarpetas o solo en el directorio raíz.
2. **Seleccionar Carpeta de Destino:**
   - Haz clic en `Examinar...` junto a "Carpeta Destino".
   - Si la carpeta de destino ya contiene un archivo de sesión previo (`clasificador_progreso.json`), la aplicación te preguntará si deseas **reanudar el trabajo** para continuar exactamente donde lo dejaste.
3. **Modo de Operación:**
   - Por defecto está en modo **COPIAR** (los originales permanecen intactos).
   - Si marcas **"Mover en vez de copiar"**, la aplicación solicitará confirmación por seguridad.
4. **Gestionar Categorías:**
   - Puedes usar las categorías sugeridas ("Mami", "Papi", "Hermano", "Obras terminadas", "Otros") o usar los botones:
     - `➕ Nueva`: Crear una nueva categoría.
     - `✏️ Editar`: Renombrar una categoría.
     - `🗑️ Quitar`: Quitar una categoría de la lista activa (las fotos ya copiadas no se borrarán).
5. **Iniciar:**
   - Haz clic en el botón azul **"▶ Cargar imágenes / Iniciar"**.
6. **Clasificar:**
   - Presiona el botón de la categoría o utiliza el número/letra de atajo correspondiente en el teclado.
   - La foto se guardará de inmediato en `CarpetaDestino/NombreCategoria/foto.jpg` y pasará automáticamente a la siguiente imagen pendiente.

---

## ⌨️ Atajos de Teclado

| Tecla / Combinación | Acción |
| :--- | :--- |
| `1`, `2`, `3`, ..., `9`, `0` | Clasificar en la categoría correspondiente al número |
| `Q`, `W`, `E`, `R`, `T`, ... | Clasificar en categorías adicionales si superan los números |
| `Espacio` | **Saltar imagen** (dejarla pendiente/omitida y pasar a la siguiente) |
| `←` (Flecha Izquierda) | **Anterior:** Ver la imagen anterior |
| `→` (Flecha Derecha) | **Siguiente:** Ver la imagen siguiente sin clasificar |
| `Ctrl + Z` | **Deshacer:** Revierte la última clasificación o salto |

---

## 📦 Cómo Crear el Ejecutable para Windows (.exe)

Puedes compilar la aplicación en un ejecutable independiente de Windows mediante **PyInstaller**.

### Opción A: Archivo único (.exe portátil)
Genera un único archivo ejecutable listo para compartir:
```powershell
python -m PyInstaller --noconsole --onefile --name "ClasificadorDeFotos" main.py
```
El archivo resultante se encontrará en:
```text
dist\ClasificadorDeFotos.exe
```

### Opción B: Carpeta distribuible (arranque más veloz)
Si prefieres que el ejecutable abra de manera instantánea sin descompresión en cada arranque:
```powershell
python -m PyInstaller --noconsole --onedir --name "ClasificadorDeFotos" main.py
```
Encontrarás la carpeta en `dist\ClasificadorDeFotos\ClasificadorDeFotos.exe`.

---

## 🧪 Pruebas Unitarias Automatizadas

El proyecto incluye una suite completa de pruebas unitarias que cubren:
- Escaneo plano y recursivo con filtrado de extensiones y orden natural.
- Copia segura, movimiento y resolución de colisiones de nombres duplicados.
- Reversión y deshacer tanto en modo copia como en modo mover.
- Carga de imágenes válidas, transparencias alfa, orientación EXIF y manejo seguro de archivos corruptos.
- Ciclo de vida de la sesión, guardado atómico, reanudación sin duplicación y seguridad en categorías.

Para ejecutar todas las pruebas:
```powershell
python -m pytest tests/ -v
```

Resultado obtenido:
```text
tests/test_file_ops.py::test_sanitize_category_name PASSED
tests/test_file_ops.py::test_get_unique_destination_path PASSED
tests/test_file_ops.py::test_classify_copy_mode PASSED
tests/test_file_ops.py::test_classify_move_mode PASSED
tests/test_file_ops.py::test_undo_copy PASSED
tests/test_file_ops.py::test_undo_move PASSED
tests/test_file_ops.py::test_classify_nonexistent_file PASSED
tests/test_file_scanner.py::test_is_supported_image PASSED
tests/test_file_scanner.py::test_natural_sort PASSED
tests/test_file_scanner.py::test_scan_images_flat_and_recursive PASSED
tests/test_file_scanner.py::test_scan_empty_directory PASSED
tests/test_image_loader.py::test_load_valid_rgb_image PASSED
tests/test_image_loader.py::test_load_valid_rgba_image PASSED
tests/test_image_loader.py::test_load_corrupted_image PASSED
tests/test_image_loader.py::test_load_nonexistent_image PASSED
tests/test_session.py::test_session_lifecycle_and_persistence PASSED
tests/test_session.py::test_resume_existing_session PASSED
tests/test_session.py::test_category_management_safety PASSED
============================== 18 passed in 2.00s ==============================
```

---

## 🛡️ Decisiones de Diseño y Seguridad

1. **Prioridad Absoluta de Copia:** El modo predeterminado siempre es copiar. Si el usuario decide activar el modo "Mover", se muestra un diálogo de confirmación explícito advirtiendo que los originales serán trasladados.
2. **Escritura Atómica del Progreso:** Para evitar que un apagón o cierre abrupto corrompa el archivo `clasificador_progreso.json`, los datos se escriben primero en un archivo temporal (`.tmp`) y se reemplazan de forma atómica (`replace`).
3. **No Destrucción en Edición de Categorías:** Si el usuario renombra o elimina una categoría que ya tenía imágenes en disco, los archivos existentes en la carpeta de destino se conservan intactos.
4. **Nombres de Categoría Seguros en Windows:** Los caracteres reservados en el sistema de archivos de Windows (`< > : " / \ | ? *`) se limpian y reemplazan automáticamente con guiones bajos para garantizar que las carpetas siempre puedan crearse sin errores.
5. **Lazy Loading de Fotos:** En lugar de cargar todo el lote a la memoria RAM, cada imagen se carga y decodifica únicamente cuando se va a visualizar. Al pasar a la siguiente, se libera la anterior, permitiendo trabajar con carpetas de decenas de gigabytes sin ralentizaciones.
