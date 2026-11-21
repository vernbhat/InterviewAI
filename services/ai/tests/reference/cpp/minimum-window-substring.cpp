class Solution { public:
    string minWindow(string s, string t) { int n = s.size(); map<char,int> need; for (char c : t) need[c]++;
        for (int len = 1; len <= n; len++) for (int i = 0; i + len <= n; i++) { map<char,int> have; for (int j = i; j < i + len; j++) have[s[j]]++;
            bool ok = true; for (auto& [c, k] : need) if (have[c] < k) { ok = false; break; } if (ok) return s.substr(i, len); } return ""; }
};
