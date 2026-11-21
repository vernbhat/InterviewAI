class Solution { public:
    bool isAnagram(string s, string t) { if (s.size() != t.size()) return false; int c[26] = {0}; for (char ch : s) c[ch-'a']++; for (char ch : t) if (--c[ch-'a'] < 0) return false; return true; }
};
