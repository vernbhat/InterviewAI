from app import envfile


def test_envfile_parses_and_never_overrides(tmp_path, monkeypatch):
    f = tmp_path / ".env"
    f.write_text("# comment\nGROQ_API_KEY=gsk_abc  # my key\nexport FOO_X='quoted value'\nEMPTY=\nKEEP=fromfile\n")
    monkeypatch.setattr(envfile, "CANDIDATES", [f])
    monkeypatch.delenv("INTERVIEWAI_NO_DOTENV", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("FOO_X", raising=False)
    monkeypatch.delenv("EMPTY", raising=False)
    monkeypatch.setenv("KEEP", "fromenv")
    assert envfile.load() == [str(f)]
    import os
    assert os.environ["GROQ_API_KEY"] == "gsk_abc"
    assert os.environ["FOO_X"] == "quoted value"
    assert "EMPTY" not in os.environ
    assert os.environ["KEEP"] == "fromenv"


def test_save_key_creates_and_updates(tmp_path, monkeypatch):
    from app import envfile

    root = tmp_path / ".env"
    (tmp_path / ".env.example").write_text("# comment\nGROQ_API_KEY=\nLLM_MODEL=x\n")
    monkeypatch.setattr(envfile, "ROOT_ENV", root)
    monkeypatch.setattr(envfile, "EXAMPLE", tmp_path / ".env.example")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    envfile.save_key("gsk_first_key_123")
    assert "GROQ_API_KEY=gsk_first_key_123" in root.read_text()
    assert "LLM_MODEL=x" in root.read_text()
    envfile.save_key("gsk_second_key_456")
    text = root.read_text()
    assert text.count("GROQ_API_KEY=") == 1 and "gsk_second_key_456" in text
    import os

    assert os.environ["GROQ_API_KEY"] == "gsk_second_key_456"
    import pytest

    with pytest.raises(ValueError):
        envfile.save_key("bad key\nINJECT=1")

