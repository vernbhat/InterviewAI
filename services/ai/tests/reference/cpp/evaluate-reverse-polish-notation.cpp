class Solution { public:
    int evalRPN(vector<string>& tokens) { vector<long long> st; for (auto& t : tokens) {
        if (t == "+" || t == "-" || t == "*" || t == "/") { long long b = st.back(); st.pop_back(); long long a = st.back(); st.pop_back();
            st.push_back(t == "+" ? a + b : t == "-" ? a - b : t == "*" ? a * b : a / b); } else st.push_back(stoll(t)); } return (int)st.back(); }
};
