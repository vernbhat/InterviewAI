class Solution { public:
    int firstMissingPositive(vector<int>& nums) { set<long long> s(nums.begin(), nums.end()); long long k = 1; while (s.count(k)) k++; return (int)k; }
};
