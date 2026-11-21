"""Hard problems. Reference functions are self-contained (imports inside the body)."""

from __future__ import annotations

from specs_easy import P


# --------------------------------------------------------------------------- references

def min_window(s, t):
    need = {}
    for c in t:
        need[c] = need.get(c, 0) + 1
    missing = len(t)
    left = 0
    best = (float("inf"), 0, 0)
    for right, c in enumerate(s):
        if need.get(c, 0) > 0:
            missing -= 1
        need[c] = need.get(c, 0) - 1
        while missing == 0:
            if right - left + 1 < best[0]:
                best = (right - left + 1, left, right + 1)
            lc = s[left]
            need[lc] += 1
            if need[lc] > 0:
                missing += 1
            left += 1
    return "" if best[0] == float("inf") else s[best[1]:best[2]]


def max_sliding_window(nums, k):
    from collections import deque
    dq = deque()
    out = []
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out


def largest_rectangle_area(heights):
    stack = []
    best = 0
    for i, h in enumerate(heights + [0]):
        start = i
        while stack and stack[-1][1] >= h:
            j, hh = stack.pop()
            best = max(best, hh * (i - j))
            start = j
        stack.append((start, h))
    return best


def longest_valid_parentheses(s):
    stack = [-1]
    best = 0
    for i, c in enumerate(s):
        if c == "(":
            stack.append(i)
        else:
            stack.pop()
            if not stack:
                stack.append(i)
            else:
                best = max(best, i - stack[-1])
    return best


def total_n_queens(n):
    count = 0
    cols, d1, d2 = set(), set(), set()

    def place(r):
        nonlocal count
        if r == n:
            count += 1
            return
        for c in range(n):
            if c in cols or r - c in d1 or r + c in d2:
                continue
            cols.add(c); d1.add(r - c); d2.add(r + c)
            place(r + 1)
            cols.discard(c); d1.discard(r - c); d2.discard(r + c)

    place(0)
    return count


def is_match(s, p):
    m, n = len(s), len(p)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True
    for j in range(2, n + 1):
        if p[j - 1] == "*":
            dp[0][j] = dp[0][j - 2]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if p[j - 1] == "*":
                dp[i][j] = dp[i][j - 2] or (p[j - 2] in (s[i - 1], ".") and dp[i - 1][j])
            else:
                dp[i][j] = p[j - 1] in (s[i - 1], ".") and dp[i - 1][j - 1]
    return dp[m][n]


def first_missing_positive(nums):
    a = list(nums)
    n = len(a)
    for i in range(n):
        while 1 <= a[i] <= n and a[a[i] - 1] != a[i]:
            j = a[i] - 1
            a[i], a[j] = a[j], a[i]
    for i in range(n):
        if a[i] != i + 1:
            return i + 1
    return n + 1


def ladder_length(beginWord, endWord, wordList):
    from collections import deque
    words = set(wordList)
    if endWord not in words:
        return 0
    q = deque([(beginWord, 1)])
    seen = {beginWord}
    while q:
        w, d = q.popleft()
        if w == endWord:
            return d
        for i in range(len(w)):
            for ch in "abcdefghijklmnopqrstuvwxyz":
                nxt = w[:i] + ch + w[i + 1:]
                if nxt in words and nxt not in seen:
                    seen.add(nxt)
                    q.append((nxt, d + 1))
    return 0


# --------------------------------------------------------------------------- generators

def gen_min_window(rng):
    a = rng.choice(["ab", "abc", "abcd"])
    s = "".join(rng.choice(a) for _ in range(rng.randint(1, 14)))
    t = "".join(rng.choice(a) for _ in range(rng.randint(1, 4)))
    return [s, t]


def gen_sliding_max(rng):
    nums = [rng.randint(-10, 10) for _ in range(rng.randint(1, 16))]
    return [nums, rng.randint(1, len(nums))]


def gen_histogram(rng):
    return [[rng.randint(0, 8) for _ in range(rng.randint(1, 16))]]


def gen_valid_paren_len(rng):
    return ["".join(rng.choice("()") for _ in range(rng.randint(0, 18)))]


def gen_queens(rng):
    return [rng.randint(1, 9)]


def gen_regex(rng):
    s = "".join(rng.choice("ab") for _ in range(rng.randint(0, 6)))
    p = ""
    for _ in range(rng.randint(0, 5)):
        p += rng.choice("ab.")
        if rng.random() < 0.4:
            p += "*"
    return [s, p]


def gen_first_missing(rng):
    return [[rng.randint(-3, 10) for _ in range(rng.randint(1, 12))]]


def gen_ladder(rng):
    pool = ["hot", "dot", "dog", "lot", "log", "cog", "hit", "hog", "cot", "lit", "dit", "hat", "cat", "cog", "dig"]
    words = sorted(set(rng.sample(pool, rng.randint(2, 10))))
    begin = rng.choice(["hit", "hot", "cat", "dig"])
    end = rng.choice(words) if rng.random() < 0.8 else "zzz"
    if end == begin:
        end = words[0] if words[0] != begin else "zzz"
    return [begin, end, words]


# --------------------------------------------------------------------------- specs

HARD = [
    P("minimum-window-substring", "Minimum Window Substring", "Hard", "Sliding window",
      "Given strings `s` and `t`, return the shortest substring of `s` that contains every character of `t` (with multiplicity). If several are equally short, return the leftmost. Return an empty string if none exists.",
      ["1 <= s.length, t.length <= 10^5", "English letters"], "minWindow", [["s", "string"], ["t", "string"]], "string",
      [(["ADOBECODEBANC", "ABC"], "\"BANC\"."), (["a", "a"], "\"a\"."), (["a", "aa"], "s has only one 'a'.")],
      [["ab", "b"], ["abc", "d"], ["aa", "aa"], ["bba", "ab"], ["cabwefgewcwaefgcf", "cae"]], gen_min_window, min_window, "O(|s| + |t|)", "O(alphabet)",
      ["Checking every substring is far too slow. Can you reuse one window as it slides?",
       "Expand the right edge until the window covers t, then shrink the left edge while it still covers t.",
       "Keep a count of needed characters and a 'missing' total; update the best window each time missing hits 0 while shrinking."]),
    P("sliding-window-maximum", "Sliding Window Maximum", "Hard", "Monotonic deque",
      "Given an integer array `nums` and a window size `k`, return the maximum of each window of size `k` as it slides from left to right.",
      ["1 <= k <= nums.length <= 10^5", "-10^4 <= nums[i] <= 10^4"], "maxSlidingWindow", [["nums", "int[]"], ["k", "int"]], "int[]",
      [([[1, 3, -1, -3, 5, 3, 6, 7], 3], "[3,3,5,5,6,7]."), ([[1], 1], "[1].")],
      [[[9, 8, 7, 6], 2], [[1, 2, 3, 4], 2], [[4, 4, 4], 3], [[-1, -2], 1]], gen_sliding_max, max_sliding_window, "O(n)", "O(k)",
      ["A heap gives O(n log n). Which elements can never be a future maximum?",
       "Once a larger element arrives, smaller elements before it are useless.",
       "Keep a deque of indices with decreasing values: pop smaller values from the back, drop the front when it leaves the window, and read the max from the front."]),
    P("largest-rectangle-in-histogram", "Largest Rectangle in Histogram", "Hard", "Monotonic stack",
      "Given `heights` of histogram bars (each of width 1), return the area of the largest rectangle that fits inside the histogram.",
      ["1 <= heights.length <= 10^5", "0 <= heights[i] <= 10^4"], "largestRectangleArea", [["heights", "int[]"]], "int",
      [([[2, 1, 5, 6, 2, 3]], "Bars 5 and 6 give 10."), ([[2, 4]], "4.")],
      [[[0]], [[5]], [[1, 1, 1, 1]], [[6, 2, 5, 4, 5, 1, 6]], [[3, 2, 1]]], gen_histogram, largest_rectangle_area, "O(n)", "O(n)",
      ["For each bar, the best rectangle at its height extends to the nearest shorter bar on each side.",
       "A stack of increasing heights tells you exactly when a bar's right boundary is found.",
       "When a shorter bar arrives, pop taller bars and compute height * width using the index where each popped bar started."]),
    P("longest-valid-parentheses", "Longest Valid Parentheses", "Hard", "Stack",
      "Given a string `s` of `(` and `)`, return the length of its longest well-formed parentheses substring.",
      ["0 <= s.length <= 3 * 10^4"], "longestValidParentheses", [["s", "string"]], "int",
      [(["(()"], "\"()\"."), ([")()())"], "\"()()\"."), ([""], "0.")],
      [["("], ["()"], ["()(()"], ["(()())"], ["))(("]], gen_valid_paren_len, longest_valid_parentheses, "O(n)", "O(n)",
      ["Brute force checks every substring. What makes a valid run end?",
       "Push indices on a stack and keep the index of the last unmatched ')' as a base.",
       "Start the stack with -1. On '(' push i; on ')' pop, then push i if the stack is empty, else best = max(best, i - top)."]),
    P("n-queens-ii", "N-Queens II", "Hard", "Backtracking",
      "Return the number of ways to place `n` queens on an `n x n` chessboard so that no two queens attack each other.",
      ["1 <= n <= 9"], "totalNQueens", [["n", "int"]], "int",
      [([4], "2 solutions."), ([1], "1 solution.")],
      [[2], [3], [8]], gen_queens, total_n_queens, "O(n!)", "O(n)",
      ["Each row holds exactly one queen, so place them row by row.",
       "A placement is attacked through its column or one of its two diagonals. How can you check that in O(1)?",
       "Backtrack with sets (or bitmasks) for columns, r - c diagonals and r + c diagonals."]),
    P("regular-expression-matching", "Regular Expression Matching", "Hard", "2D dynamic programming",
      "Implement matching of the whole string `s` against pattern `p`, where `.` matches any single character and `*` matches zero or more of the element before it.",
      ["0 <= s.length <= 20", "0 <= p.length <= 20", "Every '*' follows a valid character"], "isMatch", [["s", "string"], ["p", "string"]], "bool",
      [(["aa", "a"], "The pattern is too short."), (["aa", "a*"], "a* covers both."), (["ab", ".*"], ".* matches anything.")],
      [["", ""], ["", "a*"], ["", "."], ["aab", "c*a*b"], ["mississippi", "mis*is*p*."]], gen_regex, is_match, "O(m * n)", "O(m * n)",
      ["The hard part is '*'. It can match zero copies or one more copy.",
       "Let dp[i][j] mean s[:i] matches p[:j]. What are the cases when p[j-1] == '*'?",
       "For '*': dp[i][j] = dp[i][j-2] (zero copies) or (p[j-2] matches s[i-1] and dp[i-1][j]). Otherwise compare one character."]),
    P("first-missing-positive", "First Missing Positive", "Hard", "In-place hashing",
      "Given an unsorted integer array `nums`, return the smallest positive integer that does not appear in it, in O(n) time with O(1) extra space.",
      ["1 <= nums.length <= 10^5", "-2^31 <= nums[i] <= 2^31 - 1"], "firstMissingPositive", [["nums", "int[]"]], "int",
      [([[1, 2, 0]], "3."), ([[3, 4, -1, 1]], "2."), ([[7, 8, 9, 11, 12]], "1.")],
      [[[1]], [[2]], [[1, 1]], [[-5, -1]], [[2, 1]]], gen_first_missing, first_missing_positive, "O(n)", "O(1)",
      ["The answer is always in 1..n+1. Why?",
       "Use the array itself as the hash table: value v belongs at index v-1.",
       "Cyclically swap each value in [1, n] into its home slot, then return the first index i with nums[i] != i+1 (or n+1)."]),
    P("word-ladder", "Word Ladder", "Hard", "BFS on implicit graph",
      "Given `beginWord`, `endWord` and a `wordList`, return the number of words in the shortest transformation sequence from `beginWord` to `endWord`, changing one letter at a time, with every intermediate word in `wordList`. Return `0` if no sequence exists.",
      ["1 <= word length <= 10", "1 <= wordList.length <= 5000", "beginWord need not be in wordList"], "ladderLength", [["beginWord", "string"], ["endWord", "string"], ["wordList", "string[]"]], "int",
      [(["hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]], "hit -> hot -> dot -> dog -> cog: 5 words."), (["hit", "cog", ["hot", "dot", "dog", "lot", "log"]], "cog is not in the list.")],
      [["a", "c", ["a", "b", "c"]], ["hot", "dog", ["hot", "dog"]], ["hot", "dot", ["dot"]], ["hot", "hog", ["hog", "dog"]]], gen_ladder, ladder_length, "O(N * L * 26)", "O(N * L)",
      ["Shortest number of steps in an unweighted graph suggests which algorithm?",
       "Words are nodes; an edge joins two words that differ in exactly one letter. You do not need to build every edge up front.",
       "BFS from beginWord; for each word try all 26 letters at each position, visiting neighbours that are in the word set."]),
]
