class Solution { public:
    bool m(const string& s, const string& p, int i, int j) { if (j == (int)p.size()) return i == (int)s.size();
        bool first = i < (int)s.size() && (p[j] == s[i] || p[j] == '.');
        if (j + 1 < (int)p.size() && p[j+1] == '*') return m(s, p, i, j + 2) || (first && m(s, p, i + 1, j)); return first && m(s, p, i + 1, j + 1); }
    bool isMatch(string s, string p) { return m(s, p, 0, 0); }
};
