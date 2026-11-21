class Solution { public:
    int lengthOfLIS(vector<int>& a) { int n = a.size(), best = 0; vector<int> d(n, 1); for (int i = 0; i < n; i++) { for (int j = 0; j < i; j++) if (a[j] < a[i]) d[i] = max(d[i], d[j] + 1); best = max(best, d[i]); } return best; }
};
