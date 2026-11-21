class Solution { public:
    int countSubstrings(string s) { int n = s.size(), c = 0; vector<vector<char>> p(n, vector<char>(n, 0));
        for (int i = n - 1; i >= 0; i--) for (int j = i; j < n; j++) if (s[i] == s[j] && (j - i < 2 || p[i+1][j-1])) { p[i][j] = 1; c++; } return c; }
};
