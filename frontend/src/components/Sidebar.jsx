import { Link } from "react-router-dom";

function Sidebar() {
  const linkStyle = {
    color: "white",
    textDecoration: "none",
    fontSize: "16px",
    display: "block",
    padding: "10px 0",
  };

  return (
    <div
      style={{
        width: "250px",
        minHeight: "100vh",
        background: "#111827",
        padding: "20px",
        borderRight: "1px solid #374151",
      }}
    >
      <h2
        style={{
          color: "#6366f1",
          marginBottom: "30px",
        }}
      >
        CodeSentinel
      </h2>

      <nav>
        <Link to="/" style={linkStyle}>
          📊 Dashboard
        </Link>

        <Link to="/rag" style={linkStyle}>
          🧠 RAG Visualization
        </Link>

        <Link to="/agents" style={linkStyle}>
          🤖 Multi-Agent View
        </Link>

        <Link to="/review" style={linkStyle}>
          🔍 AI Review Demo
        </Link>
      </nav>

      <div
        style={{
          marginTop: "40px",
          color: "#9CA3AF",
          fontSize: "14px",
        }}
      >
        <p>AI-Powered Code Review Platform</p>
      </div>
    </div>
  );
}

export default Sidebar;