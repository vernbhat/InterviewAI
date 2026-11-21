class Solution { public:
    vector<int> mergeSorted(vector<int>& a, vector<int>& b) { vector<int> out(a.size() + b.size()); int i = (int)a.size() - 1, j = (int)b.size() - 1, k = (int)out.size() - 1;
        while (j >= 0) { if (i >= 0 && a[i] > b[j]) out[k--] = a[i--]; else out[k--] = b[j--]; } while (i >= 0) out[k--] = a[i--]; return out; }
};
