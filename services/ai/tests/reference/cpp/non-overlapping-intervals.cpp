class Solution { public:
    int eraseOverlapIntervals(vector<vector<int>>& iv) { sort(iv.begin(), iv.end()); int removed = 0; int end = iv[0][1];
        for (size_t i = 1; i < iv.size(); i++) { if (iv[i][0] < end) { removed++; end = min(end, iv[i][1]); } else end = iv[i][1]; } return removed; }
};
