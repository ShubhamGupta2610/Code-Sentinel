import { useState } from "react";

function AIReviewDemo() {
  const [result, setResult] = useState(null);

  const analyzePR = () => {
    setResult({
      issue: "SQL Injection",
      severity: "Critical",
      confidence: 96,
      fix: "Use parameterized queries."
    });
  };

  return (
    <div
      style={{
        background: "#0f172a",
        minHeight: "100vh",
        color: "white",
        padding: "30px"
      }}
    >
      <h1>AI Review Demo</h1>

      <div
        style={{
          background: "#1e293b",
          padding: "20px",
          borderRadius: "12px"
        }}
      >
        Pull Request:
        <br />
        Fix login validation bug
      </div>

      <button
        onClick={analyzePR}
        style={{
          marginTop: "20px",
          padding: "10px 20px"
        }}
      >
        Analyze
      </button>

      {result && (
        <div
          style={{
            background: "#1e293b",
            marginTop: "20px",
            padding: "20px",
            borderRadius: "12px"
          }}
        >
          <h2>{result.issue}</h2>

          <p>Severity: {result.severity}</p>

          <p>Confidence: {result.confidence}%</p>

          <p>Fix: {result.fix}</p>
        </div>
      )}
    </div>
  );
}

export default AIReviewDemo;