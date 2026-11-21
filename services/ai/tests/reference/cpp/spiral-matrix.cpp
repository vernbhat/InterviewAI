class Solution { public:
    vector<int> spiralOrder(vector<vector<int>>& m) { int R = m.size(), C = m[0].size(); vector<vector<char>> seen(R, vector<char>(C, 0)); vector<int> out;
        int dr[] = {0,1,0,-1}, dc[] = {1,0,-1,0}, r = 0, c = 0, d = 0;
        for (int k = 0; k < R * C; k++) { out.push_back(m[r][c]); seen[r][c] = 1; int nr = r + dr[d], nc = c + dc[d];
            if (nr < 0 || nr >= R || nc < 0 || nc >= C || seen[nr][nc]) { d = (d + 1) % 4; nr = r + dr[d]; nc = c + dc[d]; } r = nr; c = nc; } return out; }
};
