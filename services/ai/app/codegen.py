"""Starter code and test-harness generation for C++ and Python.

Supported parameter/return types: int, long, bool, string, int[], string[], int[][].
Harness output protocol: one line per test, ``@@IV@@ <index> <status> <payload>``
where status is ``ok`` (payload is the JSON-serialised return value) or ``err``
(payload is a JSON string with the error message). Anything else on stdout is
the candidate's own debug output.
"""

from __future__ import annotations

import json
from typing import Any

MARK = "@@IV@@"

CPP_TYPES = {
    "int": "int",
    "long": "long long",
    "bool": "bool",
    "string": "string",
    "int[]": "vector<int>",
    "string[]": "vector<string>",
    "int[][]": "vector<vector<int>>",
}

PY_TYPES = {
    "int": "int",
    "long": "int",
    "bool": "bool",
    "string": "str",
    "int[]": "list[int]",
    "string[]": "list[str]",
    "int[][]": "list[list[int]]",
}


def _cpp_param(name: str, typ: str) -> str:
    base = CPP_TYPES[typ]
    if typ in ("int", "long", "bool"):
        return f"{base} {name}"
    return f"{base}& {name}"


def starter_code(problem: dict[str, Any], language: str) -> str:
    fn = problem["function"]
    if language == "cpp":
        params = ", ".join(_cpp_param(p["name"], p["type"]) for p in fn["params"])
        ret = CPP_TYPES[fn["returns"]]
        return (
            "#include <bits/stdc++.h>\n"
            "using namespace std;\n\n"
            "class Solution {\n"
            "public:\n"
            f"    {ret} {fn['name']}({params}) {{\n"
            "        // Explain your approach to the interviewer before you code.\n"
            "        \n"
            "    }\n"
            "};\n"
        )
    if language == "python":
        params = ", ".join(f"{p['name']}: {PY_TYPES[p['type']]}" for p in fn["params"])
        ret = PY_TYPES[fn["returns"]]
        return (
            "class Solution:\n"
            f"    def {fn['name']}(self, {params}) -> {ret}:\n"
            "        # Explain your approach to the interviewer before you code.\n"
            "        pass\n"
        )
    raise ValueError(f"unsupported language: {language}")


# --------------------------------------------------------------------------- #
# C++
# --------------------------------------------------------------------------- #

def _cpp_literal(value: Any, typ: str) -> str:
    if typ in ("int", "long"):
        v = int(value)
        return f"{v}LL" if typ == "long" else str(v)
    if typ == "bool":
        return "true" if value else "false"
    if typ == "string":
        return f"string({json.dumps(value, ensure_ascii=True)})"
    if typ == "int[]":
        return "vector<int>{" + ", ".join(str(int(v)) for v in value) + "}"
    if typ == "string[]":
        return "vector<string>{" + ", ".join(json.dumps(v, ensure_ascii=True) for v in value) + "}"
    if typ == "int[][]":
        return "vector<vector<int>>{" + ", ".join(_cpp_literal(row, "int[]") for row in value) + "}"
    raise ValueError(f"unsupported type: {typ}")


CPP_PRELUDE = "#include <bits/stdc++.h>\nusing namespace std;\n#line 1 \"solution.cpp\"\n"

CPP_SERIALISER = r"""
namespace iv_harness {
inline std::string ser(int v) { return std::to_string(v); }
inline std::string ser(long long v) { return std::to_string(v); }
inline std::string ser(long v) { return std::to_string(v); }
inline std::string ser(bool v) { return v ? "true" : "false"; }
inline std::string ser(const std::string& s) {
    std::string o = "\"";
    for (unsigned char c : s) {
        if (c == '"' || c == '\\') { o += '\\'; o += (char)c; }
        else if (c == '\n') o += "\\n";
        else if (c < 0x20) { char b[8]; std::snprintf(b, sizeof b, "\\u%04x", c); o += b; }
        else o += (char)c;
    }
    return o + "\"";
}
inline std::string ser(const char* s) { return ser(std::string(s)); }
template <class T> std::string ser(const std::vector<T>& v) {
    std::string o = "[";
    for (size_t i = 0; i < v.size(); ++i) { if (i) o += ","; o += ser(v[i]); }
    return o + "]";
}
inline std::string ser(const std::vector<bool>& v) {
    std::string o = "[";
    for (size_t i = 0; i < v.size(); ++i) { if (i) o += ","; o += v[i] ? "true" : "false"; }
    return o + "]";
}
}  // namespace iv_harness
"""


def cpp_program(problem: dict[str, Any], code: str, tests: list[dict[str, Any]], mark: str = MARK) -> str:
    fn = problem["function"]
    blocks = []
    for idx, test in enumerate(tests):
        decls = []
        names = []
        for p, arg in zip(fn["params"], test["args"]):
            var = f"a_{p['name']}"
            decls.append(f"        {CPP_TYPES[p['type']]} {var} = {_cpp_literal(arg, p['type'])};")
            names.append(var)
        blocks.append(
            "    {\n"
            "      try {\n"
            + "\n".join(decls)
            + "\n        Solution sol;\n"
            f"        auto res = sol.{fn['name']}({', '.join(names)});\n"
            f"        std::cout << std::flush; std::cout << \"\\n{mark} {idx} ok \" << iv_harness::ser(res) << std::endl;\n"
            "      } catch (const std::exception& e) {\n"
            f"        std::cout << \"\\n{mark} {idx} err \" << iv_harness::ser(std::string(e.what())) << std::endl;\n"
            "      } catch (...) {\n"
            f"        std::cout << \"\\n{mark} {idx} err \\\"unknown exception\\\"\" << std::endl;\n"
            "      }\n"
            "    }"
        )
    main = "int main() {\n    std::ios::sync_with_stdio(true);\n" + "\n".join(blocks) + "\n    return 0;\n}\n"
    return CPP_PRELUDE + code + "\n#line 1 \"harness.cpp\"\n" + CPP_SERIALISER + main


# --------------------------------------------------------------------------- #
# Python
# --------------------------------------------------------------------------- #

PY_HARNESS = r'''

# ---- InterviewAI harness ----
def _iv_main():
    import copy as _copy, json as _json, sys as _sys
    _tests = _json.loads(__IV_TESTS__)
    for _i, _args in enumerate(_tests):
        try:
            _res = getattr(Solution(), __IV_FN__)(*_copy.deepcopy(_args))
            _payload = _json.dumps(_res)
            print("\n" + __IV_MARK__ + " " + str(_i) + " ok " + _payload, flush=True)
        except Exception as _e:
            _msg = type(_e).__name__ + ": " + str(_e)
            print("\n" + __IV_MARK__ + " " + str(_i) + " err " + _json.dumps(_msg), flush=True)

_iv_main()
'''


def python_program(problem: dict[str, Any], code: str, tests: list[dict[str, Any]], mark: str = MARK) -> str:
    args = json.dumps([t["args"] for t in tests])
    harness = (
        PY_HARNESS.replace("__IV_TESTS__", repr(args))
        .replace("__IV_FN__", repr(problem["function"]["name"]))
        .replace("__IV_MARK__", repr(mark))
    )
    return "from __future__ import annotations\nfrom typing import *\n" + code + harness


def build_program(problem: dict[str, Any], language: str, code: str, tests: list[dict[str, Any]], mark: str = MARK) -> str:
    if language == "cpp":
        return cpp_program(problem, code, tests, mark)
    if language == "python":
        return python_program(problem, code, tests, mark)
    raise ValueError(f"unsupported language: {language}")


def parse_output(stdout: str, count: int, mark: str = MARK) -> tuple[dict[int, tuple[str, Any]], str]:
    """Return ({index: (status, value)}, candidate_stdout)."""
    results: dict[int, tuple[str, Any]] = {}
    other: list[str] = []
    for line in stdout.splitlines():
        if line.startswith(mark + " "):
            try:
                _, idx, status, payload = line.split(" ", 3)
                i = int(idx)
                if 0 <= i < count:
                    results[i] = (status, json.loads(payload))
                    continue
            except (ValueError, json.JSONDecodeError):
                pass
        other.append(line)
    candidate = "\n".join(other).strip("\n")
    return results, candidate
