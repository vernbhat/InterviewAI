class Solution { public:
    int missingNumber(vector<int>& nums) { int x = 0; for (int i = 0; i < (int)nums.size(); i++) x ^= i ^ nums[i]; return x ^ (int)nums.size(); }
};
