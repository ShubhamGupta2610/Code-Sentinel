import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import RAGVisualization from "./pages/RAGVisualization";
import MultiAgent from "./pages/MultiAgent";
import AIReviewDemo from "./pages/AIReviewDemo";

import Sidebar from "./components/Sidebar";

function App() {
  return (
    <BrowserRouter>
      <div style={{ display: "flex" }}>
        <Sidebar />

        <div style={{ flex: 1 }}>
          <Routes>
            <Route
              path="/"
              element={<Dashboard />}
            />

            <Route
              path="/rag"
              element={<RAGVisualization />}
            />

            <Route
              path="/agents"
              element={<MultiAgent />}
            />

            <Route
              path="/review"
              element={<AIReviewDemo />}
            />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;