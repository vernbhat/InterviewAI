class Solution { public:
    int longestConsecutive(vector<int>& nums) { if (nums.empty()) return 0; vector<int> a = nums; sort(a.begin(), a.end()); a.erase(unique(a.begin(), a.end()), a.end());
        int best = 1, run = 1; for (size_t i = 1; i < a.size(); i++) { run = (a[i] == a[i-1] + 1) ? run + 1 : 1; best = max(best, run); } return best; }
};
