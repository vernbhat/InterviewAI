class Solution { public:
    int maxSubArray(vector<int>& a) { // prefix-sum formulation
        long long best = LLONG_MIN, pre = 0, mn = 0; for (int x : a) { pre += x; best = max(best, pre - mn); mn = min(mn, pre); } return (int)best; }
};
