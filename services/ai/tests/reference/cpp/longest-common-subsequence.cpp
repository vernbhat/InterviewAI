class Solution { public:
    int longestCommonSubsequence(string a, string b) { int m = a.size(), n = b.size(); vector<vector<int>> d(m + 1, vector<int>(n + 1, 0));
        for (int i = m - 1; i >= 0; i--) for (int j = n - 1; j >= 0; j--) d[i][j] = a[i] == b[j] ? d[i+1][j+1] + 1 : max(d[i+1][j], d[i][j+1]); return d[0][0]; }
};
