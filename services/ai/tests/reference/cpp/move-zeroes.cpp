class Solution { public:
    vector<int> moveZeroes(vector<int>& nums) { int w = 0; for (int i = 0; i < (int)nums.size(); i++) if (nums[i] != 0) swap(nums[w++], nums[i]); return nums; }
};
