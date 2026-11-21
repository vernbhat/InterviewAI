class Solution { public:
    vector<vector<int>> adj; vector<int> color;
    bool cyc(int u) { color[u] = 1; for (int v : adj[u]) { if (color[v] == 1) return true; if (color[v] == 0 && cyc(v)) return true; } color[u] = 2; return false; }
    bool canFinish(int n, vector<vector<int>>& pre) { adj.assign(n, {}); color.assign(n, 0); for (auto& p : pre) adj[p[1]].push_back(p[0]);
        for (int i = 0; i < n; i++) if (color[i] == 0 && cyc(i)) return false; return true; }
};
