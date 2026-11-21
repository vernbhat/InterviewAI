"""The problem bank is only trustworthy if independent reference solutions pass every test."""

import inspect
import textwrap
from pathlib import Path

import pytest

from app.problems import all_problems, get_problem
from app.runner import grade
from problem_specs import SPECS

REF_CPP = Path(__file__).parent / "reference" / "cpp"
SPEC_BY_ID = {s["id"]: s for s in SPECS}


def python_reference(problem):
    spec = SPEC_BY_ID[problem["id"]]
    fn = spec["reference"]
    src = textwrap.dedent(inspect.getsource(fn))
    name = problem["function"]["name"]
    return f"{src}\n\nclass Solution:\n    def {name}(self, *args):\n        return {fn.__name__}(*args)\n"


def test_bank_has_over_fifty_problems_with_hidden_tests():
    problems = all_problems()
    assert len(problems) >= 60
    assert {p["difficulty"] for p in problems} == {"Easy", "Medium", "Hard"}
    for p in problems:
        assert sum(t["hidden"] for t in p["tests"]) >= 5, p["id"]
        assert len(p["hints"]) == 3


@pytest.mark.parametrize("problem", all_problems(), ids=lambda p: p["id"])
def test_python_reference_passes_all_tests(problem):
    report = grade(problem, "python", python_reference(problem), include_hidden=True)
    assert report.status == "accepted", report.public()
    assert report.passed == report.total == len(problem["tests"])


@pytest.mark.parametrize("problem", all_problems(), ids=lambda p: p["id"])
def test_cpp_reference_passes_all_tests(problem):
    code = (REF_CPP / f"{problem['id']}.cpp").read_text()
    report = grade(problem, "cpp", code, include_hidden=True)
    assert report.status == "accepted", report.public()


def test_starter_code_compiles_but_fails():
    from app.codegen import starter_code

    p = get_problem("two-sum")
    py = grade(p, "python", starter_code(p, "python"), include_hidden=False)
    assert py.status == "wrong_answer" and py.passed == 0
    # C++ starter has no return statement; it must still compile.
    cpp = grade(p, "cpp", starter_code(p, "cpp").replace("        \n", "        return {};\n"), include_hidden=False)
    assert cpp.status == "wrong_answer"


def test_compile_error_is_reported_with_user_line_numbers():
    p = get_problem("two-sum")
    report = grade(p, "cpp", "class Solution {\npublic:\n  vector<int> twoSum(vector<int>& nums, int target) { return nums }\n};", False)
    assert report.status == "compile_error"
    assert "solution.cpp:3" in report.compile_output


def test_python_syntax_error_is_compile_error():
    p = get_problem("two-sum")
    report = grade(p, "python", "class Solution:\n    def twoSum(self, nums, target)\n        return []\n", False)
    assert report.status == "compile_error"


def test_runtime_error_and_debug_output():
    p = get_problem("binary-search")
    code = "class Solution:\n    def search(self, nums, target):\n        print('debug', len(nums))\n        return nums[100]\n"
    report = grade(p, "python", code, False)
    assert report.status == "runtime_error"
    assert "IndexError" in report.tests[0].error
    assert "debug" in report.stdout


def test_infinite_loop_times_out():
    p = get_problem("binary-search")
    report = grade(p, "cpp", "class Solution { public: int search(vector<int>& n, int t) { while (true) {} } };", False)
    assert report.status == "timeout"


def test_hidden_tests_do_not_expose_inputs():
    p = get_problem("two-sum")
    report = grade(p, "python", "class Solution:\n    def twoSum(self, nums, target):\n        return [0, 1]\n", True)
    hidden = [t for t in report.public()["tests"] if t["hidden"]]
    assert hidden and all("args" not in t and "expected" not in t for t in hidden)


def test_spoofed_marker_is_ignored():
    p = get_problem("two-sum")
    code = "class Solution:\n    def twoSum(self, nums, target):\n        print('\\n@@IV@@ 0 ok [0, 1]')\n        return []\n"
    report = grade(p, "python", code, False)
    assert report.passed == 0
