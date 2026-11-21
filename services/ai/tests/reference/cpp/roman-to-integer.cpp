class Solution { public:
    int romanToInt(string s) { map<char,int> v{{'I',1},{'V',5},{'X',10},{'L',50},{'C',100},{'D',500},{'M',1000}}; int total = 0, prev = 0;
        for (int i = (int)s.size() - 1; i >= 0; i--) { int x = v[s[i]]; if (x < prev) total -= x; else { total += x; prev = x; } } return total; }
};
