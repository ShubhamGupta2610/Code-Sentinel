function FindingDetails({ finding }) {
  if (!finding) return null;

  return (
    <div
      style={{
        background: "#1e293b",
        padding: "20px",
        borderRadius: "12px",
        color: "white",
        marginTop: "20px"
      }}
    >
      <h2>{finding.issue}</h2>

      <p>
        <strong>File:</strong> {finding.file}
      </p>

      <p>
        <strong>Severity:</strong> {finding.severity}
      </p>

      <p>
        <strong>Confidence:</strong> {finding.confidence}%
      </p>

      <p>
        <strong>Why AI Flagged It:</strong><br />
        {finding.reason}
      </p>

      <p>
        <strong>Risk:</strong><br />
        {finding.risk}
      </p>

      <p>
        <strong>Suggested Fix:</strong><br />
        {finding.fix}
      </p>
    </div>
  );
}

export default FindingDetails;