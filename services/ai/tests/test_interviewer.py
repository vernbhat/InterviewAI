import json

from app import feedback
from app.interviewer import TurnContext, advance, leaks_code, llm_turn, strip_code
from app.problems import get_problem


def ctx(**kw):
    p = get_problem("two-sum")
    base = dict(problem=p, language="python", phase="approach", hints_used=0, code="", starter="", history=[], last_run=None, last_submit=None)
    base.update(kw)
    return TurnContext(**base)


def test_phase_only_moves_forward():
    assert advance("code", "clarify") == "code"
    assert advance("code", "complexity") == "complexity"
    assert advance("code", "bogus") == "code"


def test_leak_guard_flags_code():
    assert leaks_code("Try this:\n```python\nreturn x\n```")
    assert leaks_code("seen = {}\nfor i in range(n):\n    if target - nums[i] in seen: return")
    assert leaks_code("int lo = 0;\nint hi = n - 1;")
    assert not leaks_code("What happens when the array has only two elements? Walk me through it.")
    assert not leaks_code("Think about a hash map. What would you store as the key?")
    assert strip_code("Good.\n```\nx = 1\n```\nWhat next?") == "Good.\n\nWhat next?"


class FakeLLM:
    def __init__(self, scripted):
        self.scripted = list(scripted)
        self.calls = []

    def __call__(self, messages, key, tools=None, **kw):
        self.calls.append({"messages": messages, "tools": tools})
        return self.scripted.pop(0)


def tool_call(name, args, cid="c1"):
    return {"content": "", "tool_calls": [{"id": cid, "type": "function", "function": {"name": name, "arguments": json.dumps(args)}}]}


def test_llm_agent_uses_tools_and_hint_ladder():
    fake = FakeLLM([
        tool_call("give_hint", {"reason": "candidate asked"}),
        tool_call("set_phase", {"phase": "code"}, "c2"),
        {"content": "What could you store as you scan so the complement lookup is fast?"},
    ])
    r = llm_turn(ctx(), "I'm stuck, can I get a hint?", "k", chat_fn=fake)
    assert r.mode == "llm" and r.hints_used == 1 and r.phase == "code"
    assert r.hint_text == get_problem("two-sum")["hints"][0]
    assert [c["name"] for c in r.tool_calls] == ["give_hint", "set_phase"]
    # The model never receives hints it has not unlocked, nor hidden tests.
    sys_prompt = fake.calls[0]["messages"][0]["content"]
    assert get_problem("two-sum")["hints"][2] not in sys_prompt
    assert "-999999995" not in json.dumps(fake.calls[0]["messages"])


def test_llm_agent_test_results_tool_is_grounded():
    run = {"status": "wrong_answer", "passed": 1, "total": 3, "tests": [{"hidden": False, "passed": False, "args": [[3, 3], 6], "expected": [0, 1], "actual": []}]}
    fake = FakeLLM([tool_call("get_test_results", {}), {"content": "Your run failed on [3,3]. Why might equal values matter?"}])
    llm_turn(ctx(last_run=run), "Is my code right?", "k", chat_fn=fake)
    tool_msg = fake.calls[1]["messages"][-1]
    assert tool_msg["role"] == "tool" and '"passed": 1' in tool_msg["content"]


def test_llm_leak_is_blocked_and_rewritten():
    fake = FakeLLM([
        {"content": "Here you go:\n```python\nseen = {}\nfor i, x in enumerate(nums): ...\n```"},
        {"content": "What data structure gives O(1) lookups of values you've already seen?"},
    ])
    r = llm_turn(ctx(), "Just give me the code", "k", chat_fn=fake)
    assert r.leak_blocked and "```" not in r.reply and "O(1) lookups" in r.reply


def test_feedback_flags_fabricated_quotes():
    msgs = [
        {"id": 1, "role": "candidate", "content": "I will use a hash map keyed by value."},
        {"id": 2, "role": "interviewer", "content": "Okay."},
    ]
    fake = FakeLLM([{"content": json.dumps({
        "summary": "Solid.",
        "strengths": [{"point": "Picked the right structure", "evidence": "use a hash map keyed by value"}],
        "improvements": [{"point": "Discuss edge cases", "evidence": "I never considered duplicates"}],
    })}])
    session = {"id": "s", "language": "python", "created_at": 0, "ended_at": 60, "hints_used": 0, "phase": "code", "mode": "llm", "code": ""}
    report = feedback.build_report(session, get_problem("two-sum"), msgs, [], "k", chat_fn=fake)
    llm_obs = [o for o in report["observations"] if o["source"] == "llm"]
    assert llm_obs[0]["verified"] is True and llm_obs[0]["evidence"]["message_id"] == 1
    assert llm_obs[1]["verified"] is False
