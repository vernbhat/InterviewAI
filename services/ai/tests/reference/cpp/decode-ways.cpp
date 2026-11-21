class Solution { public:
    int numDecodings(string s) { int n = s.size(); vector<long long> d(n + 1, 0); d[n] = 1;
        for (int i = n - 1; i >= 0; i--) { if (s[i] == '0') continue; d[i] = d[i+1]; if (i + 1 < n && (s[i] == '1' || (s[i] == '2' && s[i+1] <= '6'))) d[i] += d[i+2]; } return (int)d[0]; }
};
