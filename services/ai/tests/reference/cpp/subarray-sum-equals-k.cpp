class Solution { public:
    int subarraySum(vector<int>& a, int k) { int c = 0; for (size_t i = 0; i < a.size(); i++) { int s = 0; for (size_t j = i; j < a.size(); j++) { s += a[j]; if (s == k) c++; } } return c; }
};
