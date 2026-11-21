class Solution {
public:
    int coinChange(vector<int>& coins, int amount) {
        vector<int> dp(amount + 1, amount + 1);
        dp[0] = 0;
        for (int v = 1; v <= amount; ++v)
            for (int c : coins)
                if (c <= v) dp[v] = min(dp[v], dp[v - c] + 1);
        return dp[amount] > amount ? -1 : dp[amount];
    }
};
