class Solution { public:
    int characterReplacement(string s, int k) { int n = s.size(), best = 0; for (int i = 0; i < n; i++) { int c[26] = {0}, mx = 0;
        for (int j = i; j < n; j++) { mx = max(mx, ++c[s[j]-'A']); if (j - i + 1 - mx <= k) best = max(best, j - i + 1); } } return best; }
};
