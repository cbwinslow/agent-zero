from pathlib import Path

def test_togetherai_provider_present():
    text = Path('models.py').read_text()
    assert 'TOGETHERAI' in text
