class Solution { public:
    vector<int> topKFrequent(vector<int>& nums, int k) { map<int,int> c; for (int x : nums) c[x]++; vector<pair<int,int>> v; for (auto& [x, f] : c) v.push_back({-f, x});
        sort(v.begin(), v.end()); vector<int> out; for (int i = 0; i < k; i++) out.push_back(v[i].second); return out; }
};
