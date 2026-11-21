class Solution { public:
    int longestValidParentheses(string s) { int best = 0, l = 0, r = 0; for (char c : s) { c == '(' ? l++ : r++; if (l == r) best = max(best, 2 * r); else if (r > l) l = r = 0; }
        l = r = 0; for (int i = (int)s.size() - 1; i >= 0; i--) { s[i] == '(' ? l++ : r++; if (l == r) best = max(best, 2 * l); else if (l > r) l = r = 0; } return best; }
};
