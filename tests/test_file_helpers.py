from pathlib import Path
from python.helpers import files


def test_get_abs_path(tmp_path, monkeypatch):
    monkeypatch.setattr(files, "get_base_dir", lambda: tmp_path)
    path = files.get_abs_path("data", "file.txt")
    assert Path(path) == tmp_path / "data" / "file.txt"
