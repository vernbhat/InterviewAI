import json

from app import llm


def test_to_anthropic_merges_roles_and_maps_tools():
    msgs = [
        {"role": "system", "content": "be an interviewer"},
        {"role": "assistant", "content": "Hi, read the problem."},
        {"role": "user", "content": "ok"},
        {"role": "assistant", "content": "", "tool_calls": [
            {"id": "c1", "type": "function", "function": {"name": "advance_phase", "arguments": json.dumps({"to": "code"})}}]},
        {"role": "tool", "tool_call_id": "c1", "content": "done"},
        {"role": "user", "content": "next"},
    ]
    system, out = llm._to_anthropic(msgs)
    assert system == "be an interviewer"
    assert out[0]["role"] == "user"  # synthetic opener
    roles = [m["role"] for m in out]
    assert all(a != b for a, b in zip(roles, roles[1:]))  # strictly alternating
    tool_use = out[3]["content"][0]
    assert tool_use == {"type": "tool_use", "id": "c1", "name": "advance_phase", "input": {"to": "code"}}
    assert out[4]["content"][0]["type"] == "tool_result" and out[4]["content"][1]["text"] == "next"


def test_server_key_sentinel(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    assert llm.server_key() == llm.ANTHROPIC_SERVER_SENTINEL
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    assert llm.server_key() is None
