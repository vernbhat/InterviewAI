class Solution { public:
    vector<int> maxSlidingWindow(vector<int>& a, int k) { multiset<int> w; vector<int> out; for (int i = 0; i < (int)a.size(); i++) { w.insert(a[i]);
        if (i >= k) w.erase(w.find(a[i-k])); if (i >= k - 1) out.push_back(*w.rbegin()); } return out; }
};
