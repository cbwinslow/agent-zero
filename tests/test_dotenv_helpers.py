from pathlib import Path
import os
import importlib
from python.helpers import dotenv, files


def test_save_and_get_dotenv_value(tmp_path, monkeypatch):
    monkeypatch.setattr(files, "get_base_dir", lambda: tmp_path)
    dotenv.save_dotenv_value("TEST_KEY", "VALUE")
    assert dotenv.get_dotenv_value("TEST_KEY") == "VALUE"
    assert (tmp_path / ".env").read_text().strip().split("=")[1] == "VALUE"
