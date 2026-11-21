class Solution { public:
    int search(vector<int>& nums, int target) { int n = nums.size(), lo = 0, hi = n - 1; while (lo < hi) { int m = (lo + hi) / 2; if (nums[m] > nums[hi]) lo = m + 1; else hi = m; }
        int rot = lo; lo = 0; hi = n - 1; while (lo <= hi) { int m = (lo + hi) / 2, real = (m + rot) % n; if (nums[real] == target) return real; if (nums[real] < target) lo = m + 1; else hi = m - 1; } return -1; }
};
