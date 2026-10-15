import os
import pytest
from pathlib import Path
from unittest.mock import patch

from clasificador.core.app_config import get_app_config, save_app_config


def test_save_and_get_app_config(tmp_path):
    test_config_file = tmp_path / "config.json"
    
    with patch("clasificador.core.app_config.CONFIG_DIR", tmp_path), \
         patch("clasificador.core.app_config.CONFIG_FILE", test_config_file):
        
        # Al inicio está vacío
        assert get_app_config() == {}

        sample_data = {
            "last_source_folder": "C:/Fotos/Origen",
            "last_destination_folder": "C:/Fotos/Destino",
            "recursive_scan": False,
            "move_mode": False,
            "categories": ["Trabajo", "Personal"],
        }

        save_ok = save_app_config(sample_data)
        assert save_ok is True
        assert test_config_file.exists()

        loaded = get_app_config()
        assert loaded == sample_data
        assert loaded["categories"] == ["Trabajo", "Personal"]
