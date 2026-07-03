import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  Bot,
  Code2,
  History,
  Lightbulb,
  Mic,
  PhoneOff,
  Play,
  Radio,
  Send,
  Sparkles,
  Video
} from "lucide-react";
import { Difficulty, InterviewProblem, fetchCompanyQuestionCatalog } from "./questionCatalog";
import "./styles.css";

const realtimeUrl = import.meta.env.VITE_REALTIME_URL || "ws://localhost:8787";
const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";

type Language = "cpp" | "java" | "python" | "javascript";
type QuestionPreference = "easy-medium" | "medium-medium" | "medium-hard" | "manual";

const languageLabels: Record<Language, string> = {
  cpp: "C++",
  java: "Java",
  python: "Python",
  javascript: "JS"
};

const fallbackProblems: InterviewProblem[] = [
  {
    id: "amazon-two-sum",
    title: "Two Sum",
    pattern: "Array + hash map",
    difficulty: "Easy",
    prompt: "Return indices of two numbers that add up to a target.",
    frequency: 100
  },
  {
    id: "amazon-group-anagrams",
    title: "Group Anagrams",
    pattern: "Hashing",
    difficulty: "Medium",
    prompt: "Group strings that are anagrams of each other.",
    frequency: 96
  }
];

const preferenceLabels: Record<QuestionPreference, string> = {
  "easy-medium": "1 Easy + 1 Medium",
  "medium-medium": "2 Medium",
  "medium-hard": "1 Medium + 1 Hard",
  manual: "Manual questions"
};

const preferenceDifficulties: Record<Exclude<QuestionPreference, "manual">, Difficulty[]> = {
  "easy-medium": ["Easy", "Medium"],
  "medium-medium": ["Medium", "Medium"],
  "medium-hard": ["Medium", "Hard"]
};

const languages: Language[] = ["cpp", "java", "python", "javascript"];
const fallbackCatalog = { Amazon: fallbackProblems };

function pickInterviewQuestions(problems: InterviewProblem[], preference: QuestionPreference) {
  if (preference === "manual") {
    return problems.slice(0, 2);
  }

  const picked: InterviewProblem[] = [];

  for (const difficulty of preferenceDifficulties[preference]) {
    const next = problems.find((problem) => problem.difficulty === difficulty && !picked.some((item) => item.id === problem.id));
    if (next) {
      picked.push(next);
    }
  }

  for (const problem of problems) {
    if (picked.length >= 2) break;
    if (!picked.some((item) => item.id === problem.id)) {
      picked.push(problem);
    }
  }

  return picked.slice(0, 2);
}

function buildStarterCode(language: Language, problem: InterviewProblem) {
  const problemComment = `${problem.title}: ${problem.prompt}`;

  const templates: Record<Language, string> = {
    cpp: `// ${problemComment}
#include <vector>
#include <unordered_map>
using namespace std;

class Solution {
public:
  vector<int> solve(vector<int>& nums, int target) {
    // Talk through the brute force first, then optimize.
    return {};
  }
};`,
    java: `// ${problemComment}
import java.util.HashMap;
import java.util.Map;

class Solution {
  public int[] solve(int[] nums, int target) {
    // Talk through the brute force first, then optimize.
    return new int[] {};
  }
}`,
    python: `# ${problemComment}
class Solution:
    def solve(self, nums: list[int], target: int) -> list[int]:
        # Talk through the brute force first, then optimize.
        return []`,
    javascript: `// ${problemComment}
function solve(nums, target) {
  // Talk through the brute force first, then optimize.
  return [];
}`
  };

  return templates[language];
}

type ChatLine = {
  actor: "AI" | "Candidate" | "System";
  text: string;
};

const keywordMap: Record<Language, Set<string>> = {
  cpp: new Set(["class", "public", "private", "return", "if", "else", "for", "while", "int", "long", "bool", "true", "false", "void", "using", "namespace", "include", "vector", "unordered_map", "string"]),
  java: new Set(["class", "public", "private", "return", "if", "else", "for", "while", "int", "long", "boolean", "true", "false", "void", "new", "import", "Map", "HashMap", "String"]),
  python: new Set(["class", "def", "return", "if", "else", "elif", "for", "while", "in", "not", "and", "or", "True", "False", "None", "list", "dict", "range"]),
  javascript: new Set(["function", "const", "let", "var", "return", "if", "else", "for", "while", "true", "false", "class", "new", "Map", "Set", "null", "undefined"])
};

const tokenPattern = /(\/\/.*|#.*|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\b\d+(?:\.\d+)?\b|\b[A-Za-z_][A-Za-z0-9_]*\b|[{}()[\];,.+\-*/%=<>!&|:]+)/g;

function highlightedLine(line: string, language: Language, lineIndex: number) {
  const pieces = line.split(tokenPattern).filter((piece) => piece.length > 0);

  return pieces.map((piece, pieceIndex) => {
    let className = "codeText";
    if (piece.startsWith("//") || piece.startsWith("#")) {
      className = "codeComment";
    } else if ((piece.startsWith("\"") && piece.endsWith("\"")) || (piece.startsWith("'") && piece.endsWith("'"))) {
      className = "codeString";
    } else if (/^\d/.test(piece)) {
      className = "codeNumber";
    } else if (keywordMap[language].has(piece)) {
      className = "codeKeyword";
    } else if (/^[{}()[\];,.+\-*/%=<>!&|:]+$/.test(piece)) {
      className = "codePunctuation";
    }

    return <span className={className} key={`${lineIndex}-${pieceIndex}`}>{piece}</span>;
  });
}

type ProblemDetail = {
  variables: Array<{ name: string; description: string }>;
  examples: Array<{ input: string; output: string; explanation: string }>;
  constraints: string[];
};

function detailForProblem(problem: InterviewProblem): ProblemDetail {
  const title = problem.title.toLowerCase();

  if (title.includes("two sum")) {
    return {
      variables: [
        { name: "nums", description: "Integer array searched for the pair." },
        { name: "target", description: "Required sum of the two selected values." },
        { name: "seen", description: "Hash map from value to its earlier index." }
      ],
      examples: [
        { input: "nums = [2,7,11,15], target = 9", output: "[0,1]", explanation: "nums[0] + nums[1] equals 9." },
        { input: "nums = [3,2,4], target = 6", output: "[1,2]", explanation: "2 and 4 form the target." }
      ],
      constraints: ["2 <= nums.length <= 10^4", "Return exactly one valid pair.", "The same element cannot be used twice."]
    };
  }

  if (title.includes("search insert")) {
    return {
      variables: [
        { name: "nums", description: "Sorted array of distinct integers." },
        { name: "target", description: "Value to locate or insert." },
        { name: "left/right", description: "Binary search bounds." }
      ],
      examples: [
        { input: "nums = [1,3,5,6], target = 5", output: "2", explanation: "5 already appears at index 2." },
        { input: "nums = [1,3,5,6], target = 2", output: "1", explanation: "2 should be inserted before 3." }
      ],
      constraints: ["1 <= nums.length <= 10^4", "nums is sorted in ascending order.", "Aim for O(log n) time."]
    };
  }

  if (problem.pattern.toLowerCase().includes("tree")) {
    return {
      variables: [
        { name: "root", description: "Current tree node being processed." },
        { name: "left/right", description: "Child subtrees used for recursion or traversal." },
        { name: "result", description: "Collected answer for the traversal or check." }
      ],
      examples: [
        { input: "root = [3,9,20,null,null,15,7]", output: "varies by task", explanation: "Walk level by level or recursively depending on the prompt." },
        { input: "root = []", output: "empty result", explanation: "Handle the empty tree before traversing." }
      ],
      constraints: ["0 <= number of nodes <= 10^4", "Node values may be negative.", "Explain DFS vs BFS tradeoffs."]
    };
  }

  if (problem.pattern.toLowerCase().includes("grid") || problem.pattern.toLowerCase().includes("matrix")) {
    return {
      variables: [
        { name: "grid", description: "2D input board or matrix." },
        { name: "row/col", description: "Current cell coordinates." },
        { name: "visited", description: "Tracks cells already processed." }
      ],
      examples: [
        { input: "grid = [[1,1,0],[0,1,0],[1,0,1]]", output: "depends on task", explanation: "Neighbors are usually checked in four directions." },
        { input: "grid = []", output: "0 or empty result", explanation: "Guard empty input before scanning." }
      ],
      constraints: ["1 <= rows, cols <= 300", "Check boundaries before reading a cell.", "Avoid revisiting the same cell."]
    };
  }

  if (problem.pattern.toLowerCase().includes("linked list")) {
    return {
      variables: [
        { name: "head", description: "Start of the linked list." },
        { name: "prev/current", description: "Pointers used to relink nodes." },
        { name: "next", description: "Temporary pointer to avoid losing the list." }
      ],
      examples: [
        { input: "head = [1,2,3,4]", output: "task-specific list", explanation: "Walk nodes while preserving links." },
        { input: "head = []", output: "[]", explanation: "Empty list should return cleanly." }
      ],
      constraints: ["0 <= list length <= 5000", "Use O(1) extra space when possible.", "Be precise about pointer update order."]
    };
  }

  if (problem.pattern.toLowerCase().includes("stack")) {
    return {
      variables: [
        { name: "stack", description: "Stores unmatched tokens or pending values." },
        { name: "current", description: "Current character or value being processed." },
        { name: "top", description: "Most recent stack item used for comparison." }
      ],
      examples: [
        { input: "s = \"()[]{}\"", output: "true", explanation: "Each closing token matches the most recent opening token." },
        { input: "s = \"(]\"", output: "false", explanation: "The closing bracket does not match the stack top." }
      ],
      constraints: ["0 <= input length <= 10^4", "Stack operations should be O(1).", "Explain what invalid states look like."]
    };
  }

  return {
    variables: [
      { name: "input", description: "Primary data structure from the prompt." },
      { name: "index", description: "Current scan position or iteration counter." },
      { name: "result", description: "Value returned after processing." }
    ],
    examples: [
      { input: "input = small sample", output: "expected result", explanation: `Apply the ${problem.pattern} approach directly.` },
      { input: "input = edge case", output: "boundary result", explanation: "Check empty, single-item, duplicate, or invalid inputs." }
    ],
    constraints: ["Start with brute force, then optimize.", "State time and space complexity.", "Cover at least one edge case before coding."]
  };
}

type Feedback = {
  overall_score: number;
  recommendation: string;
  strengths: string[];
  improvements: string[];
  rubric: Record<string, number>;
};

function App() {
  const [connected, setConnected] = useState(false);
  const [language, setLanguage] = useState<Language>("javascript");
  const [catalog, setCatalog] = useState<Record<string, InterviewProblem[]>>(fallbackCatalog);
  const [catalogStatus, setCatalogStatus] = useState("Loading company question catalog...");
  const [company, setCompany] = useState("Amazon");
  const [preference, setPreference] = useState<QuestionPreference>("easy-medium");
  const [manualQuestionIds, setManualQuestionIds] = useState<[string, string]>([fallbackProblems[0].id, fallbackProblems[1].id]);
  const [activeQuestionIndex, setActiveQuestionIndex] = useState(0);
  const companies = Object.keys(catalog);
  const companyProblems = catalog[company] || fallbackProblems;
  const manualQuestions = manualQuestionIds.map((id) => companyProblems.find((problem) => problem.id === id)).filter(Boolean) as InterviewProblem[];
  const selectedQuestions = preference === "manual" && manualQuestions.length === 2
    ? manualQuestions
    : pickInterviewQuestions(companyProblems, preference);
  const selectedProblem = selectedQuestions[activeQuestionIndex] || selectedQuestions[0] || fallbackProblems[0];
  const selectedProblemDetail = detailForProblem(selectedProblem);
  const [code, setCode] = useState(() => buildStarterCode("javascript", fallbackProblems[0]));
  const [chat, setChat] = useState<ChatLine[]>([
    { actor: "AI", text: "Welcome. This is a junior coding screen, so start with examples and a simple brute-force approach." }
  ]);
  const [candidateNote, setCandidateNote] = useState("");
  const [hint, setHint] = useState("Ask for a hint when the candidate stalls or starts guessing.");
  const [feedback, setFeedback] = useState<Feedback | null>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const editorRef = useRef<HTMLTextAreaElement | null>(null);
  const syntaxRef = useRef<HTMLPreElement | null>(null);
  const lastCodeRef = useRef(code);

  const session = useMemo(
    () => ({
      id: "demo-session",
      candidate: "KS",
      role: "Junior Software Engineer",
      difficulty: "junior"
    }),
    []
  );

  useEffect(() => {
    lastCodeRef.current = code;
  }, [code]);

  function selectLanguage(nextLanguage: Language) {
    setLanguage(nextLanguage);
    setCode(buildStarterCode(nextLanguage, selectedProblem));
  }

  function selectCompany(nextCompany: string) {
    const nextProblems = catalog[nextCompany] || fallbackProblems;
    const nextQuestions = pickInterviewQuestions(nextProblems, preference);
    const nextProblem = nextQuestions[0] || nextProblems[0];
    setCompany(nextCompany);
    setManualQuestionIds([nextProblems[0]?.id || fallbackProblems[0].id, nextProblems[1]?.id || fallbackProblems[1].id]);
    setActiveQuestionIndex(0);
    setCode(buildStarterCode(language, nextProblem));
    setHint(`Loaded ${nextProblems.length} ${nextCompany} questions. Starting with ${nextProblem.title}.`);
  }

  function selectPreference(nextPreference: QuestionPreference) {
    const nextQuestions = nextPreference === "manual"
      ? manualQuestionIds.map((id) => companyProblems.find((problem) => problem.id === id)).filter(Boolean) as InterviewProblem[]
      : pickInterviewQuestions(companyProblems, nextPreference);
    const nextProblem = nextQuestions[0] || companyProblems[0];
    setPreference(nextPreference);
    setActiveQuestionIndex(0);
    setCode(buildStarterCode(language, nextProblem));
    setHint(`Preference set to ${preferenceLabels[nextPreference]}. The interview now has two selected questions.`);
  }

  function selectManualQuestion(slot: 0 | 1, problemId: string) {
    const nextIds: [string, string] = [...manualQuestionIds];
    nextIds[slot] = problemId;
    const nextProblem = companyProblems.find((problem) => problem.id === problemId) || companyProblems[0];
    setManualQuestionIds(nextIds);
    setPreference("manual");
    setActiveQuestionIndex(slot);
    setCode(buildStarterCode(language, nextProblem));
    setHint(`Manual question ${slot + 1} set to ${nextProblem.title}.`);
  }

  function selectActiveQuestion(nextIndex: number) {
    const nextProblem = selectedQuestions[nextIndex];
    if (!nextProblem) return;
    setActiveQuestionIndex(nextIndex);
    setCode(buildStarterCode(language, nextProblem));
    setHint(`Selected ${nextProblem.title}. Look for clear examples, edge cases, and a simple optimization path.`);
  }

  useEffect(() => {
    const socket = new WebSocket(realtimeUrl);
    socketRef.current = socket;

    socket.addEventListener("open", () => {
      setConnected(true);
      socket.send(JSON.stringify({ type: "join", sessionId: session.id }));
    });

    socket.addEventListener("close", () => setConnected(false));
    socket.addEventListener("message", (event) => {
      const message = JSON.parse(event.data);
      if (message.type === "hint") {
        setHint(message.payload.hint);
      }
      if (message.type === "chat") {
        setChat((current) => [...current, { actor: "Candidate", text: message.text }]);
      }
    });

    return () => socket.close();
  }, [session.id]);

  useEffect(() => {
    let cancelled = false;

    fetchCompanyQuestionCatalog().then((nextCatalog) => {
      if (cancelled) return;
      setCatalog(nextCatalog);
      setCatalogStatus(`${Object.keys(nextCatalog).length} companies loaded`);
      const nextProblems = nextCatalog.Amazon || fallbackProblems;
      const nextProblem = pickInterviewQuestions(nextProblems, preference)[0] || nextProblems[0];
      setManualQuestionIds([nextProblems[0]?.id || fallbackProblems[0].id, nextProblems[1]?.id || fallbackProblems[1].id]);
      setCode(buildStarterCode(language, nextProblem));
    });

    return () => {
      cancelled = true;
    };
  }, []);

  async function askInterviewer() {
    const response = await fetch(`${apiUrl}/interviewer/turn`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        session_id: session.id,
        role_title: session.role,
        difficulty: session.difficulty,
        transcript: chat.map((line) => ({ role: line.actor, text: line.text })),
        code,
        company,
        problem: selectedProblem.title
      })
    });
    const data = await response.json();
    setChat((current) => [...current, { actor: "AI", text: data.message }]);
  }

  function requestHint() {
    socketRef.current?.send(
      JSON.stringify({
        type: "hint_request",
        payload: {
          session_id: session.id,
          problem: `${company} ${selectedProblem.title}: ${selectedProblem.prompt}`,
          language,
          code
        }
      })
    );
  }

  function sendCandidateNote() {
    const text = candidateNote.trim();
    if (!text) return;
    setChat((current) => [...current, { actor: "Candidate", text }]);
    socketRef.current?.send(JSON.stringify({ type: "chat", text }));
    setCandidateNote("");
  }

  async function generateFeedback() {
    const response = await fetch(`${apiUrl}/feedback/generate`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        session_id: session.id,
        transcript: chat.map((line) => ({ role: line.actor, text: line.text })),
        code,
        tests_passed: 6,
        tests_total: 7,
        signal_summary: { sentiment: "focused", engagement: 0.82, stress: 0.31 }
      })
    });
    setFeedback(await response.json());
  }

  const lineNumbers = code.split("\n").map((_, index) => index + 1);

  function replaceSelection(nextText: string, cursorOffset = nextText.length) {
    const editor = editorRef.current;
    if (!editor) return;

    replaceCodeRange(editor.selectionStart, editor.selectionEnd, nextText, cursorOffset);
  }

  function replaceCodeRange(start: number, end: number, nextText: string, cursorOffset = nextText.length) {
    const editor = editorRef.current;
    if (!editor) return;

    const nextCode = `${code.slice(0, start)}${nextText}${code.slice(end)}`;
    lastCodeRef.current = nextCode;
    setCode(nextCode);

    window.requestAnimationFrame(() => {
      editor.focus();
      editor.setSelectionRange(start + cursorOffset, start + cursorOffset);
    });
  }

  function handleCodeKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    const editor = event.currentTarget;
    const pairs: Record<string, string> = {
      "(": ")",
      "[": "]",
      "{": "}",
      "\"": "\"",
      "'": "'"
    };

    if (event.key === "Tab") {
      event.preventDefault();
      const lineStart = code.lastIndexOf("\n", editor.selectionStart - 1) + 1;
      const beforeCursor = code.slice(lineStart, editor.selectionStart);
      const snippetKey = beforeCursor.trim();

      if (snippetKey === "if") {
        const tokenStart = editor.selectionStart - beforeCursor.length + beforeCursor.search(/\S/);
        replaceCodeRange(tokenStart, editor.selectionStart, "if () {\n  \n}", 4);
        return;
      }

      if (snippetKey === "for") {
        const tokenStart = editor.selectionStart - beforeCursor.length + beforeCursor.search(/\S/);
        replaceCodeRange(tokenStart, editor.selectionStart, "for (let i = 0; i < n; i += 1) {\n  \n}", 13);
        return;
      }

      replaceSelection("  ");
      return;
    }

    if (event.key === "Backspace" && editor.selectionStart === editor.selectionEnd) {
      const before = code[editor.selectionStart - 1];
      const after = code[editor.selectionStart];

      if (before && pairs[before] === after) {
        event.preventDefault();
        replaceCodeRange(editor.selectionStart - 1, editor.selectionStart + 1, "", 0);
        return;
      }
    }

    if (event.key === "Delete" && editor.selectionStart === editor.selectionEnd) {
      const before = code[editor.selectionStart - 1];
      const current = code[editor.selectionStart];
      const after = code[editor.selectionStart + 1];

      if (before && current && pairs[before] === current) {
        event.preventDefault();
        replaceCodeRange(editor.selectionStart - 1, editor.selectionStart + 1, "", 0);
        return;
      }

      if (current && pairs[current] === after) {
        event.preventDefault();
        replaceCodeRange(editor.selectionStart, editor.selectionStart + 2, "", 0);
        return;
      }
    }

    if (pairs[event.key]) {
      event.preventDefault();
      replaceSelection(`${event.key}${pairs[event.key]}`, 1);
      return;
    }

    if (event.key === "Enter") {
      event.preventDefault();
      const lineStart = code.lastIndexOf("\n", editor.selectionStart - 1) + 1;
      const currentLine = code.slice(lineStart, editor.selectionStart);
      const indent = currentLine.match(/^\s*/)?.[0] || "";
      const extraIndent = /[{(:]\s*$/.test(currentLine) ? "  " : "";
      replaceSelection(`\n${indent}${extraIndent}`);
    }
  }

  function handleCodeChange(event: React.ChangeEvent<HTMLTextAreaElement>) {
    const nextValue = event.target.value;
    const cursor = event.target.selectionStart;
    const inserted = nextValue[cursor - 1];
    const previousCode = lastCodeRef.current;
    const pairs: Record<string, string> = {
      "(": ")",
      "[": "]",
      "{": "}",
      "\"": "\"",
      "'": "'"
    };

    if (
      inserted &&
      pairs[inserted] &&
      nextValue.length === previousCode.length + 1 &&
      nextValue.slice(0, cursor - 1) === previousCode.slice(0, cursor - 1) &&
      nextValue.slice(cursor) === previousCode.slice(cursor - 1)
    ) {
      const nextCode = `${nextValue.slice(0, cursor)}${pairs[inserted]}${nextValue.slice(cursor)}`;
      lastCodeRef.current = nextCode;
      setCode(nextCode);
      window.requestAnimationFrame(() => {
        editorRef.current?.setSelectionRange(cursor, cursor);
      });
      return;
    }

    lastCodeRef.current = nextValue;
    setCode(nextValue);
  }

  function syncCodeScroll(event: React.UIEvent<HTMLTextAreaElement>) {
    if (!syntaxRef.current) return;
    syntaxRef.current.scrollTop = event.currentTarget.scrollTop;
    syntaxRef.current.scrollLeft = event.currentTarget.scrollLeft;
  }

  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brandMark">
            <Sparkles size={20} />
          </div>
          <div>
            <strong>Interview AI</strong>
            <span>Live technical screen</span>
          </div>
        </div>

        <nav className="nav">
          <button className="active"><Radio size={18} /> Live room</button>
          <button><History size={18} /> Candidate history</button>
          <button><Activity size={18} /> Signal review</button>
        </nav>

        <section className="candidate">
          <p>Candidate</p>
          <h2>{session.candidate}</h2>
          <span>{session.role}</span>
        </section>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <p>{company} style LeetCode practice</p>
            <h1>{selectedProblem.title}</h1>
          </div>
          <div className="actions">
            <span className={connected ? "status online" : "status"}>{connected ? "Realtime on" : "Offline"}</span>
            <button aria-label="Start tests"><Play size={18} /> Run</button>
            <button className="danger" aria-label="End call"><PhoneOff size={18} /></button>
          </div>
        </header>

        <div className="interviewGrid">
          <section className="videoPane">
            <div className="questionBank">
              <div className="questionMeta">
                <span>Question bank</span>
                <strong>{company}</strong>
              </div>
              <div className="questionControls">
                <label>
                  Company
                  <select value={company} onChange={(event) => selectCompany(event.target.value)}>
                    {companies.map((option) => (
                      <option key={option} value={option}>{option}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Preference
                  <select value={preference} onChange={(event) => selectPreference(event.target.value as QuestionPreference)}>
                    {Object.entries(preferenceLabels).map(([value, label]) => (
                      <option key={value} value={value}>{label}</option>
                    ))}
                  </select>
                </label>
              </div>
              {preference === "manual" && (
                <div className="manualQuestionControls">
                  <label>
                    Question 1
                    <select value={manualQuestionIds[0]} onChange={(event) => selectManualQuestion(0, event.target.value)}>
                      {companyProblems.map((problem) => (
                        <option key={problem.id} value={problem.id}>
                          {problem.title} - {problem.difficulty}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label>
                    Question 2
                    <select value={manualQuestionIds[1]} onChange={(event) => selectManualQuestion(1, event.target.value)}>
                      {companyProblems.map((problem) => (
                        <option key={problem.id} value={problem.id}>
                          {problem.title} - {problem.difficulty}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>
              )}
              <div className="selectedQuestions">
                {selectedQuestions.map((problem, index) => (
                  <button
                    key={problem.id}
                    className={index === activeQuestionIndex ? "selected" : ""}
                    onClick={() => selectActiveQuestion(index)}
                    type="button"
                  >
                    <span>Q{index + 1}</span>
                    <strong>{problem.title}</strong>
                    <small>{problem.difficulty} | {problem.pattern}</small>
                  </button>
                ))}
              </div>
              <div className="problemCard">
                <strong>{selectedProblem.title}</strong>
                <span>{selectedProblem.difficulty} | {selectedProblem.pattern}</span>
                <p>{selectedProblem.prompt}</p>
              </div>
              <div className="problemDetail">
                <section>
                  <h3>Examples</h3>
                  {selectedProblemDetail.examples.map((example, index) => (
                    <article className="exampleBlock" key={`${selectedProblem.id}-example-${index}`}>
                      <strong>Example {index + 1}</strong>
                      <code>Input: {example.input}</code>
                      <code>Output: {example.output}</code>
                      <p>{example.explanation}</p>
                    </article>
                  ))}
                </section>
                <section>
                  <h3>Variables</h3>
                  <div className="variableList">
                    {selectedProblemDetail.variables.map((variable) => (
                      <div key={variable.name}>
                        <code>{variable.name}</code>
                        <span>{variable.description}</span>
                      </div>
                    ))}
                  </div>
                </section>
                <section>
                  <h3>Constraints</h3>
                  <ul>
                    {selectedProblemDetail.constraints.map((constraint) => (
                      <li key={constraint}>{constraint}</li>
                    ))}
                  </ul>
                </section>
              </div>
            </div>
            <div className="videoTile interviewer">
              <Video size={22} />
              <span>AI interviewer</span>
            </div>
            <div className="videoTile candidateTile">
              <Mic size={22} />
              <span>Candidate audio + speech</span>
            </div>
            <div className="signals">
              <div><span>Engagement</span><strong>82%</strong></div>
              <div><span>Stress</span><strong>31%</strong></div>
              <div><span>Speech confidence</span><strong>91%</strong></div>
            </div>
          </section>

          <section className="editorPane">
            <div className="paneHeader">
              <div><Code2 size={18} /> {languageLabels[language]}</div>
              <div className="editorTools">
                <div className="languageTabs" aria-label="Select coding language">
                  {languages.map((option) => (
                    <button
                      key={option}
                      className={option === language ? "selected" : ""}
                      onClick={() => selectLanguage(option)}
                      type="button"
                    >
                      {languageLabels[option]}
                    </button>
                  ))}
                </div>
              </div>
            </div>
            <div className="leetcodeEditor">
              <div className="lineNumbers" aria-hidden="true">
                {lineNumbers.map((line) => <span key={line}>{line}</span>)}
              </div>
              <div className="codeSurface">
                <pre className="syntaxLayer" ref={syntaxRef} aria-hidden="true">
                  {code.split("\n").map((line, lineIndex) => (
                    <span className="codeLine" key={lineIndex}>
                      {highlightedLine(line || " ", language, lineIndex)}
                    </span>
                  ))}
                </pre>
                <textarea
                  ref={editorRef}
                  value={code}
                  onChange={handleCodeChange}
                  onKeyDown={handleCodeKeyDown}
                  onScroll={syncCodeScroll}
                  spellCheck={false}
                />
              </div>
            </div>
          </section>

          <section className="coachPane">
            <div className="paneHeader">
              <div><Bot size={18} /> Interviewer</div>
              <button onClick={askInterviewer}><Send size={16} /> Ask</button>
            </div>
            <div className="chatLog">
              {chat.map((line, index) => (
                <article key={`${line.actor}-${index}`} className={line.actor.toLowerCase()}>
                  <strong>{line.actor}</strong>
                  <p>{line.text}</p>
                </article>
              ))}
            </div>
            <div className="composer">
              <input
                value={candidateNote}
                onChange={(event) => setCandidateNote(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") sendCandidateNote();
                }}
                placeholder="Add candidate transcript note"
              />
              <button onClick={sendCandidateNote} aria-label="Send note"><Send size={17} /></button>
            </div>
          </section>

          <section className="insightsPane">
            <div className="hintBox">
              <div>
                <Lightbulb size={18} />
                <strong>Coding hint</strong>
              </div>
              <p>{hint}</p>
              <button onClick={requestHint}>Generate hint</button>
            </div>

            <div className="feedbackBox">
              <div className="paneHeader">
                <div><Activity size={18} /> Feedback</div>
                <button onClick={generateFeedback}>Generate</button>
              </div>
              {feedback ? (
                <div className="feedback">
                  <strong>{feedback.overall_score}%</strong>
                  <span>{feedback.recommendation.replace("_", " ")}</span>
                  <p>{feedback.strengths[0]}</p>
                  <p>{feedback.improvements[0]}</p>
                </div>
              ) : (
                <p className="muted">Generate structured feedback after the coding and discussion rounds.</p>
              )}
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
