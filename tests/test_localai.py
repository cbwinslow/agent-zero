from pathlib import Path

def test_localai_provider_present():
    text = Path('models.py').read_text()
    assert 'LOCALAI' in text
