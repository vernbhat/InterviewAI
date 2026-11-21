class Solution { public:
    bool isPalindrome(string s) { int l = 0, r = (int)s.size() - 1;
        while (l < r) { if (!isalnum((unsigned char)s[l])) { l++; continue; } if (!isalnum((unsigned char)s[r])) { r--; continue; }
            if (tolower(s[l]) != tolower(s[r])) return false; l++; r--; } return true; }
};
