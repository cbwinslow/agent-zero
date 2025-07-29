from pathlib import Path

def test_anythingllm_provider_present():
    text = Path('models.py').read_text()
    assert 'ANYTHINGLLM' in text
