class Solution { public:
    int majorityElement(vector<int>& nums) { unordered_map<int,int> c; for (int x : nums) if (++c[x] * 2 > (int)nums.size()) return x; return -1; }
};
