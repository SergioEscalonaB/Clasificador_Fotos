import os
import json
from pathlib import Path
from typing import Dict, Any

# Ubicación de configuración global del usuario en Windows / SO
CONFIG_DIR = Path(os.environ.get("APPDATA", str(Path.home()))) / "ClasificadorDeFotos"
CONFIG_FILE = CONFIG_DIR / "config.json"


def get_app_config() -> Dict[str, Any]:
    """Lee la configuración global de la aplicación si existe."""
    if CONFIG_FILE.is_file():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_app_config(config: Dict[str, Any]) -> bool:
    """Guarda la configuración global de forma atómica."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        temp_file = CONFIG_DIR / "config.json.tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        temp_file.replace(CONFIG_FILE)
        return True
    except Exception as e:
        print(f"[Error guardando config de app]: {e}")
        return False
