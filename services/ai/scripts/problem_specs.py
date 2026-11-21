"""Source of truth for the InterviewAI problem bank.

Each spec holds the statement, the function signature, hand-written edge cases,
a seeded random-input generator and a Python reference solution. Run
``python scripts/build_problems.py`` to regenerate ``app/data/problems/*.json``.
Expected outputs are always computed by the reference solution, never typed by
hand, so a test can only be wrong if the reference is wrong (and the reference
is cross-checked against an independent C++ solution in the test suite).
"""

from __future__ import annotations

import random
from typing import Any, Callable


# --------------------------------------------------------------------------- #
# Reference solutions (Python). Kept deliberately plain.
# --------------------------------------------------------------------------- #

def two_sum(nums: list[int], target: int) -> list[int]:
    seen: dict[int, int] = {}
    for i, x in enumerate(nums):
        if target - x in seen:
            return [seen[target - x], i]
        seen[x] = i
    return []


def valid_parentheses(s: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}
    stack: list[str] = []
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif not stack or stack.pop() != pairs[ch]:
            return False
    return not stack


def max_profit(prices: list[int]) -> int:
    best, low = 0, float("inf")
    for p in prices:
        low = min(low, p)
        best = max(best, p - low)
    return int(best)


def binary_search(nums: list[int], target: int) -> int:
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def length_of_longest_substring(s: str) -> int:
    last: dict[str, int] = {}
    start = best = 0
    for i, ch in enumerate(s):
        if ch in last and last[ch] >= start:
            start = last[ch] + 1
        last[ch] = i
        best = max(best, i - start + 1)
    return best


def product_except_self(nums: list[int]) -> list[int]:
    n = len(nums)
    out = [1] * n
    acc = 1
    for i in range(n):
        out[i] = acc
        acc *= nums[i]
    acc = 1
    for i in range(n - 1, -1, -1):
        out[i] *= acc
        acc *= nums[i]
    return out


def num_islands(grid: list[list[int]]) -> int:
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    seen = [[False] * cols for _ in range(rows)]
    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1 and not seen[r][c]:
                count += 1
                stack = [(r, c)]
                seen[r][c] = True
                while stack:
                    y, x = stack.pop()
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < rows and 0 <= nx < cols and grid[ny][nx] == 1 and not seen[ny][nx]:
                            seen[ny][nx] = True
                            stack.append((ny, nx))
    return count


def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    out: list[list[int]] = []
    for a, b in sorted(intervals):
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def coin_change(coins: list[int], amount: int) -> int:
    inf = amount + 1
    dp = [0] + [inf] * amount
    for v in range(1, amount + 1):
        for c in coins:
            if c <= v and dp[v - c] + 1 < dp[v]:
                dp[v] = dp[v - c] + 1
    return dp[amount] if dp[amount] != inf else -1


def find_kth_largest(nums: list[int], k: int) -> int:
    return sorted(nums, reverse=True)[k - 1]


def trap(height: list[int]) -> int:
    l, r = 0, len(height) - 1
    lmax = rmax = water = 0
    while l < r:
        if height[l] < height[r]:
            lmax = max(lmax, height[l])
            water += lmax - height[l]
            l += 1
        else:
            rmax = max(rmax, height[r])
            water += rmax - height[r]
            r -= 1
    return water


def min_distance(word1: str, word2: str) -> int:
    m, n = len(word1), len(word2)
    prev = list(range(n + 1))
    for i in range(1, m + 1):
        cur = [i] + [0] * n
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                cur[j] = prev[j - 1]
            else:
                cur[j] = 1 + min(prev[j], cur[j - 1], prev[j - 1])
        prev = cur
    return prev[n]


# --------------------------------------------------------------------------- #
# Random generators (seeded per problem in build_problems.py).
# --------------------------------------------------------------------------- #

def gen_two_sum(rng: random.Random) -> list[Any]:
    n = rng.randint(2, 30)
    # Build an array with exactly one valid pair.
    while True:
        nums = rng.sample(range(-200, 200), n)
        i, j = sorted(rng.sample(range(n), 2))
        target = nums[i] + nums[j]
        pairs = [(a, b) for a in range(n) for b in range(a + 1, n) if nums[a] + nums[b] == target]
        if len(pairs) == 1:
            return [nums, target]


def gen_parens(rng: random.Random) -> list[Any]:
    if rng.random() < 0.5:
        # Build a balanced string.
        out, stack = [], []
        for _ in range(rng.randint(1, 12)):
            if stack and rng.random() < 0.45:
                out.append({"(": ")", "[": "]", "{": "}"}[stack.pop()])
            else:
                ch = rng.choice("([{")
                stack.append(ch)
                out.append(ch)
        out += [{"(": ")", "[": "]", "{": "}"}[c] for c in reversed(stack)]
        return ["".join(out)]
    return ["".join(rng.choice("()[]{}") for _ in range(rng.randint(1, 16)))]


def gen_prices(rng: random.Random) -> list[Any]:
    return [[rng.randint(0, 100) for _ in range(rng.randint(1, 25))]]


def gen_bsearch(rng: random.Random) -> list[Any]:
    nums = sorted(rng.sample(range(-100, 100), rng.randint(1, 30)))
    target = rng.choice(nums) if rng.random() < 0.6 else rng.randint(-110, 110)
    return [nums, target]


def gen_substring(rng: random.Random) -> list[Any]:
    alphabet = rng.choice(["ab", "abc", "abcdef", "abcdefghijklmnop"])
    return ["".join(rng.choice(alphabet) for _ in range(rng.randint(0, 30)))]


def gen_product(rng: random.Random) -> list[Any]:
    return [[rng.randint(-5, 5) for _ in range(rng.randint(2, 10))]]


def gen_islands(rng: random.Random) -> list[Any]:
    rows, cols = rng.randint(1, 8), rng.randint(1, 8)
    p = rng.uniform(0.3, 0.6)
    return [[[1 if rng.random() < p else 0 for _ in range(cols)] for _ in range(rows)]]


def gen_intervals(rng: random.Random) -> list[Any]:
    out = []
    for _ in range(rng.randint(1, 10)):
        a = rng.randint(0, 40)
        out.append([a, a + rng.randint(0, 8)])
    return [out]


def gen_coins(rng: random.Random) -> list[Any]:
    coins = sorted(rng.sample(range(1, 30), rng.randint(1, 4)))
    return [coins, rng.randint(0, 120)]


def gen_kth(rng: random.Random) -> list[Any]:
    nums = [rng.randint(-50, 50) for _ in range(rng.randint(1, 25))]
    return [nums, rng.randint(1, len(nums))]


def gen_trap(rng: random.Random) -> list[Any]:
    return [[rng.randint(0, 6) for _ in range(rng.randint(1, 25))]]


def gen_edit(rng: random.Random) -> list[Any]:
    alphabet = rng.choice(["ab", "abc", "abcdefg"])
    return ["".join(rng.choice(alphabet) for _ in range(rng.randint(0, 10))),
            "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 10)))]


# --------------------------------------------------------------------------- #
# Specs
# --------------------------------------------------------------------------- #

Spec = dict[str, Any]

SPECS: list[Spec] = [
    {
        "id": "two-sum",
        "title": "Two Sum",
        "difficulty": "Easy",
        "pattern": "Array, hash map",
        "statement": "Given an integer array `nums` and an integer `target`, return the indices of the two numbers that add up to `target`, as `[i, j]` with `i < j`. Exactly one valid pair exists, and you may not use the same element twice.",
        "constraints": ["2 <= nums.length <= 10^4", "-10^9 <= nums[i], target <= 10^9", "Exactly one valid answer exists."],
        "function": {"name": "twoSum", "params": [["nums", "int[]"], ["target", "int"]], "returns": "int[]"},
        "examples": [
            {"args": [[2, 7, 11, 15], 9], "explanation": "nums[0] + nums[1] = 9."},
            {"args": [[3, 2, 4], 6], "explanation": "nums[1] + nums[2] = 6."},
            {"args": [[3, 3], 6], "explanation": "Two different indices may hold equal values."},
        ],
        "edge_cases": [[[-1, -2, -3, -4, -5], -8], [[0, 4, 3, 0], 0], [[1, 5, 1000000000, -999999995], 5]],
        "generator": gen_two_sum,
        "reference": two_sum,
        "complexity": {"time": "O(n)", "space": "O(n)"},
        "hints": [
            "What would a brute-force check of every pair cost? Can you avoid re-scanning the array for each element?",
            "For each value x, you need to know quickly whether target - x has already appeared, and where.",
            "Walk the array once, keeping a hash map from value to index. Check for the complement before inserting the current value.",
        ],
    },
    {
        "id": "valid-parentheses",
        "title": "Valid Parentheses",
        "difficulty": "Easy",
        "pattern": "Stack",
        "statement": "Given a string `s` containing only the characters `()[]{}`, return `true` if every opening bracket is closed by the same type of bracket in the correct order, otherwise `false`.",
        "constraints": ["1 <= s.length <= 10^4", "s consists only of ()[]{}"],
        "function": {"name": "isValid", "params": [["s", "string"]], "returns": "bool"},
        "examples": [
            {"args": ["()[]{}"], "explanation": "Each pair closes immediately."},
            {"args": ["(]"], "explanation": "The bracket types do not match."},
            {"args": ["{[()]}"], "explanation": "Nested pairs close in reverse order."},
        ],
        "edge_cases": [["("], [")"], ["(("], ["([)]"], ["]["]],
        "generator": gen_parens,
        "reference": valid_parentheses,
        "complexity": {"time": "O(n)", "space": "O(n)"},
        "hints": [
            "When you see a closing bracket, which opening bracket must it match?",
            "The most recent unmatched opening bracket is the one that must close first. Which data structure gives you 'most recent' cheaply?",
            "Push opening brackets on a stack; on a closing bracket, pop and compare. At the end the stack must be empty.",
        ],
    },
    {
        "id": "best-time-to-buy-and-sell-stock",
        "title": "Best Time to Buy and Sell Stock",
        "difficulty": "Easy",
        "pattern": "Array, running minimum",
        "statement": "`prices[i]` is the price of a stock on day `i`. Choose one day to buy and a later day to sell. Return the maximum profit, or `0` if no profit is possible.",
        "constraints": ["1 <= prices.length <= 10^5", "0 <= prices[i] <= 10^4"],
        "function": {"name": "maxProfit", "params": [["prices", "int[]"]], "returns": "int"},
        "examples": [
            {"args": [[7, 1, 5, 3, 6, 4]], "explanation": "Buy at 1, sell at 6."},
            {"args": [[7, 6, 4, 3, 1]], "explanation": "Prices only fall, so the answer is 0."},
        ],
        "edge_cases": [[[5]], [[1, 2]], [[2, 4, 1]], [[3, 3, 3]]],
        "generator": gen_prices,
        "reference": max_profit,
        "complexity": {"time": "O(n)", "space": "O(1)"},
        "hints": [
            "If you fix the selling day, what is the best buying day?",
            "As you scan left to right, what single value summarises all earlier buying options?",
            "Track the minimum price seen so far and the best (price - minimum) as you go.",
        ],
    },
    {
        "id": "binary-search",
        "title": "Binary Search",
        "difficulty": "Easy",
        "pattern": "Binary search",
        "statement": "Given a sorted array of distinct integers `nums` and a `target`, return the index of `target`, or `-1` if it is not present. Aim for O(log n).",
        "constraints": ["1 <= nums.length <= 10^4", "nums is sorted ascending and has distinct values"],
        "function": {"name": "search", "params": [["nums", "int[]"], ["target", "int"]], "returns": "int"},
        "examples": [
            {"args": [[-1, 0, 3, 5, 9, 12], 9], "explanation": "9 is at index 4."},
            {"args": [[-1, 0, 3, 5, 9, 12], 2], "explanation": "2 is not present."},
        ],
        "edge_cases": [[[5], 5], [[5], -5], [[1, 3], 3], [[1, 3], 0]],
        "generator": gen_bsearch,
        "reference": binary_search,
        "complexity": {"time": "O(log n)", "space": "O(1)"},
        "hints": [
            "The array is sorted. What does comparing target with the middle element tell you?",
            "Keep a [lo, hi] window that must contain the target if it exists. Be precise about the loop condition.",
            "Loop while lo <= hi; mid = lo + (hi - lo) / 2; move lo to mid + 1 or hi to mid - 1.",
        ],
    },
    {
        "id": "longest-substring-without-repeating",
        "title": "Longest Substring Without Repeating Characters",
        "difficulty": "Medium",
        "pattern": "Sliding window",
        "statement": "Given a string `s`, return the length of the longest substring that contains no repeated characters.",
        "constraints": ["0 <= s.length <= 5 * 10^4", "s consists of printable ASCII characters"],
        "function": {"name": "lengthOfLongestSubstring", "params": [["s", "string"]], "returns": "int"},
        "examples": [
            {"args": ["abcabcbb"], "explanation": "\"abc\" has length 3."},
            {"args": ["bbbbb"], "explanation": "\"b\" has length 1."},
            {"args": ["pwwkew"], "explanation": "\"wke\" has length 3."},
        ],
        "edge_cases": [[""], [" "], ["abba"], ["dvdf"], ["a b c a"]],
        "generator": gen_substring,
        "reference": length_of_longest_substring,
        "complexity": {"time": "O(n)", "space": "O(min(n, alphabet))"},
        "hints": [
            "Checking every substring is O(n^2) or worse. Can you reuse work as the right end moves?",
            "Keep a window with no repeats. When a repeat enters, how far must the left edge jump?",
            "Store the last index of each character. On a repeat inside the window, set left = last[ch] + 1.",
        ],
    },
    {
        "id": "product-of-array-except-self",
        "title": "Product of Array Except Self",
        "difficulty": "Medium",
        "pattern": "Prefix and suffix products",
        "statement": "Given an integer array `nums`, return an array `answer` where `answer[i]` is the product of all elements except `nums[i]`. Do it in O(n) time without using division.",
        "constraints": ["2 <= nums.length <= 10^5", "-30 <= nums[i] <= 30", "Every prefix and suffix product fits in a 32-bit integer."],
        "function": {"name": "productExceptSelf", "params": [["nums", "int[]"]], "returns": "int[]"},
        "examples": [
            {"args": [[1, 2, 3, 4]], "explanation": "[2*3*4, 1*3*4, 1*2*4, 1*2*3]."},
            {"args": [[-1, 1, 0, -3, 3]], "explanation": "Only index 2 avoids the zero."},
        ],
        "edge_cases": [[[0, 0]], [[2, 3]], [[0, 4, 0]], [[-1, -1, -1]]],
        "generator": gen_product,
        "reference": product_except_self,
        "complexity": {"time": "O(n)", "space": "O(1) extra (output excluded)"},
        "hints": [
            "Division breaks with zeros. What two pieces make up 'everything except i'?",
            "answer[i] = (product of everything left of i) * (product of everything right of i).",
            "Fill answer with prefix products in one pass, then multiply in suffix products in a reverse pass with a running variable.",
        ],
    },
    {
        "id": "number-of-islands",
        "title": "Number of Islands",
        "difficulty": "Medium",
        "pattern": "Grid DFS / BFS",
        "statement": "Given an `m x n` grid of `1`s (land) and `0`s (water), return the number of islands. An island is a group of land cells connected horizontally or vertically.",
        "constraints": ["1 <= m, n <= 300", "grid[i][j] is 0 or 1"],
        "function": {"name": "numIslands", "params": [["grid", "int[][]"]], "returns": "int"},
        "examples": [
            {"args": [[[1, 1, 0, 0], [1, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]], "explanation": "Three separate land groups."},
            {"args": [[[1, 1, 1], [0, 1, 0], [1, 1, 1]]], "explanation": "All land connects through the middle column."},
        ],
        "edge_cases": [[[[0]]], [[[1]]], [[[1, 0, 1, 0, 1]]], [[[1], [0], [1]]]],
        "generator": gen_islands,
        "reference": num_islands,
        "complexity": {"time": "O(m * n)", "space": "O(m * n)"},
        "hints": [
            "When you find an unvisited land cell, how do you make sure you never count the rest of its island again?",
            "Each new island start should trigger a flood fill that marks every connected land cell as visited.",
            "Scan all cells; on an unvisited 1, increment the count and run DFS/BFS over 4 neighbours, marking visited.",
        ],
    },
    {
        "id": "merge-intervals",
        "title": "Merge Intervals",
        "difficulty": "Medium",
        "pattern": "Sorting, intervals",
        "statement": "Given an array of `intervals` where `intervals[i] = [start, end]`, merge all overlapping intervals and return the result sorted by start. Intervals that touch (e.g. `[1,4]` and `[4,5]`) count as overlapping.",
        "constraints": ["1 <= intervals.length <= 10^4", "0 <= start <= end <= 10^4"],
        "function": {"name": "merge", "params": [["intervals", "int[][]"]], "returns": "int[][]"},
        "examples": [
            {"args": [[[1, 3], [2, 6], [8, 10], [15, 18]]], "explanation": "[1,3] and [2,6] overlap."},
            {"args": [[[1, 4], [4, 5]]], "explanation": "Touching intervals merge."},
        ],
        "edge_cases": [[[[1, 1]]], [[[5, 6], [1, 2]]], [[[1, 10], [2, 3], [4, 5]]], [[[2, 3], [2, 2], [3, 3], [1, 3]]]],
        "generator": gen_intervals,
        "reference": merge_intervals,
        "complexity": {"time": "O(n log n)", "space": "O(n)"},
        "hints": [
            "Overlaps are hard to find in arbitrary order. What ordering would put candidates next to each other?",
            "After sorting by start, an interval can only overlap with the last interval you kept.",
            "Sort by start; for each interval, extend the last kept end if start <= lastEnd, else push a new interval.",
        ],
    },
    {
        "id": "coin-change",
        "title": "Coin Change",
        "difficulty": "Medium",
        "pattern": "Dynamic programming",
        "statement": "Given coin denominations `coins` (unlimited supply of each) and an `amount`, return the fewest coins needed to make that amount, or `-1` if it cannot be made.",
        "constraints": ["1 <= coins.length <= 12", "1 <= coins[i] <= 2^31 - 1", "0 <= amount <= 10^4"],
        "function": {"name": "coinChange", "params": [["coins", "int[]"], ["amount", "int"]], "returns": "int"},
        "examples": [
            {"args": [[1, 2, 5], 11], "explanation": "5 + 5 + 1."},
            {"args": [[2], 3], "explanation": "Odd amounts cannot be made from 2s."},
            {"args": [[1], 0], "explanation": "Zero coins make amount 0."},
        ],
        "edge_cases": [[[186, 419, 83, 408], 6249], [[2, 5, 10, 1], 27], [[3, 7], 5], [[1, 3, 4], 6]],
        "generator": gen_coins,
        "reference": coin_change,
        "complexity": {"time": "O(amount * coins)", "space": "O(amount)"},
        "hints": [
            "Does always taking the largest coin work? Try coins [1, 3, 4] and amount 6.",
            "Let best(v) be the fewest coins for value v. How does best(v) relate to best(v - c) for each coin c?",
            "Bottom-up DP: dp[0] = 0, dp[v] = 1 + min(dp[v - c]) over coins c <= v; unreachable values stay at infinity.",
        ],
    },
    {
        "id": "kth-largest-element",
        "title": "Kth Largest Element in an Array",
        "difficulty": "Medium",
        "pattern": "Heap / quickselect",
        "statement": "Given an integer array `nums` and an integer `k`, return the `k`th largest element (in sorted order, not the `k`th distinct element).",
        "constraints": ["1 <= k <= nums.length <= 10^5", "-10^4 <= nums[i] <= 10^4"],
        "function": {"name": "findKthLargest", "params": [["nums", "int[]"], ["k", "int"]], "returns": "int"},
        "examples": [
            {"args": [[3, 2, 1, 5, 6, 4], 2], "explanation": "Sorted descending: 6, 5, ..."},
            {"args": [[3, 2, 3, 1, 2, 4, 5, 5, 6], 4], "explanation": "Duplicates count separately."},
        ],
        "edge_cases": [[[1], 1], [[2, 1], 2], [[-1, -1], 1], [[7, 7, 7, 7], 3]],
        "generator": gen_kth,
        "reference": find_kth_largest,
        "complexity": {"time": "O(n log k) with a heap, O(n) average with quickselect", "space": "O(k)"},
        "hints": [
            "Sorting works in O(n log n). Can you avoid ordering elements you do not care about?",
            "You only need to remember the k largest values seen so far. Which structure lets you evict the smallest of them fast?",
            "Keep a min-heap of size k; push each value and pop when size exceeds k. The heap top is the answer.",
        ],
    },
    {
        "id": "trapping-rain-water",
        "title": "Trapping Rain Water",
        "difficulty": "Hard",
        "pattern": "Two pointers",
        "statement": "Given `n` non-negative integers `height` representing an elevation map where each bar has width 1, return how many units of water it can trap after raining.",
        "constraints": ["1 <= n <= 2 * 10^4", "0 <= height[i] <= 10^5"],
        "function": {"name": "trap", "params": [["height", "int[]"]], "returns": "int"},
        "examples": [
            {"args": [[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]], "explanation": "6 units are trapped."},
            {"args": [[4, 2, 0, 3, 2, 5]], "explanation": "9 units are trapped."},
        ],
        "edge_cases": [[[1]], [[3, 0]], [[2, 0, 2]], [[5, 4, 3, 2, 1]], [[0, 0, 0]]],
        "generator": gen_trap,
        "reference": trap,
        "complexity": {"time": "O(n)", "space": "O(1)"},
        "hints": [
            "How much water sits above a single bar i? It depends on two other heights.",
            "water[i] = min(maxLeft[i], maxRight[i]) - height[i]. Precomputing both arrays gives O(n) time and O(n) space.",
            "Two pointers: move the side with the smaller height inward, tracking that side's max; the smaller side's max bounds its water.",
        ],
    },
    {
        "id": "edit-distance",
        "title": "Edit Distance",
        "difficulty": "Hard",
        "pattern": "2D dynamic programming",
        "statement": "Given two strings `word1` and `word2`, return the minimum number of single-character insertions, deletions or substitutions needed to turn `word1` into `word2`.",
        "constraints": ["0 <= word1.length, word2.length <= 500", "Both strings use lowercase English letters"],
        "function": {"name": "minDistance", "params": [["word1", "string"], ["word2", "string"]], "returns": "int"},
        "examples": [
            {"args": ["horse", "ros"], "explanation": "horse -> rorse -> rose -> ros."},
            {"args": ["intention", "execution"], "explanation": "5 operations."},
        ],
        "edge_cases": [["", ""], ["", "abc"], ["abc", ""], ["same", "same"], ["a", "b"]],
        "generator": gen_edit,
        "reference": min_distance,
        "complexity": {"time": "O(m * n)", "space": "O(min(m, n)) with a rolling row"},
        "hints": [
            "Think about the last characters of both strings. What are your options if they match? If they do not?",
            "Define dp[i][j] = edits to turn the first i chars of word1 into the first j chars of word2. What are the base cases?",
            "dp[i][j] = dp[i-1][j-1] if chars match, else 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]). Base: dp[i][0] = i, dp[0][j] = j.",
        ],
    },
]

from specs_easy import EASY  # noqa: E402
from specs_medium import MEDIUM  # noqa: E402
from specs_hard import HARD  # noqa: E402

SPECS += EASY + MEDIUM + HARD

RANDOM_TESTS_PER_PROBLEM = 6
GeneratorFn = Callable[[random.Random], list[Any]]
