class Solution { public:
    vector<int> countBits(int n) { vector<int> out; for (int i = 0; i <= n; i++) out.push_back(__builtin_popcount(i)); return out; }
};
