class Solution { public:
    int maxArea(vector<int>& h) { int best = 0; for (size_t i = 0; i < h.size(); i++) for (size_t j = i + 1; j < h.size(); j++) best = max(best, (int)(j - i) * min(h[i], h[j])); return best; }
};
