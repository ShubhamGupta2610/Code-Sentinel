function RAGVisualization() {
  return (
    <div
      style={{
        color: "white",
        padding: "30px",
      }}
    >
      <h1>RAG Visualization Page</h1>

      <div
        style={{
          background: "#1e293b",
          padding: "20px",
          borderRadius: "12px",
          marginTop: "20px",
        }}
      >
        <h2>GitHub Issue</h2>
        <p>Add premium discount for users</p>
      </div>

      <div
        style={{
          background: "#1e293b",
          padding: "20px",
          borderRadius: "12px",
          marginTop: "20px",
        }}
      >
        <h2>Retrieved Context</h2>
        <p>premium_user.py</p>
        <p>discount_engine.py</p>
      </div>

      <div
        style={{
          background: "#1e293b",
          padding: "20px",
          borderRadius: "12px",
          marginTop: "20px",
        }}
      >
        <h2>Prompt Sent To LLM</h2>
        <p>
          Review this code change against the retrieved repository context.
        </p>
      </div>

      <div
        style={{
          background: "#1e293b",
          padding: "20px",
          borderRadius: "12px",
          marginTop: "20px",
        }}
      >
        <h2>AI Analysis</h2>
        <p>Potential business logic mismatch detected.</p>
      </div>

      <div
        style={{
          background: "#1e293b",
          padding: "20px",
          borderRadius: "12px",
          marginTop: "20px",
        }}
      >
        <h2>Final Finding</h2>
        <p>Premium users receive 0% discount instead of 10%.</p>
      </div>
    </div>
  );
}

export default RAGVisualization;