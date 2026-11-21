class Solution { public:
    int orangesRotting(vector<vector<int>>& g) { int R = g.size(), C = g[0].size(), t = 0;
        while (true) { vector<vector<int>> n = g; bool changed = false;
            for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) if (g[r][c] == 1) { int dr[] = {1,-1,0,0}, dc[] = {0,0,1,-1};
                for (int k = 0; k < 4; k++) { int y = r + dr[k], x = c + dc[k]; if (y >= 0 && y < R && x >= 0 && x < C && g[y][x] == 2) { n[r][c] = 2; changed = true; break; } } }
            if (!changed) break; g = n; t++; }
        for (auto& row : g) for (int v : row) if (v == 1) return -1; return t; }
};
