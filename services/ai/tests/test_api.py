import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("INTERVIEWAI_DB", str(tmp_path / "test.db"))
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    from app.main import app

    return TestClient(app)


GOOD_TWO_SUM = """class Solution:
    def twoSum(self, nums, target):
        seen = {}
        for i, x in enumerate(nums):
            if target - x in seen:
                return [seen[target - x], i]
            seen[x] = i
"""


def test_health_and_problem_list(client):
    h = client.get("/api/health").json()
    assert h["status"] == "ok" and h["executor"] == "local" and h["server_llm_key"] is False
    problems = client.get("/api/problems").json()
    assert len(problems) >= 60


def test_problem_detail_hides_hidden_tests_and_hints(client):
    d = client.get("/api/problems/two-sum").json()
    assert "tests" not in d and "hints" not in d
    assert d["hidden_test_count"] >= 8 and len(d["examples"]) == 3
    assert "class Solution" in d["starter_code"]["cpp"] and "def twoSum" in d["starter_code"]["python"]
    assert client.get("/api/problems/nope").status_code == 404


def test_full_offline_interview_loop(client):
    s = client.post("/api/sessions", json={"problem_id": "two-sum", "language": "python"}).json()
    sid = s["session"]["id"]
    assert s["session"]["mode"] == "offline" and s["session"]["phase"] == "clarify"
    assert "Offline mode" in s["messages"][0]["content"]

    r = client.post(f"/api/sessions/{sid}/messages", json={"text": "Can the array contain negative numbers?"}).json()
    assert r["session"]["phase"] == "approach"
    r = client.post(f"/api/sessions/{sid}/messages", json={"text": "Brute force checks all pairs in O(n^2). Better: one pass with a hash map from value to index, checking the complement first."}).json()
    assert r["session"]["phase"] == "code"

    run = client.post(f"/api/sessions/{sid}/run", json={"code": GOOD_TWO_SUM, "kind": "run"}).json()
    assert run["result"]["status"] == "accepted" and run["result"]["total"] == 3
    sub = client.post(f"/api/sessions/{sid}/run", json={"code": GOOD_TWO_SUM, "kind": "submit"}).json()
    assert sub["result"]["status"] == "accepted" and sub["result"]["total"] == 12
    assert sub["session"]["phase"] == "test"

    r = client.post(f"/api/sessions/{sid}/messages", json={"text": "Done", "code": GOOD_TWO_SUM}).json()
    assert r["session"]["phase"] == "complexity"
    r = client.post(f"/api/sessions/{sid}/messages", json={"text": "Time is O(n) and space is O(n) for the map."}).json()
    assert r["session"]["phase"] == "wrapup"

    report = client.post(f"/api/sessions/{sid}/end", json={"code": GOOD_TWO_SUM}).json()
    assert "overall_score" not in report and "recommendation" not in report
    texts = " ".join(o["text"] for o in report["observations"])
    assert "first submission" in texts and "matches the reference" in texts and "no hints" in texts
    assert all("evidence" in o for o in report["observations"])
    # Ended sessions reject further activity, and the report is stable.
    assert client.post(f"/api/sessions/{sid}/messages", json={"text": "hi"}).status_code == 409
    assert client.post(f"/api/sessions/{sid}/end", json={}).json()["generated_at"] == report["generated_at"]

    history = client.get("/api/sessions").json()
    assert history[0]["id"] == sid and history[0]["best_passed"] == 12


def test_empty_code_gets_honest_report(client):
    sid = client.post("/api/sessions", json={"problem_id": "coin-change", "language": "cpp"}).json()["session"]["id"]
    report = client.post(f"/api/sessions/{sid}/end", json={}).json()
    kinds = {o["kind"] for o in report["observations"]}
    texts = " ".join(o["text"] for o in report["observations"])
    assert "never submitted" in texts and "never stated" in texts
    # The only strength allowed is "no hints"; nothing about the code itself.
    assert [o for o in report["observations"] if o["kind"] == "strength"][0]["category"] == "Independence"
    assert "improvement" in kinds


def test_hint_ladder(client):
    sid = client.post("/api/sessions", json={"problem_id": "two-sum", "language": "cpp"}).json()["session"]["id"]
    for level in (1, 2, 3):
        r = client.post(f"/api/sessions/{sid}/hint").json()
        assert r["level"] == level
    assert client.post(f"/api/sessions/{sid}/hint").status_code == 409
    full = client.get(f"/api/sessions/{sid}").json()
    assert len(full["revealed_hints"]) == 3 and full["session"]["hints_used"] == 3


def test_validation_errors_are_422_not_500(client):
    assert client.post("/api/sessions", json={"problem_id": "two-sum", "language": "java"}).status_code == 422
    sid = client.post("/api/sessions", json={"problem_id": "two-sum"}).json()["session"]["id"]
    assert client.post(f"/api/sessions/{sid}/messages", json={"text": ""}).status_code == 422
    assert client.post(f"/api/sessions/{sid}/messages", json={}).status_code == 422
    assert client.get("/api/sessions/doesnotexist").status_code == 404


def test_voice_requires_key(client):
    r = client.post("/api/speech/transcribe", files={"file": ("a.webm", b"123", "audio/webm")})
    assert r.status_code == 503


def test_sessions_are_isolated(client):
    a = client.post("/api/sessions", json={"problem_id": "two-sum"}).json()["session"]["id"]
    b = client.post("/api/sessions", json={"problem_id": "two-sum"}).json()["session"]["id"]
    assert a != b
    client.post(f"/api/sessions/{a}/messages", json={"text": "question for a"})
    assert all("question for a" not in m["content"] for m in client.get(f"/api/sessions/{b}").json()["messages"])
