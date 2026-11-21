class Solution { public:
    bool canJump(vector<int>& a) { int goal = (int)a.size() - 1; for (int i = (int)a.size() - 1; i >= 0; i--) if (i + a[i] >= goal) goal = i; return goal == 0; }
};
