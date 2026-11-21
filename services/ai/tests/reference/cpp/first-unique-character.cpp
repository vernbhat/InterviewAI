class Solution { public:
    int firstUniqChar(string s) { int c[26] = {0}; for (char ch : s) c[ch-'a']++; for (int i = 0; i < (int)s.size(); i++) if (c[s[i]-'a'] == 1) return i; return -1; }
};
