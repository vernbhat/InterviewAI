"""Medium problems. Reference functions are self-contained (imports inside the body)."""

from __future__ import annotations

from specs_easy import P


# --------------------------------------------------------------------------- references

def max_subarray(nums):
    best = cur = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best


def three_sum(nums):
    a = sorted(nums)
    n = len(a)
    out = []
    for i in range(n):
        if i and a[i] == a[i - 1]:
            continue
        l, r = i + 1, n - 1
        while l < r:
            s = a[i] + a[l] + a[r]
            if s < 0:
                l += 1
            elif s > 0:
                r -= 1
            else:
                out.append([a[i], a[l], a[r]])
                l += 1
                while l < r and a[l] == a[l - 1]:
                    l += 1
                r -= 1
    return out


def max_area(height):
    l, r, best = 0, len(height) - 1, 0
    while l < r:
        best = max(best, (r - l) * min(height[l], height[r]))
        if height[l] < height[r]:
            l += 1
        else:
            r -= 1
    return best


def top_k_frequent(nums, k):
    counts = {}
    for x in nums:
        counts[x] = counts.get(x, 0) + 1
    order = sorted(counts, key=lambda v: (-counts[v], v))
    return order[:k]


def longest_consecutive(nums):
    s = set(nums)
    best = 0
    for x in s:
        if x - 1 not in s:
            y = x
            while y + 1 in s:
                y += 1
            best = max(best, y - x + 1)
    return best


def search_rotated(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1


def find_min_rotated(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        else:
            hi = mid
    return nums[lo]


def rob(nums):
    take, skip = 0, 0
    for x in nums:
        take, skip = skip + x, max(take, skip)
    return max(take, skip)


def length_of_lis(nums):
    import bisect
    tails = []
    for x in nums:
        i = bisect.bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)


def unique_paths(m, n):
    row = [1] * n
    for _ in range(1, m):
        for j in range(1, n):
            row[j] += row[j - 1]
    return row[-1]


def can_jump(nums):
    reach = 0
    for i, x in enumerate(nums):
        if i > reach:
            return False
        reach = max(reach, i + x)
    return True


def num_decodings(s):
    prev2, prev1 = 1, 1 if s and s[0] != "0" else 0
    if not s:
        return 0
    for i in range(1, len(s)):
        cur = 0
        if s[i] != "0":
            cur += prev1
        if 10 <= int(s[i - 1:i + 1]) <= 26:
            cur += prev2
        prev2, prev1 = prev1, cur
    return prev1


def word_break(s, wordDict):
    words = set(wordDict)
    ok = [True] + [False] * len(s)
    for i in range(1, len(s) + 1):
        for j in range(i):
            if ok[j] and s[j:i] in words:
                ok[i] = True
                break
    return ok[len(s)]


def count_substrings(s):
    n, total = len(s), 0
    for center in range(2 * n - 1):
        l, r = center // 2, center // 2 + center % 2
        while l >= 0 and r < n and s[l] == s[r]:
            total += 1
            l -= 1
            r += 1
    return total


def longest_common_subsequence(text1, text2):
    m, n = len(text1), len(text2)
    prev = [0] * (n + 1)
    for i in range(1, m + 1):
        cur = [0] * (n + 1)
        for j in range(1, n + 1):
            cur[j] = prev[j - 1] + 1 if text1[i - 1] == text2[j - 1] else max(prev[j], cur[j - 1])
        prev = cur
    return prev[n]


def daily_temperatures(temperatures):
    out = [0] * len(temperatures)
    stack = []
    for i, t in enumerate(temperatures):
        while stack and temperatures[stack[-1]] < t:
            j = stack.pop()
            out[j] = i - j
        stack.append(i)
    return out


def eval_rpn(tokens):
    st = []
    for tok in tokens:
        if tok in ("+", "-", "*", "/"):
            b, a = st.pop(), st.pop()
            if tok == "+":
                st.append(a + b)
            elif tok == "-":
                st.append(a - b)
            elif tok == "*":
                st.append(a * b)
            else:
                q = abs(a) // abs(b)
                st.append(q if (a >= 0) == (b >= 0) else -q)
        else:
            st.append(int(tok))
    return st[-1]


def subarray_sum(nums, k):
    seen = {0: 1}
    s = total = 0
    for x in nums:
        s += x
        total += seen.get(s - k, 0)
        seen[s] = seen.get(s, 0) + 1
    return total


def oranges_rotting(grid):
    from collections import deque
    rows, cols = len(grid), len(grid[0])
    g = [row[:] for row in grid]
    q = deque((r, c) for r in range(rows) for c in range(cols) if g[r][c] == 2)
    fresh = sum(row.count(1) for row in g)
    minutes = 0
    while q and fresh:
        for _ in range(len(q)):
            r, c = q.popleft()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and g[nr][nc] == 1:
                    g[nr][nc] = 2
                    fresh -= 1
                    q.append((nr, nc))
        minutes += 1
    return -1 if fresh else minutes


def can_finish(numCourses, prerequisites):
    indeg = [0] * numCourses
    adj = [[] for _ in range(numCourses)]
    for a, b in prerequisites:
        adj[b].append(a)
        indeg[a] += 1
    stack = [i for i in range(numCourses) if indeg[i] == 0]
    done = 0
    while stack:
        u = stack.pop()
        done += 1
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                stack.append(v)
    return done == numCourses


def spiral_order(matrix):
    out = []
    top, bottom, left, right = 0, len(matrix) - 1, 0, len(matrix[0]) - 1
    while top <= bottom and left <= right:
        for j in range(left, right + 1):
            out.append(matrix[top][j])
        for i in range(top + 1, bottom + 1):
            out.append(matrix[i][right])
        if top < bottom and left < right:
            for j in range(right - 1, left - 1, -1):
                out.append(matrix[bottom][j])
            for i in range(bottom - 1, top, -1):
                out.append(matrix[i][left])
        top, bottom, left, right = top + 1, bottom - 1, left + 1, right - 1
    return out


def rotate_image(matrix):
    n = len(matrix)
    return [[matrix[n - 1 - j][i] for j in range(n)] for i in range(n)]


def min_eating_speed(piles, h):
    lo, hi = 1, max(piles)
    while lo < hi:
        mid = (lo + hi) // 2
        if sum((p + mid - 1) // mid for p in piles) <= h:
            hi = mid
        else:
            lo = mid + 1
    return lo


def character_replacement(s, k):
    counts = {}
    left = best = top = 0
    for right, ch in enumerate(s):
        counts[ch] = counts.get(ch, 0) + 1
        top = max(top, counts[ch])
        while right - left + 1 - top > k:
            counts[s[left]] -= 1
            left += 1
        best = max(best, right - left + 1)
    return best


def generate_parenthesis(n):
    out = []

    def go(cur, opened, closed):
        if len(cur) == 2 * n:
            out.append(cur)
            return
        if opened < n:
            go(cur + "(", opened + 1, closed)
        if closed < opened:
            go(cur + ")", opened, closed + 1)

    go("", 0, 0)
    return out


def erase_overlap_intervals(intervals):
    end = None
    removed = 0
    for a, b in sorted(intervals, key=lambda iv: iv[1]):
        if end is not None and a < end:
            removed += 1
        else:
            end = b
    return removed


# --------------------------------------------------------------------------- generators

def _ints(rng, lo, hi, nlo, nhi):
    return [rng.randint(lo, hi) for _ in range(rng.randint(nlo, nhi))]


def gen_max_sub(rng):
    return [_ints(rng, -10, 10, 1, 20)]


def gen_3sum(rng):
    return [_ints(rng, -6, 6, 0, 14)]


def gen_area(rng):
    return [_ints(rng, 0, 12, 2, 20)]


def gen_topk(rng):
    nums = _ints(rng, -5, 5, 1, 20)
    return [nums, rng.randint(1, len(set(nums)))]


def gen_consec(rng):
    return [_ints(rng, -15, 15, 0, 18)]


def gen_rotated(rng):
    nums = sorted(rng.sample(range(-50, 50), rng.randint(1, 15)))
    k = rng.randrange(len(nums))
    nums = nums[k:] + nums[:k]
    target = rng.choice(nums) if rng.random() < 0.6 else rng.randint(-55, 55)
    return [nums, target]


def gen_rotated_min(rng):
    return [gen_rotated(rng)[0]]


def gen_rob(rng):
    return [_ints(rng, 0, 40, 1, 15)]


def gen_lis(rng):
    return [_ints(rng, -10, 10, 1, 18)]


def gen_paths(rng):
    return [rng.randint(1, 12), rng.randint(1, 12)]


def gen_jump(rng):
    return [[rng.choice([0, 0, 1, 1, 2, 3]) for _ in range(rng.randint(1, 12))]]


def gen_decode(rng):
    return ["".join(rng.choice("0112223456789") for _ in range(rng.randint(1, 12)))]


def gen_wordbreak(rng):
    words = list({"".join(rng.choice("ab") for _ in range(rng.randint(1, 3))) for _ in range(rng.randint(1, 5))})
    if rng.random() < 0.5:
        s = "".join(rng.choice(words) for _ in range(rng.randint(1, 5)))
    else:
        s = "".join(rng.choice("ab") for _ in range(rng.randint(1, 10)))
    return [s, sorted(words)]


def gen_pal_count(rng):
    return ["".join(rng.choice(rng.choice(["ab", "abc", "aab"])) for _ in range(rng.randint(1, 14)))]


def gen_lcs(rng):
    a = rng.choice(["ab", "abc", "abcdef"])
    return ["".join(rng.choice(a) for _ in range(rng.randint(1, 10))), "".join(rng.choice(a) for _ in range(rng.randint(1, 10)))]


def gen_temps(rng):
    return [_ints(rng, 30, 45, 1, 18)]


def gen_rpn(rng):
    while True:
        tokens = _rpn_tokens(rng)
        try:
            eval_rpn(tokens)
            return [tokens]
        except ZeroDivisionError:
            continue


def _rpn_tokens(rng):
    tokens = [str(rng.randint(-9, 9))]
    depth = 1
    for _ in range(rng.randint(0, 6)):
        tokens.append(str(rng.randint(-9, 9)))
        depth += 1
        while depth > 1 and rng.random() < 0.6:
            op = rng.choice("+-*/")
            if op == "/" and tokens[-1] in ("0", "-0"):
                op = "+"
            tokens.append(op)
            depth -= 1
    while depth > 1:
        tokens.append(rng.choice("+-*"))
        depth -= 1
    return tokens


def gen_subsum(rng):
    return [_ints(rng, -3, 4, 1, 16), rng.randint(-3, 8)]


def gen_oranges(rng):
    rows, cols = rng.randint(1, 5), rng.randint(1, 5)
    return [[[rng.choice([0, 1, 1, 1, 2]) for _ in range(cols)] for _ in range(rows)]]


def gen_courses(rng):
    n = rng.randint(1, 7)
    edges = set()
    for _ in range(rng.randint(0, 8)):
        a, b = rng.randrange(n), rng.randrange(n)
        if a != b:
            edges.add((a, b))
    return [n, [list(e) for e in sorted(edges)]]


def gen_spiral(rng):
    r, c = rng.randint(1, 5), rng.randint(1, 5)
    return [[[rng.randint(-9, 9) for _ in range(c)] for _ in range(r)]]


def gen_rotate(rng):
    n = rng.randint(1, 5)
    return [[[rng.randint(-9, 9) for _ in range(n)] for _ in range(n)]]


def gen_koko(rng):
    piles = _ints(rng, 1, 40, 1, 8)
    return [piles, rng.randint(len(piles), len(piles) * 4)]


def gen_replace(rng):
    return ["".join(rng.choice(rng.choice(["AB", "ABC"])) for _ in range(rng.randint(1, 15))), rng.randint(0, 3)]


def gen_genparen(rng):
    return [rng.randint(1, 8)]


def gen_overlap(rng):
    out = []
    for _ in range(rng.randint(1, 8)):
        a = rng.randint(-10, 20)
        out.append([a, a + rng.randint(1, 6)])
    return [out]


# --------------------------------------------------------------------------- specs

MEDIUM = [
    P("maximum-subarray", "Maximum Subarray", "Medium", "Kadane's algorithm",
      "Given an integer array `nums`, return the largest sum of any non-empty contiguous subarray.",
      ["1 <= nums.length <= 10^5", "-10^4 <= nums[i] <= 10^4"], "maxSubArray", [["nums", "int[]"]], "int",
      [([[-2, 1, -3, 4, -1, 2, 1, -5, 4]], "[4,-1,2,1] sums to 6."), ([[1]], "Single element."), ([[5, 4, -1, 7, 8]], "The whole array, 23.")],
      [[[-3]], [[-2, -1]], [[0, 0]], [[-1, 3, -1]]], gen_max_sub, max_subarray, "O(n)", "O(1)",
      ["Checking every subarray is O(n^2). What is the best subarray that ends at index i?",
       "best_ending_at(i) = max(nums[i], best_ending_at(i-1) + nums[i]).",
       "Kadane: track the current running sum (reset when it would be worse than starting fresh) and the best seen. Watch all-negative input."]),
    P("3sum", "3Sum", "Medium", "Sorting, two pointers",
      "Given an integer array `nums`, return all unique triplets `[a, b, c]` with `a + b + c = 0`. Each triplet must be sorted ascending, and the list of triplets must be sorted lexicographically.",
      ["0 <= nums.length <= 3000", "-10^5 <= nums[i] <= 10^5"], "threeSum", [["nums", "int[]"]], "int[][]",
      [([[-1, 0, 1, 2, -1, -4]], "[[-1,-1,2],[-1,0,1]]."), ([[0, 1, 1]], "No triplet sums to 0."), ([[0, 0, 0]], "One triplet.")],
      [[[]], [[0, 0]], [[0, 0, 0, 0]], [[-2, 0, 1, 1, 2]], [[3, -2, 1, 0]]], gen_3sum, three_sum, "O(n^2)", "O(1) extra (sorting aside)",
      ["Triple loops are O(n^3) and create duplicates. Would sorting help?",
       "Fix the first element, then the problem becomes Two Sum on the sorted remainder.",
       "Sort; for each i (skipping repeated values) run two pointers l, r; on a hit, record and skip duplicates of l."]),
    P("container-with-most-water", "Container With Most Water", "Medium", "Two pointers",
      "Given `height[i]`, the heights of vertical lines at positions `i`, pick two lines that, with the x-axis, hold the most water. Return that maximum area.",
      ["2 <= n <= 10^5", "0 <= height[i] <= 10^4"], "maxArea", [["height", "int[]"]], "int",
      [([[1, 8, 6, 2, 5, 4, 8, 3, 7]], "Lines at 1 and 8: 7 * 7 = 49."), ([[1, 1]], "Area 1.")],
      [[[0, 0]], [[5, 0, 5]], [[1, 2, 4, 3]], [[10, 1, 1, 1, 10]]], gen_area, max_area, "O(n)", "O(1)",
      ["Area = width * min(left, right). Checking all pairs is O(n^2).",
       "Start with the widest pair. Which pointer could possibly lead to a bigger area if you move it?",
       "Two pointers from both ends; always move the shorter line inward, since the taller one can never do better with it."]),
    P("top-k-frequent-elements", "Top K Frequent Elements", "Medium", "Hash map, bucket sort",
      "Given an integer array `nums` and an integer `k`, return the `k` most frequent values, ordered by frequency (highest first) and breaking ties by smaller value first.",
      ["1 <= nums.length <= 10^5", "1 <= k <= number of distinct values"], "topKFrequent", [["nums", "int[]"], ["k", "int"]], "int[]",
      [([[1, 1, 1, 2, 2, 3], 2], "1 appears 3 times, 2 appears twice."), ([[1], 1], "Only one value.")],
      [[[4, 4, 5, 5, 6], 2], [[-1, -1, 2], 2], [[3, 2, 1], 3], [[7, 7, 7], 1]], gen_topk, top_k_frequent, "O(n log n), or O(n) with buckets", "O(n)",
      ["First count how often each value occurs.",
       "Now you need the k largest counts. Sorting works; a size-k heap or frequency buckets are faster.",
       "Count with a hash map, then sort unique values by (-count, value) and take the first k."]),
    P("longest-consecutive-sequence", "Longest Consecutive Sequence", "Medium", "Hash set",
      "Given an unsorted integer array `nums`, return the length of the longest run of consecutive integers (such as 1, 2, 3, 4) that can be formed from its values. Aim for O(n).",
      ["0 <= nums.length <= 10^5", "-10^9 <= nums[i] <= 10^9"], "longestConsecutive", [["nums", "int[]"]], "int",
      [([[100, 4, 200, 1, 3, 2]], "1, 2, 3, 4."), ([[0, 3, 7, 2, 5, 8, 4, 6, 0, 1]], "0 through 8.")],
      [[[]], [[5]], [[1, 1, 1]], [[-1, 0, 1]], [[10, 30, 20]]], gen_consec, longest_consecutive, "O(n)", "O(n)",
      ["Sorting gives O(n log n). Can a hash set give O(n)?",
       "Only start counting from a number x when x - 1 is not in the set.",
       "Put every value in a set; for each sequence start, walk x+1, x+2, ... and track the longest run."]),
    P("search-in-rotated-sorted-array", "Search in Rotated Sorted Array", "Medium", "Binary search",
      "A sorted array of distinct integers was rotated at an unknown pivot (for example `[0,1,2,4,5,6,7]` became `[4,5,6,7,0,1,2]`). Return the index of `target` in `nums`, or `-1`, in O(log n).",
      ["1 <= nums.length <= 5000", "Values are distinct"], "search", [["nums", "int[]"], ["target", "int"]], "int",
      [([[4, 5, 6, 7, 0, 1, 2], 0], "0 is at index 4."), ([[4, 5, 6, 7, 0, 1, 2], 3], "3 is absent."), ([[1], 0], "Absent.")],
      [[[1], 1], [[3, 1], 1], [[5, 1, 3], 5], [[1, 3], 3]], gen_rotated, search_rotated, "O(log n)", "O(1)",
      ["After picking mid, at least one half [lo, mid] or [mid, hi] is sorted. How can you tell which?",
       "If target lies inside the sorted half's range, search there; otherwise search the other half.",
       "If nums[lo] <= nums[mid], the left half is sorted: go left when nums[lo] <= target < nums[mid]. Otherwise mirror that on the right."]),
    P("find-minimum-in-rotated-sorted-array", "Find Minimum in Rotated Sorted Array", "Medium", "Binary search",
      "Given a sorted array of distinct integers that has been rotated an unknown number of times, return its minimum element in O(log n).",
      ["1 <= nums.length <= 5000", "Values are distinct"], "findMin", [["nums", "int[]"]], "int",
      [([[3, 4, 5, 1, 2]], "Minimum 1."), ([[4, 5, 6, 7, 0, 1, 2]], "Minimum 0."), ([[11, 13, 15, 17]], "Not rotated.")],
      [[[1]], [[2, 1]], [[1, 2]], [[-5, -3, -10]]], gen_rotated_min, find_min_rotated, "O(log n)", "O(1)",
      ["Compare nums[mid] with nums[hi]. What does it tell you about where the drop is?",
       "If nums[mid] > nums[hi], the minimum is strictly to the right of mid.",
       "lo = mid + 1 when nums[mid] > nums[hi], else hi = mid; loop while lo < hi and return nums[lo]."]),
    P("house-robber", "House Robber", "Medium", "1D dynamic programming",
      "`nums[i]` is the money in house `i` along a street. You cannot rob two adjacent houses. Return the maximum amount you can rob.",
      ["1 <= nums.length <= 100", "0 <= nums[i] <= 400"], "rob", [["nums", "int[]"]], "int",
      [([[1, 2, 3, 1]], "Rob houses 0 and 2: 4."), ([[2, 7, 9, 3, 1]], "Rob 2 + 9 + 1 = 12.")],
      [[[5]], [[1, 9]], [[0, 0, 0]], [[2, 1, 1, 2]]], gen_rob, rob, "O(n)", "O(1)",
      ["Greedy (always take the biggest) fails. Think about house i: rob it or skip it.",
       "best(i) = max(best(i-1), best(i-2) + nums[i]).",
       "Iterate keeping two values: the best with house i robbed and the best with it skipped."]),
    P("longest-increasing-subsequence", "Longest Increasing Subsequence", "Medium", "DP + binary search",
      "Given an integer array `nums`, return the length of the longest strictly increasing subsequence.",
      ["1 <= nums.length <= 2500", "-10^4 <= nums[i] <= 10^4"], "lengthOfLIS", [["nums", "int[]"]], "int",
      [([[10, 9, 2, 5, 3, 7, 101, 18]], "[2,3,7,101], length 4."), ([[0, 1, 0, 3, 2, 3]], "Length 4."), ([[7, 7, 7, 7]], "Strictly increasing, so 1.")],
      [[[1]], [[2, 1]], [[1, 2]], [[4, 10, 4, 3, 8, 9]]], gen_lis, length_of_lis, "O(n log n)", "O(n)",
      ["O(n^2) DP: lis[i] = 1 + max(lis[j]) over j < i with nums[j] < nums[i].",
       "For the O(n log n) version, keep the smallest possible tail for each subsequence length.",
       "Maintain a sorted 'tails' array; binary-search the first tail >= x and replace it (or append). Its length is the answer."]),
    P("unique-paths", "Unique Paths", "Medium", "Grid DP",
      "A robot starts at the top-left of an `m x n` grid and can only move right or down. Return the number of distinct paths to the bottom-right corner.",
      ["1 <= m, n <= 100", "The answer fits in a 32-bit signed integer for the tested sizes"], "uniquePaths", [["m", "int"], ["n", "int"]], "int",
      [([3, 7], "28 paths."), ([3, 2], "3 paths.")],
      [[1, 1], [1, 10], [10, 1], [10, 10]], gen_paths, unique_paths, "O(m * n)", "O(n)",
      ["How many ways reach a cell? It depends on two neighbours.",
       "paths(r, c) = paths(r-1, c) + paths(r, c-1), with the first row and column all 1.",
       "Use a single row array updated in place: row[j] += row[j-1]. (Combinatorics: C(m+n-2, m-1).)"]),
    P("jump-game", "Jump Game", "Medium", "Greedy",
      "You start at index 0 of `nums`; `nums[i]` is the maximum jump length from index `i`. Return `true` if you can reach the last index.",
      ["1 <= nums.length <= 10^4", "0 <= nums[i] <= 10^5"], "canJump", [["nums", "int[]"]], "bool",
      [([[2, 3, 1, 1, 4]], "0 -> 1 -> 4."), ([[3, 2, 1, 0, 4]], "Every path gets stuck at index 3.")],
      [[[0]], [[0, 1]], [[1, 0]], [[2, 0, 0]], [[1, 1, 0, 1]]], gen_jump, can_jump, "O(n)", "O(1)",
      ["Do you need to know the exact path, or only how far you can get?",
       "Track the furthest index reachable so far. When do you get stuck?",
       "Scan left to right; if i > reach return false; otherwise reach = max(reach, i + nums[i])."]),
    P("decode-ways", "Decode Ways", "Medium", "1D dynamic programming",
      "Letters A-Z are encoded as `\"1\"` to `\"26\"`. Given a digit string `s`, return how many ways it can be decoded. `\"06\"` is not a valid code for F.",
      ["1 <= s.length <= 100", "s contains only digits"], "numDecodings", [["s", "string"]], "int",
      [(["12"], "\"AB\" or \"L\"."), (["226"], "BZ, VF, BBF."), (["06"], "Leading zero, so 0.")],
      [["0"], ["10"], ["100"], ["27"], ["1111"]], gen_decode, num_decodings, "O(n)", "O(1)",
      ["How does the last one digit, or the last two digits, extend the earlier decodings?",
       "ways(i) = ways(i-1) if s[i] != '0', plus ways(i-2) if s[i-1..i] is between 10 and 26.",
       "Roll two variables through the string. Zeros are the trap: a '0' can only be the second digit of 10 or 20."]),
    P("word-break", "Word Break", "Medium", "1D dynamic programming",
      "Given a string `s` and a list of words `wordDict`, return `true` if `s` can be split into a sequence of one or more dictionary words (words may be reused).",
      ["1 <= s.length <= 300", "1 <= wordDict.length <= 1000"], "wordBreak", [["s", "string"], ["wordDict", "string[]"]], "bool",
      [(["leetcode", ["leet", "code"]], "leet + code."), (["applepenapple", ["apple", "pen"]], "Words may repeat."), (["catsandog", ["cats", "dog", "sand", "and", "cat"]], "No split works.")],
      [["a", ["b"]], ["aaaa", ["a", "aa"]], ["ab", ["a", "b"]], ["aaab", ["a", "aa"]]], gen_wordbreak, word_break, "O(n^2) substring checks", "O(n)",
      ["Plain recursion re-solves the same suffixes many times.",
       "Let ok[i] mean the prefix s[0..i) can be segmented. How does ok[i] depend on earlier values?",
       "ok[0] = true; ok[i] = true if some j < i has ok[j] and s[j..i) in the dictionary (use a hash set)."]),
    P("palindromic-substrings", "Palindromic Substrings", "Medium", "Expand around center",
      "Given a string `s`, return how many of its substrings are palindromes. Substrings at different positions count separately.",
      ["1 <= s.length <= 1000", "Lowercase English letters"], "countSubstrings", [["s", "string"]], "int",
      [(["abc"], "a, b, c."), (["aaa"], "a, a, a, aa, aa, aaa.")],
      [["a"], ["ab"], ["aba"], ["abba"]], gen_pal_count, count_substrings, "O(n^2)", "O(1)",
      ["Checking every substring separately is O(n^3).",
       "Every palindrome has a center: a character, or a gap between two characters.",
       "For each of the 2n-1 centers, expand outward while both ends match, counting each step."]),
    P("longest-common-subsequence", "Longest Common Subsequence", "Medium", "2D dynamic programming",
      "Given strings `text1` and `text2`, return the length of their longest common subsequence, or `0` if they share none.",
      ["1 <= text1.length, text2.length <= 1000", "Lowercase English letters"], "longestCommonSubsequence", [["text1", "string"], ["text2", "string"]], "int",
      [(["abcde", "ace"], "\"ace\"."), (["abc", "abc"], "3."), (["abc", "def"], "0.")],
      [["a", "a"], ["a", "b"], ["ab", "ba"], ["bsbininm", "jmjkbkjkv"]], gen_lcs, longest_common_subsequence, "O(m * n)", "O(n)",
      ["Look at the last characters of both strings. Match or no match?",
       "dp[i][j] = dp[i-1][j-1] + 1 on a match, else max(dp[i-1][j], dp[i][j-1]).",
       "Fill the table row by row; one rolling row is enough."]),
    P("daily-temperatures", "Daily Temperatures", "Medium", "Monotonic stack",
      "Given `temperatures`, return an array where `answer[i]` is how many days after day `i` you must wait for a warmer temperature, or `0` if none comes.",
      ["1 <= temperatures.length <= 10^5", "30 <= temperatures[i] <= 100"], "dailyTemperatures", [["temperatures", "int[]"]], "int[]",
      [([[73, 74, 75, 71, 69, 72, 76, 73]], "[1,1,4,2,1,1,0,0]."), ([[30, 40, 50, 60]], "[1,1,1,0].")],
      [[[50]], [[60, 50, 40]], [[40, 40, 41]], [[30, 60, 90]]], gen_temps, daily_temperatures, "O(n)", "O(n)",
      ["For each day, scanning forward is O(n^2). Which days are still waiting for an answer?",
       "Keep the waiting days on a stack; their temperatures are non-increasing from bottom to top.",
       "For each day i, pop every stack index with a lower temperature and set its answer to i - j; then push i."]),
    P("evaluate-reverse-polish-notation", "Evaluate Reverse Polish Notation", "Medium", "Stack",
      "Evaluate an arithmetic expression given in Reverse Polish Notation as an array of `tokens` (integers and `+ - * /`). Division truncates toward zero. Return the result.",
      ["1 <= tokens.length <= 10^4", "The expression is valid and never divides by zero", "Intermediate values fit in a 32-bit integer"], "evalRPN", [["tokens", "string[]"]], "int",
      [([["2", "1", "+", "3", "*"]], "(2 + 1) * 3 = 9."), ([["4", "13", "5", "/", "+"]], "4 + 13 / 5 = 6."), ([["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]], "22.")],
      [[["7"]], [["-7", "2", "/"]], [["3", "-4", "-"]], [["0", "3", "/"]]], gen_rpn, eval_rpn, "O(n)", "O(n)",
      ["Where do an operator's operands live when you reach it?",
       "Push numbers on a stack; an operator pops two values. Mind the order for - and /.",
       "Pop b, then a, and push a op b. Make sure division truncates toward zero (C++ does; Python's // floors)."]),
    P("subarray-sum-equals-k", "Subarray Sum Equals K", "Medium", "Prefix sums + hash map",
      "Given an integer array `nums` and an integer `k`, return the number of contiguous non-empty subarrays whose sum equals `k`.",
      ["1 <= nums.length <= 2 * 10^4", "-1000 <= nums[i] <= 1000", "-10^7 <= k <= 10^7"], "subarraySum", [["nums", "int[]"], ["k", "int"]], "int",
      [([[1, 1, 1], 2], "Two subarrays [1,1]."), ([[1, 2, 3], 3], "[1,2] and [3].")],
      [[[0], 0], [[0, 0, 0], 0], [[-1, -1, 1], 0], [[1], 2]], gen_subsum, subarray_sum, "O(n)", "O(n)",
      ["Sliding windows fail with negative numbers. Think in terms of prefix sums.",
       "sum(i..j) = prefix[j] - prefix[i-1]. For each j, how many earlier prefixes equal prefix[j] - k?",
       "Keep a hash map of prefix-sum counts, starting with {0: 1}; add count[prefix - k] at each step."]),
    P("rotting-oranges", "Rotting Oranges", "Medium", "Multi-source BFS",
      "In a grid, `0` is empty, `1` is a fresh orange and `2` is a rotten one. Each minute, fresh oranges next to a rotten one (up, down, left, right) become rotten. Return the minutes until no fresh orange remains, or `-1` if that never happens.",
      ["1 <= m, n <= 10", "grid[i][j] is 0, 1 or 2"], "orangesRotting", [["grid", "int[][]"]], "int",
      [([[[2, 1, 1], [1, 1, 0], [0, 1, 1]]], "4 minutes."), ([[[2, 1, 1], [0, 1, 1], [1, 0, 1]]], "The bottom-left orange is never reached."), ([[[0, 2]]], "No fresh oranges, so 0.")],
      [[[[0]]], [[[1]]], [[[2]]], [[[2, 1, 0, 1]]], [[[1, 2, 1]]]], gen_oranges, oranges_rotting, "O(m * n)", "O(m * n)",
      ["The rot spreads from all rotten oranges at the same time.",
       "Start a BFS with every rotten orange in the queue; each BFS level is one minute.",
       "Count fresh oranges, BFS level by level decrementing the count, and return -1 if any remain."]),
    P("course-schedule", "Course Schedule", "Medium", "Topological sort",
      "There are `numCourses` courses labelled `0` to `numCourses - 1`. `prerequisites[i] = [a, b]` means you must take `b` before `a`. Return `true` if you can finish every course.",
      ["1 <= numCourses <= 2000", "0 <= prerequisites.length <= 5000", "All pairs are distinct"], "canFinish", [["numCourses", "int"], ["prerequisites", "int[][]"]], "bool",
      [([2, [[1, 0]]], "Take 0, then 1."), ([2, [[1, 0], [0, 1]]], "A cycle.")],
      [[1, []], [3, [[0, 1], [1, 2], [2, 0]]], [4, [[1, 0], [2, 1], [3, 2]]], [3, [[1, 0], [2, 0]]]], gen_courses, can_finish, "O(V + E)", "O(V + E)",
      ["Model courses as a directed graph. What structure makes finishing impossible?",
       "You can finish exactly when the graph has no cycle.",
       "Kahn's algorithm: repeatedly take courses with in-degree 0; if you take all of them there is no cycle. DFS with three colours also works."]),
    P("spiral-matrix", "Spiral Matrix", "Medium", "Matrix simulation",
      "Given an `m x n` matrix, return all its elements in clockwise spiral order, starting from the top-left.",
      ["1 <= m, n <= 10", "-100 <= matrix[i][j] <= 100"], "spiralOrder", [["matrix", "int[][]"]], "int[]",
      [([[[1, 2, 3], [4, 5, 6], [7, 8, 9]]], "[1,2,3,6,9,8,7,4,5]."), ([[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]], "[1,2,3,4,8,12,11,10,9,5,6,7].")],
      [[[[1]]], [[[1, 2, 3]]], [[[1], [2], [3]]], [[[1, 2], [3, 4]]]], gen_spiral, spiral_order, "O(m * n)", "O(1) extra",
      ["Think of peeling the matrix one ring at a time.",
       "Keep four boundaries (top, bottom, left, right) and shrink them after each side.",
       "Traverse top row, right column, bottom row (if top < bottom), left column (if left < right); then shrink. Single rows and columns are the trap."]),
    P("rotate-image", "Rotate Image", "Medium", "Matrix",
      "Given an `n x n` matrix, rotate it 90 degrees clockwise and return it. In an interview, explain how to do it in place.",
      ["1 <= n <= 20", "-1000 <= matrix[i][j] <= 1000"], "rotate", [["matrix", "int[][]"]], "int[][]",
      [([[[1, 2, 3], [4, 5, 6], [7, 8, 9]]], "[[7,4,1],[8,5,2],[9,6,3]]."), ([[[1, 2], [3, 4]]], "[[3,1],[4,2]].")],
      [[[[1]]], [[[0, 0], [0, 1]]], [[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]]], gen_rotate, rotate_image, "O(n^2)", "O(1) in place",
      ["Where does the element at (i, j) end up after a clockwise rotation?",
       "It moves to (j, n-1-i). Could two simpler in-place operations combine to do this?",
       "Transpose the matrix (swap [i][j] with [j][i]), then reverse each row."]),
    P("koko-eating-bananas", "Koko Eating Bananas", "Medium", "Binary search on the answer",
      "Koko has `piles` of bananas and `h` hours. Each hour she picks one pile and eats up to `k` bananas from it. Return the minimum integer speed `k` that lets her finish within `h` hours.",
      ["1 <= piles.length <= 10^4", "piles.length <= h <= 10^9", "1 <= piles[i] <= 10^9"], "minEatingSpeed", [["piles", "int[]"], ["h", "int"]], "int",
      [([[3, 6, 7, 11], 8], "Speed 4."), ([[30, 11, 23, 4, 20], 5], "Speed 30."), ([[30, 11, 23, 4, 20], 6], "Speed 23.")],
      [[[1], 1], [[5], 10], [[2, 2], 2], [[1000000000], 2]], gen_koko, min_eating_speed, "O(n log max)", "O(1)",
      ["If speed k works, does every faster speed work too?",
       "That monotonicity lets you binary-search k between 1 and max(piles).",
       "hours(k) = sum(ceil(p / k)); find the smallest k with hours(k) <= h. Watch for overflow in the sum."]),
    P("longest-repeating-character-replacement", "Longest Repeating Character Replacement", "Medium", "Sliding window",
      "Given an uppercase string `s` and an integer `k`, you may change at most `k` characters to any other uppercase letter. Return the length of the longest substring that can be made of one repeated letter.",
      ["1 <= s.length <= 10^5", "0 <= k <= s.length"], "characterReplacement", [["s", "string"], ["k", "int"]], "int",
      [(["ABAB", 2], "Change both A's (or B's)."), (["AABABBA", 1], "\"AABA\" -> \"AAAA\", length 4.")],
      [["A", 0], ["AB", 0], ["AAAA", 2], ["ABCDE", 1]], gen_replace, character_replacement, "O(n)", "O(1) (26 counters)",
      ["A window is fixable when (window length - count of its most common letter) <= k.",
       "Grow the window to the right; shrink from the left when it is no longer fixable.",
       "Track letter counts in the window and the max count; shrink while len - maxCount > k; record the best length."]),
    P("generate-parentheses", "Generate Parentheses", "Medium", "Backtracking",
      "Given `n`, return every string of `n` pairs of well-formed parentheses, sorted lexicographically (`(` sorts before `)`).",
      ["1 <= n <= 8"], "generateParenthesis", [["n", "int"]], "string[]",
      [([3], "[\"((()))\",\"(()())\",\"(())()\",\"()(())\",\"()()()\"]."), ([1], "[\"()\"].")],
      [[2], [4]], gen_genparen, generate_parenthesis, "O(Catalan(n) * n)", "O(n) recursion",
      ["Generating all 2^(2n) strings and filtering is wasteful. When is adding '(' legal? When is ')'?",
       "Add '(' while opened < n; add ')' while closed < opened.",
       "Backtrack with counts of opened and closed. Trying '(' before ')' produces lexicographic order directly."]),
    P("non-overlapping-intervals", "Non-overlapping Intervals", "Medium", "Greedy, intervals",
      "Given `intervals`, return the minimum number to remove so that the rest do not overlap. Intervals that only touch (such as `[1,2]` and `[2,3]`) do not overlap.",
      ["1 <= intervals.length <= 10^5", "-5 * 10^4 <= start < end <= 5 * 10^4"], "eraseOverlapIntervals", [["intervals", "int[][]"]], "int",
      [([[[1, 2], [2, 3], [3, 4], [1, 3]]], "Remove [1,3]."), ([[[1, 2], [1, 2], [1, 2]]], "Keep one."), ([[[1, 2], [2, 3]]], "Touching is fine.")],
      [[[[0, 1]]], [[[1, 100], [11, 22], [1, 11], [2, 12]]], [[[-5, -1], [-3, 0]]]], gen_overlap, erase_overlap_intervals, "O(n log n)", "O(1) extra",
      ["Equivalently: keep as many non-overlapping intervals as possible.",
       "Which interval should you keep first to leave the most room for the others?",
       "Sort by end; keep an interval if its start >= last kept end, otherwise count it as removed."]),
]
