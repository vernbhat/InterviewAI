class Solution { public:
    vector<int> sortedSquares(vector<int>& a) { int n = a.size(), l = 0, r = n - 1; vector<int> out(n);
        for (int k = n - 1; k >= 0; k--) { if (abs(a[l]) > abs(a[r])) { out[k] = a[l]*a[l]; l++; } else { out[k] = a[r]*a[r]; r--; } } return out; }
};
