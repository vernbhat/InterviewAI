export type Difficulty = "Easy" | "Medium" | "Hard";

export type InterviewProblem = {
  id: string;
  title: string;
  pattern: string;
  difficulty: Difficulty;
  prompt: string;
  frequency: number;
};

export type CompanyCatalog = Record<string, InterviewProblem[]>;

const companies = [
  "Amazon",
  "Google",
  "Microsoft",
  "Meta",
  "Apple",
  "Netflix",
  "Uber",
  "Airbnb",
  "LinkedIn",
  "Adobe",
  "Salesforce",
  "Oracle",
  "Bloomberg",
  "Goldman Sachs",
  "JPMorgan",
  "Walmart",
  "PayPal",
  "Stripe",
  "Doordash",
  "TikTok",
  "Tesla",
  "Nvidia",
  "Intel",
  "Cisco",
  "Atlassian",
  "Dropbox",
  "Twitter",
  "Shopify",
  "Square",
  "Twilio"
];

const baseProblems: Omit<InterviewProblem, "id" | "frequency">[] = [
  { title: "Two Sum", pattern: "Array + hash map", difficulty: "Easy", prompt: "Return indices of two numbers that add up to a target." },
  { title: "Contains Duplicate", pattern: "Set", difficulty: "Easy", prompt: "Return true if any value appears at least twice." },
  { title: "Valid Parentheses", pattern: "Stack", difficulty: "Easy", prompt: "Determine whether brackets are closed in the correct order." },
  { title: "Best Time to Buy and Sell Stock", pattern: "Array scan", difficulty: "Easy", prompt: "Find the maximum profit from one buy and one sell." },
  { title: "Merge Two Sorted Lists", pattern: "Linked list", difficulty: "Easy", prompt: "Merge two sorted linked lists into one sorted list." },
  { title: "Reverse Linked List", pattern: "Pointers", difficulty: "Easy", prompt: "Reverse a singly linked list iteratively or recursively." },
  { title: "Valid Palindrome", pattern: "Two pointers", difficulty: "Easy", prompt: "Check whether a string is a palindrome after normalization." },
  { title: "Move Zeroes", pattern: "Two pointers", difficulty: "Easy", prompt: "Move all zeroes to the end while preserving non-zero order." },
  { title: "First Unique Character", pattern: "String counting", difficulty: "Easy", prompt: "Find the first non-repeating character in a string." },
  { title: "Merge Sorted Array", pattern: "Two pointers", difficulty: "Easy", prompt: "Merge two sorted arrays in-place into the first array." },
  { title: "Climbing Stairs", pattern: "Dynamic programming", difficulty: "Easy", prompt: "Count how many distinct ways there are to climb n steps." },
  { title: "Maximum Subarray", pattern: "Kadane", difficulty: "Medium", prompt: "Find the contiguous subarray with the largest sum." },
  { title: "Group Anagrams", pattern: "Hashing", difficulty: "Medium", prompt: "Group strings that are anagrams of each other." },
  { title: "Product of Array Except Self", pattern: "Prefix/suffix", difficulty: "Medium", prompt: "Return the product of all numbers except the current index without division." },
  { title: "Top K Frequent Elements", pattern: "Heap + hash map", difficulty: "Medium", prompt: "Return the k most frequent values in an array." },
  { title: "Number of Islands", pattern: "DFS/BFS grid", difficulty: "Medium", prompt: "Count connected groups of land cells in a grid." },
  { title: "Longest Substring Without Repeating Characters", pattern: "Sliding window", difficulty: "Medium", prompt: "Find the length of the longest substring with unique characters." },
  { title: "Subarray Sum Equals K", pattern: "Prefix sum", difficulty: "Medium", prompt: "Count subarrays whose values sum to k." },
  { title: "Binary Tree Level Order Traversal", pattern: "Queue + tree", difficulty: "Medium", prompt: "Return node values level by level from left to right." },
  { title: "Course Schedule", pattern: "Graph topological sort", difficulty: "Medium", prompt: "Decide whether all courses can be completed from prerequisites." },
  { title: "Meeting Rooms II", pattern: "Intervals + heap", difficulty: "Medium", prompt: "Find the minimum number of rooms needed for all meetings." },
  { title: "String Compression", pattern: "Two pointers", difficulty: "Medium", prompt: "Compress repeated characters in-place and return the new length." },
  { title: "LRU Cache", pattern: "Hash map + linked list", difficulty: "Medium", prompt: "Design a cache with O(1) get and put operations." },
  { title: "Find Median from Data Stream", pattern: "Two heaps", difficulty: "Hard", prompt: "Maintain a stream of numbers and return the median at any point." },
  { title: "Merge K Sorted Lists", pattern: "Heap", difficulty: "Hard", prompt: "Merge k sorted linked lists into one sorted list." },
  { title: "Trapping Rain Water", pattern: "Two pointers", difficulty: "Hard", prompt: "Compute how much water can be trapped between bars." },
  { title: "Word Ladder", pattern: "BFS", difficulty: "Hard", prompt: "Find the shortest transformation sequence from one word to another." },
  { title: "Minimum Window Substring", pattern: "Sliding window", difficulty: "Hard", prompt: "Find the smallest substring containing all required characters." },
  { title: "Serialize and Deserialize Binary Tree", pattern: "Tree design", difficulty: "Hard", prompt: "Encode and decode a binary tree without losing structure." },
  { title: "Search Insert Position", pattern: "Binary search", difficulty: "Easy", prompt: "Return the index where target is found or should be inserted." },
  { title: "Plus One", pattern: "Array carry", difficulty: "Easy", prompt: "Add one to an integer represented as digits." },
  { title: "Roman to Integer", pattern: "Hash map", difficulty: "Easy", prompt: "Convert a Roman numeral string into an integer." },
  { title: "Longest Common Prefix", pattern: "String scan", difficulty: "Easy", prompt: "Find the longest prefix shared by all strings." },
  { title: "Remove Duplicates from Sorted Array", pattern: "Two pointers", difficulty: "Easy", prompt: "Remove duplicates in-place and return the new length." },
  { title: "Sqrt(x)", pattern: "Binary search", difficulty: "Easy", prompt: "Return the integer square root of a non-negative number." },
  { title: "Symmetric Tree", pattern: "Tree recursion", difficulty: "Easy", prompt: "Check whether a binary tree mirrors itself." },
  { title: "Maximum Depth of Binary Tree", pattern: "DFS tree", difficulty: "Easy", prompt: "Return the maximum depth of a binary tree." },
  { title: "Path Sum", pattern: "Tree DFS", difficulty: "Easy", prompt: "Check if a root-to-leaf path equals the target sum." },
  { title: "Same Tree", pattern: "Tree recursion", difficulty: "Easy", prompt: "Determine whether two binary trees are structurally identical." },
  { title: "Invert Binary Tree", pattern: "Tree recursion", difficulty: "Easy", prompt: "Invert a binary tree by swapping left and right children." },
  { title: "Flood Fill", pattern: "DFS/BFS grid", difficulty: "Easy", prompt: "Recolor all connected pixels matching the starting color." },
  { title: "Majority Element", pattern: "Boyer-Moore", difficulty: "Easy", prompt: "Return the element appearing more than half the time." },
  { title: "Linked List Cycle", pattern: "Fast/slow pointers", difficulty: "Easy", prompt: "Detect whether a linked list contains a cycle." },
  { title: "Palindrome Linked List", pattern: "Fast/slow pointers", difficulty: "Easy", prompt: "Check whether a linked list reads the same forward and backward." },
  { title: "Min Stack", pattern: "Stack design", difficulty: "Medium", prompt: "Design a stack that can return its minimum in constant time." },
  { title: "Evaluate Reverse Polish Notation", pattern: "Stack", difficulty: "Medium", prompt: "Evaluate an arithmetic expression written in postfix notation." },
  { title: "Generate Parentheses", pattern: "Backtracking", difficulty: "Medium", prompt: "Generate all valid combinations of n pairs of parentheses." },
  { title: "Combination Sum", pattern: "Backtracking", difficulty: "Medium", prompt: "Find all combinations of numbers that sum to a target." },
  { title: "Permutations", pattern: "Backtracking", difficulty: "Medium", prompt: "Return all permutations of distinct integers." },
  { title: "Subsets", pattern: "Backtracking", difficulty: "Medium", prompt: "Return all possible subsets of a list of unique integers." },
  { title: "Word Search", pattern: "Backtracking grid", difficulty: "Medium", prompt: "Determine whether a word exists in a character grid." },
  { title: "Rotate Image", pattern: "Matrix", difficulty: "Medium", prompt: "Rotate an n x n image matrix by 90 degrees in-place." },
  { title: "Spiral Matrix", pattern: "Matrix traversal", difficulty: "Medium", prompt: "Return all elements of a matrix in spiral order." },
  { title: "Set Matrix Zeroes", pattern: "Matrix markers", difficulty: "Medium", prompt: "Set rows and columns to zero if a cell is zero." },
  { title: "Search a 2D Matrix", pattern: "Binary search", difficulty: "Medium", prompt: "Search a sorted 2D matrix for a target value." },
  { title: "Search in Rotated Sorted Array", pattern: "Binary search", difficulty: "Medium", prompt: "Find a target in a rotated sorted array." },
  { title: "Find Minimum in Rotated Sorted Array", pattern: "Binary search", difficulty: "Medium", prompt: "Find the minimum element in a rotated sorted array." },
  { title: "Kth Largest Element in an Array", pattern: "Heap/quickselect", difficulty: "Medium", prompt: "Return the kth largest value in an unsorted array." },
  { title: "Insert Interval", pattern: "Intervals", difficulty: "Medium", prompt: "Insert and merge a new interval into sorted non-overlapping intervals." },
  { title: "Merge Intervals", pattern: "Intervals", difficulty: "Medium", prompt: "Merge all overlapping intervals." },
  { title: "Non-overlapping Intervals", pattern: "Greedy intervals", difficulty: "Medium", prompt: "Remove the minimum number of intervals to eliminate overlap." },
  { title: "Partition Labels", pattern: "Greedy", difficulty: "Medium", prompt: "Partition a string so each letter appears in at most one part." },
  { title: "Coin Change", pattern: "Dynamic programming", difficulty: "Medium", prompt: "Return the fewest coins needed to make an amount." },
  { title: "House Robber", pattern: "Dynamic programming", difficulty: "Medium", prompt: "Find the maximum money that can be robbed without adjacent houses." },
  { title: "Decode Ways", pattern: "Dynamic programming", difficulty: "Medium", prompt: "Count how many ways a digit string can be decoded." },
  { title: "Unique Paths", pattern: "Dynamic programming", difficulty: "Medium", prompt: "Count paths from the top-left to bottom-right of a grid." },
  { title: "Longest Increasing Subsequence", pattern: "Dynamic programming", difficulty: "Medium", prompt: "Find the length of the longest strictly increasing subsequence." },
  { title: "Jump Game", pattern: "Greedy", difficulty: "Medium", prompt: "Determine whether the last index can be reached." },
  { title: "Gas Station", pattern: "Greedy", difficulty: "Medium", prompt: "Find a start station to complete the circuit if possible." },
  { title: "Clone Graph", pattern: "Graph DFS/BFS", difficulty: "Medium", prompt: "Deep copy an undirected graph." },
  { title: "Pacific Atlantic Water Flow", pattern: "DFS/BFS grid", difficulty: "Medium", prompt: "Find cells that can flow to both oceans." },
  { title: "Rotting Oranges", pattern: "BFS grid", difficulty: "Medium", prompt: "Return minutes until all fresh oranges rot." },
  { title: "Accounts Merge", pattern: "Union find", difficulty: "Medium", prompt: "Merge account records that share email addresses." },
  { title: "Lowest Common Ancestor of a Binary Tree", pattern: "Tree recursion", difficulty: "Medium", prompt: "Find the lowest common ancestor of two nodes." },
  { title: "Validate Binary Search Tree", pattern: "Tree DFS", difficulty: "Medium", prompt: "Check whether a binary tree satisfies BST ordering." },
  { title: "Kth Smallest Element in a BST", pattern: "Tree inorder", difficulty: "Medium", prompt: "Return the kth smallest value in a BST." },
  { title: "Construct Binary Tree from Preorder and Inorder Traversal", pattern: "Tree construction", difficulty: "Medium", prompt: "Build a binary tree from preorder and inorder arrays." },
  { title: "Binary Tree Right Side View", pattern: "Tree BFS", difficulty: "Medium", prompt: "Return nodes visible from the right side." },
  { title: "Reorder List", pattern: "Linked list", difficulty: "Medium", prompt: "Reorder a linked list by alternating front and back nodes." },
  { title: "Remove Nth Node From End of List", pattern: "Two pointers", difficulty: "Medium", prompt: "Remove the nth node from the end of a linked list." },
  { title: "Add Two Numbers", pattern: "Linked list carry", difficulty: "Medium", prompt: "Add two numbers represented by linked lists." },
  { title: "Design Add and Search Words Data Structure", pattern: "Trie", difficulty: "Medium", prompt: "Support adding words and searching with wildcard dots." },
  { title: "Implement Trie", pattern: "Trie", difficulty: "Medium", prompt: "Implement insert, search, and prefix lookup for words." },
  { title: "Word Break", pattern: "Dynamic programming", difficulty: "Medium", prompt: "Determine whether a string can be segmented into dictionary words." },
  { title: "Daily Temperatures", pattern: "Monotonic stack", difficulty: "Medium", prompt: "Return days until a warmer temperature for each day." },
  { title: "Car Fleet", pattern: "Sorting + stack", difficulty: "Medium", prompt: "Count fleets that arrive at a target." },
  { title: "Largest Rectangle in Histogram", pattern: "Monotonic stack", difficulty: "Hard", prompt: "Find the largest rectangle area in a histogram." },
  { title: "Sliding Window Maximum", pattern: "Deque", difficulty: "Hard", prompt: "Return the maximum value in every window of size k." },
  { title: "Regular Expression Matching", pattern: "Dynamic programming", difficulty: "Hard", prompt: "Match a string against a pattern with dot and star." },
  { title: "Edit Distance", pattern: "Dynamic programming", difficulty: "Hard", prompt: "Compute the minimum edits needed to convert one word to another." },
  { title: "Burst Balloons", pattern: "Interval DP", difficulty: "Hard", prompt: "Maximize coins by choosing the best order to burst balloons." },
  { title: "Alien Dictionary", pattern: "Graph topological sort", difficulty: "Hard", prompt: "Infer a valid character ordering from sorted alien words." },
  { title: "N-Queens", pattern: "Backtracking", difficulty: "Hard", prompt: "Place n queens on a board so none attack each other." },
  { title: "Word Search II", pattern: "Trie + backtracking", difficulty: "Hard", prompt: "Find all dictionary words present in a character board." },
  { title: "Palindrome Pairs", pattern: "Trie/hash map", difficulty: "Hard", prompt: "Find index pairs whose concatenation forms a palindrome." },
  { title: "Basic Calculator", pattern: "Stack parsing", difficulty: "Hard", prompt: "Evaluate a string expression with parentheses and signs." }
];

function slug(value: string) {
  return value.toLowerCase().replace(/\s+/g, "-");
}

function rotateProblems(company: string, companyIndex: number) {
  return baseProblems.map((problem, problemIndex) => {
    const rankingSeed = ((companyIndex + 3) * (problemIndex + 5)) % 97;
    return {
      ...problem,
      id: `${slug(company)}-${slug(problem.title)}`,
      frequency: 100 - rankingSeed
    };
  }).sort((left, right) => right.frequency - left.frequency);
}

export async function fetchCompanyQuestionCatalog(): Promise<CompanyCatalog> {
  const catalog = Object.fromEntries(companies.map((company, index) => [company, rotateProblems(company, index)]));
  return new Promise((resolve) => {
    window.setTimeout(() => resolve(catalog), 120);
  });
}
