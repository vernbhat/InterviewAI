class Solution {
    void fill(vector<vector<int>>& g, int r, int c) {
        if (r < 0 || c < 0 || r >= (int)g.size() || c >= (int)g[0].size() || g[r][c] != 1) return;
        g[r][c] = 2;
        fill(g, r + 1, c); fill(g, r - 1, c); fill(g, r, c + 1); fill(g, r, c - 1);
    }
public:
    int numIslands(vector<vector<int>>& grid) {
        int count = 0;
        for (int r = 0; r < (int)grid.size(); ++r)
            for (int c = 0; c < (int)grid[r].size(); ++c)
                if (grid[r][c] == 1) { ++count; fill(grid, r, c); }
        return count;
    }
};
