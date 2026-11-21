class Solution { public:
    bool isSubsequence(string s, string t) { size_t pos = 0; for (char c : s) { size_t f = t.find(c, pos); if (f == string::npos) return false; pos = f + 1; } return true; }
};
