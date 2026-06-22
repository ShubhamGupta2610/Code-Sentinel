import { useEffect, useState } from "react";
import api from "../services/api";
import FindingDetails from "./FindingDetails";

function FindingsTable() {
  const [reviews, setReviews] = useState([]);
  const [selectedFinding, setSelectedFinding] = useState(null);

  useEffect(() => {
    const fetchReviews = async () => {
      try {
        const response = await api.get("/reviews");
        setReviews(response.data.data);
      } catch (error) {
        console.error("Error fetching reviews:", error);
      }
    };

    fetchReviews();
  }, []);

  return (
    <>
      <div
        style={{
          background: "#1e293b",
          padding: "20px",
          borderRadius: "12px",
          color: "white",
        }}
      >
        <h2>Recent AI Reviews</h2>

        <table
          style={{
            width: "100%",
            marginTop: "20px",
            borderCollapse: "collapse",
          }}
        >
          <thead>
            <tr>
              <th align="left">PR Title</th>
              <th align="left">Status</th>
              <th align="left">PR Number</th>
              <th align="left">Findings</th>
            </tr>
          </thead>

          <tbody>
            {reviews.map((review) => (
              <tr
                key={review.id}
                style={{
                  cursor: "pointer",
                  borderTop: "1px solid #374151",
                }}
                onClick={() => setSelectedFinding(review)}
              >
                <td>{review.pr_title}</td>
                <td>{review.status}</td>
                <td>{review.pr_number}</td>
                <td>{review.findings.length}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedFinding && (
        <FindingDetails
          finding={{
            file: selectedFinding.pr_title,
            issue: selectedFinding.status,
            severity: selectedFinding.grade || "N/A",
            confidence: selectedFinding.score || 0,
            reason:
              selectedFinding.reasoning_summary ||
              "No reasoning available.",
            risk: "Review generated from repository analysis.",
            fix:
              selectedFinding.intent_summary ||
              "No suggested fix available.",
          }}
        />
      )}
    </>
  );
}

export default FindingsTable;