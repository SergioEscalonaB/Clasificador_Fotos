# Clasificador Manual de Fotos

Aplicación de escritorio moderna desarrollada con **Python** y **PySide6 (Qt)** para clasificar grandes volúmenes de fotos de manera manual, rápida y segura en Windows 10/11.

---

## Características Principales

- **Visualización Optimizada:** Muestra una imagen a la vez ajustada al espacio disponible manteniendo la relación de aspecto sin deformaciones.
- **Soporte EXIF Automático:** Corrige y respeta la orientación EXIF de las fotos capturadas con cámaras o teléfonos móviles.
- **Amplio Soporte de Formatos:** Admite imágenes en formato `JPG`, `JPEG`, `PNG`, `BMP`, `GIF`, `TIFF`, `TIF` y `WEBP`.
- **Máxima Seguridad de Archivos:**
  - **Copia por defecto:** Nunca modifica ni elimina las fotos originales salvo que actives explícitamente la casilla de mover.
  - **Evita sobrescritura:** Si en la categoría destino ya existe un archivo con el mismo nombre, genera nombres seguros tipo `foto (1).jpg`.
  - **Tolerancia a fallos:** Si ocurre un error de disco o permisos, la aplicación alerta al usuario y no avanza la imagen.
- **Reanudación 100% Automática:**
  - Recuerda las últimas carpetas de origen y destino utilizadas.
  - Al abrir la aplicación, carga y continúa de inmediato en la foto donde te habías quedado, sin necesidad de volver a buscar carpetas ni pulsar botones.
- **Categorías Limpias y Persistentes:**
  - Comienza limpio sin categorías de ejemplo prefijadas.
  - Las categorías que tú crees se quedan guardadas para futuras sesiones.
  - Las categorías que elimines se van para siempre y no vuelven a aparecer.
- **Atajos de Teclado Ultra Rápidos:** Clasifica con teclas directas (`1`-`9`, `0`, `Q`-`P`), salta con `Espacio`, navega con flechas y deshace con `Ctrl + Z`.
- **Bajo Consumo de Memoria:** Carga únicamente la foto visible en memoria; ideal para colecciones con miles de imágenes.

---

## Estructura de la Solución

```text
Clasificador/
├── clasificador/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── app_config.py         # Persistencia de configuración global y últimas rutas
│   │   ├── file_scanner.py       # Detección de formatos, escaneo plano/recursivo y orden natural
│   │   ├── file_ops.py           # Operaciones seguras en disco, nombres únicos y lógica de deshacer
│   │   ├── session_manager.py    # Ciclo de vida de sesión, persistencia JSON y navegación
│   │   └── image_loader.py       # Decodificación de imagen, corrección EXIF y conversión a QPixmap
│   └── ui/
│       ├── __init__.py
│       ├── lucide_icons.py       # Proveedor de iconos vectoriales SVG estilo Lucide
│       ├── main_window.py        # Ventana principal, barra de carpetas, estadísticas y atajos
│       ├── image_viewer.py       # Visor con escalado proporcional y tarjetas informativas
│       ├── category_panel.py     # Panel interactivo de categorías con atajos e insignias
│       └── styles.py             # Hoja de estilos moderna QSS optimizada para Windows 10/11
├── tests/
│   ├── __init__.py
│   ├── test_app_config.py        # Pruebas de persistencia de configuración
│   ├── test_file_scanner.py      # Pruebas de escaneo, formatos y orden natural
│   ├── test_file_ops.py          # Pruebas de copia, mover, duplicados y reversión
│   ├── test_session.py           # Pruebas de ciclo de vida de sesión y categorías
│   ├── test_image_loader.py      # Pruebas de carga, transparencia y archivos dañados
│   └── test_lucide_icons.py      # Pruebas de renderizado de iconos vectoriales Lucide
├── main.py                       # Punto de entrada de la aplicación
├── requirements.txt              # Especificación de dependencias del proyecto
└── README.md                     # Documentación técnica de referencia
```

---

## Requisitos e Instalación

### Entorno de Ejecución
- Sistema Operativo: Windows 10 o Windows 11 (64 bits).
- Intérprete: Python 3.10 o superior (compatible con Python 3.10, 3.11, 3.12, 3.13, 3.14).

### 1. Clonar o Descargar el Proyecto
Abre una consola de comandos (PowerShell o Terminal de Windows) en el directorio del proyecto:
```powershell
cd "c:\Users\Sergio Luis\Desktop\Clasificador"
```

### 2. (Recomendado) Crear y Activar un Entorno Virtual
```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar Dependencias
```powershell
pip install -r requirements.txt
```

---

## Ejecución en Modo Desarrollo

Para lanzar la aplicación directamente desde el código fuente:
```powershell
python main.py
```

---

## Flujo de Trabajo

1. **Configuración de Origen:**
   - Pulsa el botón `Examinar...` para definir la carpeta contenedora de las imágenes.
   - Activa o desactiva la casilla `Incluir subcarpetas` según la profundidad de búsqueda requerida.
2. **Configuración de Destino:**
   - Selecciona la carpeta destino de organización. Si contiene una sesión previa, la aplicación te consultará si deseas reanudarla.
3. **Definición de Categorías:**
   - Emplea el botón `Nueva` para registrar tus carpetas de destino (ej: *Facturas*, *Clientes*, *Obras*, *Familia*).
   - Puedes usar `Editar` para renombrar o `Quitar` para eliminar de la lista activa.
4. **Inicio:**
   - Haz clic en `Cargar imágenes / Iniciar`.
5. **Clasificación Manual:**
   - Pulsa el botón correspondiente o la tecla de atajo asignada (`1`-`9`, `0`, `Q`-`P`).
   - La imagen se procesará en `CarpetaDestino/Categoria/archivo.ext` y el visor avanzará automáticamente a la siguiente imagen pendiente.

---

## Matriz de Atajos de Teclado

| Tecla / Combinación | Acción Realizada |
| :--- | :--- |
| `1`, `2`, `3`, ..., `9`, `0` | Clasificar inmediatamente en la categoría asignada al número |
| `Q`, `W`, `E`, `R`, `T`, ... | Clasificar en categorías adicionales si superan los diez botones |
| `Espacio` | **Saltar:** Omite la fotografía actual y pasa a la siguiente |
| `<-` (Flecha Izquierda) | **Anterior:** Retrocede a la imagen previa para inspección |
| `->` (Flecha Derecha) | **Siguiente:** Avanza a la siguiente imagen sin clasificar |
| `Ctrl + Z` | **Deshacer:** Reinvierte de forma segura la última acción ejecutada |

---

## Compilación del Ejecutable de Windows (.exe)

La compilación genera un binario totalmente independiente que no requiere tener instalado Python ni dependencias en los equipos de destino.

### Ejecutable Único Portátil (Recomendado)
```powershell
python -m PyInstaller --noconsole --onefile --name "ClasificadorDeFotos" --clean main.py
```
El archivo final compilado se encontrará en:
```text
dist\ClasificadorDeFotos.exe
```

### Compilación con Icono de Aplicación Personalizado
Si dispones de un archivo `.ico`:
```powershell
python -m PyInstaller --noconsole --onefile --icon="icono.ico" --name "ClasificadorDeFotos" --clean main.py
```

---

## Pruebas de Calidad Automatizadas

El proyecto incluye una cobertura de 21 pruebas unitarias automatizadas que verifican la estabilidad de cada componente crítico:

```powershell
python -m pytest tests/ -v
```
