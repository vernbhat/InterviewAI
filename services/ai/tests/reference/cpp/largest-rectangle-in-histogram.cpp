class Solution { public:
    int largestRectangleArea(vector<int>& h) { int n = h.size(), best = 0; for (int i = 0; i < n; i++) { int mn = INT_MAX; for (int j = i; j < n; j++) { mn = min(mn, h[j]); best = max(best, mn * (j - i + 1)); } } return best; }
};
