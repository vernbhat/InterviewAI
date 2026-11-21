class Solution { public:
    int uniquePaths(int m, int n) { long long r = 1; for (int i = 1; i <= m - 1; i++) r = r * (n - 1 + i) / i; return (int)r; }
};
