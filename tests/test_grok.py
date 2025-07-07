from pathlib import Path

def test_grok_provider_present():
    text = Path('models.py').read_text()
    assert 'GROK' in text
