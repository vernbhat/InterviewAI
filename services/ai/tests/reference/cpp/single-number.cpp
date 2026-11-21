class Solution { public:
    int singleNumber(vector<int>& nums) { unordered_map<int,int> c; for (int x : nums) c[x]++; for (auto& [k, v] : c) if (v == 1) return k; return 0; }
};
