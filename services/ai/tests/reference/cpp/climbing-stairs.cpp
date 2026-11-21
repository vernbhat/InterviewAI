class Solution { public:
    int climbStairs(int n) { vector<long long> d(n + 2); d[0] = 1; d[1] = 1; for (int i = 2; i <= n; i++) d[i] = d[i-1] + d[i-2]; return (int)d[n]; }
};
