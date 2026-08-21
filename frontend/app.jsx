import { useState } from "react";
import "./App.css";

const API_BASE = "http://127.0.0.1:8010";

function App() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const runRecommendation = async () => {
    if (!query.trim()) {
      setError("Enter a disease or condition first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(
        `${API_BASE}/recommend?q=${encodeURIComponent(query.trim())}`
      );

      if (!response.ok) {
        throw new Error("Recommendation API request failed.");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(
        "Could not connect to the Ayurveda API. Make sure the backend is running on port 8010."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter") {
      runRecommendation();
    }
  };

  const recommendations = result?.recommendations || [];
  const model = result?.model;

  return (
    <div className="app-shell">

      {/* SIDEBAR */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">🌿</div>
          <div>
            <h1>Ayurveda</h1>
            <span>Intelligence</span>
          </div>
        </div>

        <nav className="navigation">
          <button className="nav-item active">
            <span>▣</span>
            Dashboard
          </button>

          <button className="nav-item">
            <span>✦</span>
            Recommendations
          </button>

          <button className="nav-item">
            <span>◉</span>
            Diseases
          </button>

          <button className="nav-item">
            <span>♧</span>
            Formulations
          </button>

          <button className="nav-item">
            <span>◈</span>
            Model Performance
          </button>
        </nav>

        <div className="sidebar-bottom">
          <div className="system-status">
            <span className="status-dot"></span>
            <div>
              <strong>Model Online</strong>
              <small>final_top5_v2</small>
            </div>
          </div>
        </div>
      </aside>

      {/* MAIN */}
      <main className="main-content">

        {/* TOP BAR */}
        <header className="topbar">
          <div>
            <p className="eyebrow">AYURVEDIC DECISION SUPPORT</p>
            <h2>Formulation Intelligence Dashboard</h2>
          </div>

          <div className="topbar-status">
            <span className="status-dot"></span>
            System Ready
          </div>
        </header>

        {/* KPI CARDS */}
        <section className="metrics-grid">

          <div className="metric-card">
            <div className="metric-icon">◉</div>
            <div>
              <span>Knowledge Profiles</span>
              <strong>{model?.profiles || 48}</strong>
              <small>Available formulation profiles</small>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">✦</div>
            <div>
              <span>Recommendation Depth</span>
              <strong>TOP-5</strong>
              <small>Ranked formulation candidates</small>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">◎</div>
            <div>
              <span>Top-5 Accuracy</span>
              <strong>
                {model?.metrics?.exact_top5_accuracy
                  ? `${model.metrics.exact_top5_accuracy.toFixed(1)}%`
                  : "56.7%"}
              </strong>
              <small>Validation performance</small>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">♧</div>
            <div>
              <span>Ingredient Match</span>
              <strong>
                {model?.metrics?.ingredient_match_50
                  ? `${model.metrics.ingredient_match_50.toFixed(1)}%`
                  : "93.3%"}
              </strong>
              <small>50% ingredient overlap</small>
            </div>
          </div>

        </section>

        {/* SEARCH PANEL */}
        <section className="search-panel">
          <div className="section-heading">
            <div>
              <p className="eyebrow">INTELLIGENCE ENGINE</p>
              <h3>Run Formulation Recommendation</h3>
              <p>
                Enter a disease or condition to retrieve the trained model's
                Top-5 formulation candidates.
              </p>
            </div>
          </div>

          <div className="search-row">
            <div className="search-input-wrapper">
              <span>⌕</span>
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="e.g. hypertension, fever..."
              />
            </div>

            <button
              className="primary-button"
              onClick={runRecommendation}
              disabled={loading}
            >
              {loading ? "Analyzing..." : "Run Recommendation"}
            </button>
          </div>

          {error && <div className="error-message">{error}</div>}
        </section>

        {/* RESULT AREA */}
        {result && (
          <section className="results-section">

            <div className="result-header">
              <div>
                <p className="eyebrow">MODEL OUTPUT</p>

                <h3>
                  {result.query}
                </h3>

                <p>
                  Resolved condition:{" "}
                  <strong>
                    {result.normalized_term || "Unknown"}
                  </strong>
                </p>
              </div>

              <div className={`result-badge ${result.status}`}>
                {result.status}
              </div>
            </div>

            {recommendations.length > 0 ? (
              <div className="recommendation-list">

                {recommendations.map((item) => {

                  const percentage = Math.min(
                    Math.max(item.score * 100, 0),
                    100
                  );

                  return (
                    <div
                      className="recommendation-card"
                      key={item.rank}
                    >

                      <div className="rank-box">
                        #{item.rank}
                      </div>

                      <div className="recommendation-content">

                        <div className="recommendation-title-row">
                          <div>
                            <span className="recommendation-label">
                              FORMULATION
                            </span>

                            <h4>{item.formulation}</h4>
                          </div>

                          <strong className="score">
                            {percentage.toFixed(1)}%
                          </strong>
                        </div>

                        <div className="score-track">
                          <div
                            className="score-fill"
                            style={{
                              width: `${percentage}%`,
                            }}
                          />
                        </div>

                        <div className="signal-grid">

                          <div>
                            <span>Disease Match</span>
                            <strong>
                              {(
                                item.disease_match * 100
                              ).toFixed(0)}
                              %
                            </strong>
                          </div>

                          <div>
                            <span>Disease Similarity</span>
                            <strong>
                              {(
                                item.disease_similarity * 100
                              ).toFixed(1)}
                              %
                            </strong>
                          </div>

                          <div>
                            <span>Profile Similarity</span>
                            <strong>
                              {(
                                item.profile_similarity * 100
                              ).toFixed(1)}
                              %
                            </strong>
                          </div>

                          <div>
                            <span>Ingredient Similarity</span>
                            <strong>
                              {(
                                item.ingredient_similarity * 100
                              ).toFixed(1)}
                              %
                            </strong>
                          </div>

                        </div>

                      </div>

                    </div>
                  );
                })}

              </div>
            ) : (
              <div className="empty-result">
                <div>⌕</div>
                <h4>No formulation candidates returned</h4>
                <p>
                  The model did not return any recommendations for this query.
                </p>
              </div>
            )}

          </section>
        )}

        {/* MODEL PERFORMANCE */}
        <section className="performance-panel">

          <div>
            <p className="eyebrow">MODEL INFORMATION</p>
            <h3>Trained Recommendation Engine</h3>
          </div>

          <div className="performance-grid">

            <div>
              <span>Model Version</span>
              <strong>
                {model?.version || "final_top5_v2"}
              </strong>
            </div>

            <div>
              <span>Profiles</span>
              <strong>
                {model?.profiles || 48}
              </strong>
            </div>

            <div>
              <span>Ingredient Match @50</span>
              <strong>
                {model?.metrics?.ingredient_match_50
                  ? `${model.metrics.ingredient_match_50.toFixed(1)}%`
                  : "93.3%"}
              </strong>
            </div>

            <div>
              <span>Ingredient Match @75</span>
              <strong>
                {model?.metrics?.ingredient_match_75
                  ? `${model.metrics.ingredient_match_75.toFixed(1)}%`
                  : "70.0%"}
              </strong>
            </div>

          </div>

        </section>

        <footer>
          Ayurveda Intelligence · Evidence-aware formulation discovery
        </footer>

      </main>
    </div>
  );
}

export default App;
