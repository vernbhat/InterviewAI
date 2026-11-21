class Solution { public:
    vector<vector<int>> threeSum(vector<int>& nums) { set<vector<int>> s; int n = nums.size();
        for (int i = 0; i < n; i++) { unordered_set<int> seen; for (int j = i + 1; j < n; j++) { int need = -nums[i] - nums[j];
            if (seen.count(need)) { vector<int> t{nums[i], nums[j], need}; sort(t.begin(), t.end()); s.insert(t); } seen.insert(nums[j]); } }
        return vector<vector<int>>(s.begin(), s.end()); }
};
