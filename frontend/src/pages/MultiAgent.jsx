function AgentBox({ title, description }) {
  return (
    <div
      style={{
        background: "#1e293b",
        color: "white",
        padding: "20px",
        borderRadius: "12px",
        width: "300px",
        textAlign: "center",
        margin: "0 auto"
      }}
    >
      <h2>{title}</h2>
      <p>{description}</p>
    </div>
  );
}

function MultiAgent() {
  return (
    <div
      style={{
        background: "#0f172a",
        minHeight: "100vh",
        padding: "30px"
      }}
    >
      <h1 style={{ color: "white" }}>
        Multi-Agent Review Pipeline
      </h1>

      <div style={{ marginTop: "40px" }}>

        <AgentBox
          title="Intent Agent"
          description="Understands PR purpose and GitHub issue."
        />

        <h1 style={{ color: "white", textAlign: "center" }}>↓</h1>

        <AgentBox
          title="Security Agent"
          description="Detects SQL Injection, XSS, SSRF and OWASP risks."
        />

        <h1 style={{ color: "white", textAlign: "center" }}>↓</h1>

        <AgentBox
          title="Code Quality Agent"
          description="Reviews maintainability and coding standards."
        />

        <h1 style={{ color: "white", textAlign: "center" }}>↓</h1>

        <AgentBox
          title="RAG Agent"
          description="Retrieves repository context for deeper analysis."
        />

        <h1 style={{ color: "white", textAlign: "center" }}>↓</h1>

        <AgentBox
          title="Review Aggregator"
          description="Combines findings and generates final report."
        />

      </div>
    </div>
  );
}

export default MultiAgent;