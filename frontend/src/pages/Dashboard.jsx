import { useEffect, useState } from "react";

import StatCard from "../components/StatCard";
import VulnerabilityChart from "../components/VulnerabilityChart";
import HealthChart from "../components/HealthChart";
import FindingsTable from "../components/FindingsTable";

import api from "../services/api";

function Dashboard() {

  const [stats, setStats] = useState({
    total_reviews: 0,
    total_findings: 0,
    active_repos: 0,
    avg_score: 0,
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get("/stats/summary");
        setStats(response.data.data);
      } catch (error) {
        console.error("Error fetching stats:", error);
      }
    };

    fetchStats();
  }, []);

  return (
    <div
      style={{
        background: "#0f172a",
        minHeight: "100vh",
        padding: "30px",
        color: "white",
      }}
    >
      <h1>CodeSentinel Dashboard</h1>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4,1fr)",
          gap: "20px",
          marginTop: "30px",
        }}
      >
        <StatCard
          title="Repositories"
          value={stats.active_repos}
        />

        <StatCard
          title="PR Reviews"
          value={stats.total_reviews}
        />

        <StatCard
          title="Findings"
          value={stats.total_findings}
        />

        <StatCard
          title="Avg Score"
          value={Math.round(stats.avg_score)}
        />
      </div>

      <div style={{ marginTop: "40px" }}>
        <VulnerabilityChart />
      </div>

      <div style={{ marginTop: "30px" }}>
        <HealthChart />
      </div>

      <div style={{ marginTop: "30px" }}>
        <FindingsTable />
      </div>
    </div>
  );
}

export default Dashboard;