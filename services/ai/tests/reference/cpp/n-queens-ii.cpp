class Solution { public:
    int n, cnt = 0; void go(int r, int cols, int d1, int d2) { if (r == n) { cnt++; return; } int avail = ((1 << n) - 1) & ~(cols | d1 | d2);
        while (avail) { int bit = avail & -avail; avail -= bit; go(r + 1, cols | bit, (d1 | bit) << 1, (d2 | bit) >> 1); } }
    int totalNQueens(int N) { n = N; go(0, 0, 0, 0); return cnt; }
};
