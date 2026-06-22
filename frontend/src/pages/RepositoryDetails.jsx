function RepositoryDetails() {
  return (
    <div
      style={{
        background: "#0f172a",
        minHeight: "100vh",
        padding: "30px",
        color: "white"
      }}
    >
      <h1>E-Commerce API</h1>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4,1fr)",
          gap: "20px",
          marginTop: "20px"
        }}
      >
        <div>Health Score: A</div>
        <div>PR Reviewed: 42</div>
        <div>Issues Found: 18</div>
        <div>Critical Issues: 2</div>
      </div>

      <div style={{ marginTop: "30px" }}>
        <h2>Recent Findings</h2>

        <ul>
          <li>auth.py - SQL Injection</li>
          <li>login.py - XSS</li>
          <li>admin.py - Broken Authentication</li>
        </ul>
      </div>
    </div>
  );
}

export default RepositoryDetails;