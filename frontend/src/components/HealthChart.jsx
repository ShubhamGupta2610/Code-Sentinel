import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer
} from "recharts";

import { healthData } from "../data/mockData";

function HealthChart() {
  return (
    <div
      style={{
        background: "#1e293b",
        padding: "20px",
        borderRadius: "12px"
      }}
    >
      <h2>Repository Health Score</h2>

      <ResponsiveContainer
        width="100%"
        height={300}
      >
        <BarChart data={healthData}>
          <XAxis dataKey="metric" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="score" fill="#6366f1" />
          </BarChart>
         </ResponsiveContainer>
    </div>
  );
}

export default HealthChart;