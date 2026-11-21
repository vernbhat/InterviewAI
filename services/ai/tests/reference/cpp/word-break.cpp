class Solution { public:
    bool wordBreak(string s, vector<string>& dict) { int n = s.size(); vector<char> ok(n + 1, 0); ok[n] = 1;
        for (int i = n - 1; i >= 0; i--) for (auto& w : dict) if (i + w.size() <= (size_t)n && ok[i + w.size()] && s.compare(i, w.size(), w) == 0) { ok[i] = 1; break; } return ok[0]; }
};
