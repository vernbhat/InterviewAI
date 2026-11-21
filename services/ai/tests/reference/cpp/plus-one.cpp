class Solution { public:
    vector<int> plusOne(vector<int>& d) { int carry = 1; for (int i = (int)d.size() - 1; i >= 0 && carry; i--) { int v = d[i] + carry; d[i] = v % 10; carry = v / 10; }
        if (carry) d.insert(d.begin(), 1); return d; }
};
