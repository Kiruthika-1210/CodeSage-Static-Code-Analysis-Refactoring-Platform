import { useState, useEffect } from "react";

import CodeEditor from "../components/CodeEditor";
import IssueList from "../components/IssueList";
import ComplexityPanel from "../components/ComplexityPanel";
import ScorePanel from "../components/ScorePanel";
import RefactoredCode from "../components/RefactoredCode";
import ExplanationPanel from "../components/ExplanationPanel";
import VersionHistory from "../components/VersionHistory";

import {
  analyzeCode,
  refactorCode,
  analyzeAndRefactor,
} from "../utils/api";

function Home({ theme, setTheme }) {
  /* =======================
     CORE STATE
  ======================= */

  const [code, setCode] = useState("");

  const [issues, setIssues] = useState([]);
  const [activeFilter, setActiveFilter] = useState("all");

  const [complexity, setComplexity] = useState(null);

  const [scores, setScores] = useState({
    finalScore: null,
  });

  const [refactoredCode, setRefactoredCode] = useState("");
  const [explanation, setExplanation] = useState(null);

  const [versionHistory, setVersionHistory] = useState([]);

  /* =======================
     RESET ON EMPTY CODE
  ======================= */

  useEffect(() => {
    if (code.trim() === "") {
      setIssues([]);
      setComplexity(null);
      setScores({ finalScore: null });
      setRefactoredCode("");
      setExplanation(null);
    }
  }, [code]);

  /* =======================
     DERIVED STATE
  ======================= */

  const canSaveVersion =
    issues.length > 0 ||
    complexity !== null ||
    scores.finalScore !== null ||
    refactoredCode !== "";

  /* =======================
     HANDLERS
  ======================= */

  async function handleAnalyze() {
    const result = await analyzeCode(code);
    setIssues(result.issues);
    setComplexity(result.complexity);
    setScores({ finalScore: result.qualityScore });
  }

  async function handleRefactor() {
    const result = await refactorCode(code);
    setRefactoredCode(result.refactoredCode);
    setExplanation(result.explanation);
  }

  async function handleFullPipeline() {
    const result = await analyzeAndRefactor(code);

    setIssues(result.issues);
    setComplexity(result.complexity);
    setScores({ finalScore: result.qualityScore });
    setRefactoredCode(result.refactoredCode);
    setExplanation(result.explanation);

    // 🔥 Auto-save version
    const newVersion = {
      id: `v${versionHistory.length + 1}`,
      timestamp: new Date().toLocaleString(),
      code,
      issues: result.issues,
      complexity: {
        bigO: result.complexity.bigO,
        score: result.complexity.score,
      },
      score: { final: result.qualityScore },
      diff: "Auto-saved after Analyze + Refactor",
    };

    setVersionHistory((prev) => [...prev, newVersion]);
  }

  function handleSaveVersion() {
    const newVersion = {
      id: `v${versionHistory.length + 1}`,
      timestamp: new Date().toLocaleString(),
      code,
      issues,
      complexity,
      score:
        scores.finalScore !== null
          ? { final: scores.finalScore }
          : null,
      diff: "Manual snapshot saved",
    };

    setVersionHistory((prev) => [...prev, newVersion]);
  }

  /* =======================
     RENDER
  ======================= */

  return (
    <div className="min-h-screen bg-neutral-100 dark:bg-neutral-950
                    text-neutral-900 dark:text-neutral-100
                    transition-colors duration-300">
      <div className="mx-auto max-w-6xl px-6 py-8 space-y-8">

        {/* 🌗 THEME TOGGLE */}
        <div className="flex justify-end">
          <button
            onClick={() =>
              setTheme(theme === "dark" ? "light" : "dark")
            }
            className="px-3 py-1 rounded-lg text-sm font-medium
                       border border-neutral-700 dark:border-neutral-600
                       hover:bg-neutral-200 dark:hover:bg-neutral-800
                       transition"
          >
            {theme === "dark" ? "🌞 Light Mode" : "🌙 Dark Mode"}
          </button>
        </div>

        <CodeEditor
          code={code}
          onCodeChange={setCode}
          onAnalyze={handleAnalyze}
          onRefactor={handleRefactor}
          onFullPipeline={handleFullPipeline}
        />

        <IssueList
          issues={issues}
          activeFilter={activeFilter}
          setActiveFilter={setActiveFilter}
          onIssueClick={(line) => console.log("Jump to line:", line)}
        />

        {complexity && <ComplexityPanel data={complexity} />}

        {scores.finalScore !== null && <ScorePanel data={scores} />}

        {refactoredCode && (
          <RefactoredCode
            originalCode={code}
            refactoredCode={refactoredCode}
          />
        )}

        {explanation && <ExplanationPanel data={explanation} />}

        <VersionHistory
          versions={versionHistory}
          onSaveVersion={handleSaveVersion}
          canSave={canSaveVersion}
        />

      </div>
    </div>
  );
}

export default Home;
