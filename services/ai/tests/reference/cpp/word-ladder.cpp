class Solution { public:
    int ladderLength(string b, string e, vector<string>& words) { vector<string> nodes = words; nodes.push_back(b); int n = nodes.size();
        auto adj = [&](const string& x, const string& y) { if (x.size() != y.size()) return false; int d = 0; for (size_t i = 0; i < x.size(); i++) d += x[i] != y[i]; return d == 1; };
        vector<int> dist(n, 0); queue<int> q; q.push(n - 1); dist[n - 1] = 1;
        while (!q.empty()) { int u = q.front(); q.pop(); if (nodes[u] == e && u != n - 1) return dist[u]; for (int v = 0; v < n - 1; v++) if (!dist[v] && adj(nodes[u], nodes[v])) { dist[v] = dist[u] + 1; q.push(v); } }
        return 0; }
};
