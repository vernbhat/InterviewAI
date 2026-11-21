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
