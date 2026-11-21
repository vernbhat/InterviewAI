class Solution { public:
    vector<string> generateParenthesis(int n) { vector<string> out; for (int mask = 0; mask < (1 << (2*n)); mask++) { string s; int bal = 0; bool ok = true;
        for (int i = 2*n - 1; i >= 0; i--) { char ch = (mask >> i) & 1 ? ')' : '('; s += ch; bal += ch == '(' ? 1 : -1; if (bal < 0) { ok = false; break; } }
        if (ok && bal == 0) out.push_back(s); } sort(out.begin(), out.end()); return out; }
};
