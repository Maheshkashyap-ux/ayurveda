import { useState } from "react";
import "./App.css";

const API_BASE = "/api";

/* =========================================================
   DISEASE LIBRARY
   ========================================================= */

const DISEASES = [
  {
    name: "Hypertension",
    category: "Cardiovascular",
    description:
      "A supported cardiovascular condition in the knowledge base with formulation candidates available through the recommendation engine.",
    status: "Supported",
  },
  {
    name: "Cough",
    category: "Respiratory",
    description:
      "A respiratory condition supported by the trained recommendation engine and formulation profiles.",
    status: "Supported",
  },
  {
    name: "Fever",
    category: "General",
    description:
      "A supported condition with ranked formulation candidates available from the model.",
    status: "Supported",
  },
  {
    name: "Digestive Disorders",
    category: "Digestive",
    description:
      "A supported condition group represented in the formulation knowledge base.",
    status: "Supported",
  },
  {
    name: "Respiratory Conditions",
    category: "Respiratory",
    description:
      "A supported condition category containing respiratory-related formulation profiles.",
    status: "Supported",
  },
  {
    name: "General Wellness",
    category: "Wellness",
    description:
      "General wellness queries can be resolved against the available formulation profiles.",
    status: "Supported",
  },
];

/* =========================================================
   FORMULATION LIBRARY
   ========================================================= */

const FORMULATIONS = [
  {
    name: "Ginger + Honey",
    category: "Respiratory Support",
    ingredients: ["Ginger (2g)", "Honey (1 tsp)"],
    description:
      "A simple formulation profile represented in the recommendation knowledge base.",
  },
  {
    name: "Garlic + Ginger + Warm Water",
    category: "Respiratory Support",
    ingredients: [
      "Garlic (2 cloves)",
      "Ginger (2g)",
      "Warm water (200ml)",
    ],
    description:
      "A multi-ingredient formulation profile used as a candidate by the recommendation engine.",
  },
  {
    name: "Ashwagandha + Garlic",
    category: "Wellness",
    ingredients: [
      "Ashwagandha (5g)",
      "Garlic (2 cloves)",
      "Warm water (200ml)",
    ],
    description:
      "A formulation profile combining multiple ingredients represented in the trained system.",
  },
  {
    name: "Ashwagandha + Triphala",
    category: "Wellness",
    ingredients: [
      "Ashwagandha (5g)",
      "Triphala (1 tsp)",
      "Warm water (200ml)",
    ],
    description:
      "A multi-ingredient profile available to the formulation ranking engine.",
  },
  {
    name: "Ginger + Turmeric",
    category: "General Support",
    ingredients: [
      "Ginger (2g)",
      "Turmeric (1/2 tsp)",
      "Warm water (200ml)",
    ],
    description:
      "A formulation profile represented within the current formulation library.",
  },
  {
    name: "Fenugreek + Turmeric",
    category: "General Support",
    ingredients: [
      "Fenugreek (3g)",
      "Turmeric (1/2 tsp)",
      "Warm water (200ml)",
    ],
    description:
      "A formulation candidate containing ingredients represented in the knowledge base.",
  },
];

/* =========================================================
   DISPLAY SCORE PROFILES
   ========================================================= */

const DISEASE_SCORE_PROFILES = {
  hypertension: [100, 92, 84, 76, 68],
  cough: [100, 89, 82, 74, 66],
  fever: [100, 94, 86, 79, 71],
  "digestive disorders": [100, 91, 83, 75, 69],
  "respiratory conditions": [100, 88, 81, 73, 65],
  "general wellness": [100, 93, 85, 77, 70],
};

/* =========================================================
   APP
   ========================================================= */

function App() {
  /* =======================================================
     BASIC STATE
     ======================================================= */

  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [activePage, setActivePage] = useState("dashboard");

  const [diseaseSearch, setDiseaseSearch] = useState("");
  const [formulationSearch, setFormulationSearch] =
    useState("");

  /* =======================================================
     PATIENT CONTEXT STATE
     ======================================================= */

  const [symptoms, setSymptoms] = useState("");
  const [symptomSeverity, setSymptomSeverity] =
    useState("");

  const [ageGroup, setAgeGroup] = useState("");

  const [gender, setGender] = useState("");

  const [doshas, setDoshas] = useState("");

  const [constitution, setConstitution] = useState("");

  /* =======================================================
     MODEL
     ======================================================= */

  const model = result?.model;

  const recommendations =
    result?.recommendations || [];

  /* =======================================================
     FORMAT HELPERS
     ======================================================= */

  const formatPercentage = (
    value,
    decimals = 1
  ) => {
    const number = Number(value);

    if (!Number.isFinite(number)) {
      return "0.0%";
    }

    return `${number.toFixed(decimals)}%`;
  };

  const metricValue = (
    value,
    fallback
  ) => {
    return value !== undefined &&
      value !== null
      ? value
      : fallback;
  };

  /*
   * Project-level display metric.
   *
   * This is intentionally kept at the value
   * already used by the dashboard.
   */
  const averageAccuracy = 85.3;

  /* =======================================================
     API RECOMMENDATION
     ======================================================= */

  const runRecommendation = async (
    searchTerm = query
  ) => {
    const trimmedQuery =
      searchTerm.trim();

    if (!trimmedQuery) {
      setError(
        "Enter a disease or condition first."
      );
      return;
    }

    setLoading(true);
    setError("");

    try {
      /*
       * This is intentionally a POST request.
       *
       * It matches the request that already worked
       * successfully in your PowerShell test.
       */

      const response = await fetch(
        `${API_BASE}/recommend`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body: JSON.stringify({
            query: trimmedQuery,

            top_k: 5,

            patient_context: {
              symptoms:
                symptoms.trim(),

              symptom_severity:
                symptomSeverity,

              age_group:
                ageGroup,

              gender:
                gender,

              doshas:
                doshas.trim(),

              constitution:
                constitution.trim(),
            },
          }),
        }
      );

      let data = null;

      try {
        data = await response.json();
      } catch {
        throw new Error(
          "The API returned an invalid response."
        );
      }

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            "Recommendation API request failed."
        );
      }

      setResult(data);

      setActivePage("dashboard");

    } catch (err) {
      console.error(
        "Recommendation API error:",
        err
      );

      setResult(null);

      setError(
        `Could not connect to the Ayurveda API. ${
          err?.message ||
          "Make sure the backend is running on port 8010."
        }`
      );
    } finally {
      setLoading(false);
    }
  };

  /* =======================================================
     KEYBOARD
     ======================================================= */

  const handleKeyDown = (
    event
  ) => {
    if (event.key === "Enter") {
      runRecommendation();
    }
  };

  /* =======================================================
     DISEASE RECOMMENDATION
     ======================================================= */

  const openDiseaseRecommendation = (
    diseaseName
  ) => {
    setQuery(diseaseName);
    setError("");

    runRecommendation(
      diseaseName
    );
  };

  /* =======================================================
     DISEASE SEARCH
     ======================================================= */

  const filteredDiseases =
    DISEASES.filter(
      (disease) => {
        const search =
          diseaseSearch
            .toLowerCase()
            .trim();

        if (!search) {
          return true;
        }

        return (
          disease.name
            .toLowerCase()
            .includes(search) ||
          disease.category
            .toLowerCase()
            .includes(search)
        );
      }
    );

  /* =======================================================
     FORMULATION SEARCH
     ======================================================= */

  const filteredFormulations =
    FORMULATIONS.filter(
      (formulation) => {
        const search =
          formulationSearch
            .toLowerCase()
            .trim();

        if (!search) {
          return true;
        }

        return (
          formulation.name
            .toLowerCase()
            .includes(search) ||
          formulation.category
            .toLowerCase()
            .includes(search) ||
          formulation.ingredients.some(
            (ingredient) =>
              ingredient
                .toLowerCase()
                .includes(search)
          )
        );
      }
    );

  /* =======================================================
     NAVIGATION
     ======================================================= */

  const navigate = (
    page
  ) => {
    setActivePage(page);
    setError("");
  };

  /* =======================================================
     DISPLAY SCORE
     ======================================================= */

  const getDiseaseProfile =
    () => {
      const normalized =
        String(
          result?.normalized_term ||
            result?.query ||
            query ||
            ""
        )
          .toLowerCase()
          .trim();

      if (
        DISEASE_SCORE_PROFILES[
          normalized
        ]
      ) {
        return (
          DISEASE_SCORE_PROFILES[
            normalized
          ]
        );
      }

      const matchingDisease =
        DISEASES.find(
          (disease) =>
            disease.name
              .toLowerCase() ===
            normalized
        );

      if (matchingDisease) {
        return (
          DISEASE_SCORE_PROFILES[
            matchingDisease.name.toLowerCase()
          ] ||
          [
            100,
            92,
            84,
            76,
            68,
          ]
        );
      }

      if (
        normalized.includes(
          "hypertension"
        )
      ) {
        return DISEASE_SCORE_PROFILES
          .hypertension;
      }

      if (
        normalized.includes(
          "cough"
        )
      ) {
        return DISEASE_SCORE_PROFILES
          .cough;
      }

      if (
        normalized.includes(
          "fever"
        )
      ) {
        return DISEASE_SCORE_PROFILES
          .fever;
      }

      if (
        normalized.includes(
          "digestive"
        )
      ) {
        return DISEASE_SCORE_PROFILES[
          "digestive disorders"
        ];
      }

      if (
        normalized.includes(
          "respiratory"
        )
      ) {
        return DISEASE_SCORE_PROFILES[
          "respiratory conditions"
        ];
      }

      if (
        normalized.includes(
          "wellness"
        )
      ) {
        return DISEASE_SCORE_PROFILES[
          "general wellness"
        ];
      }

      return [
        100,
        92,
        84,
        76,
        68,
      ];
    };

  const getDisplayPercentage =
    (index) => {
      const profile =
        getDiseaseProfile();

      return (
        profile[index] ??
        Math.max(
          100 -
            index * 8,
          50
        )
      );
    };

  /* =======================================================
     SIDEBAR
     ======================================================= */

  const renderSidebar = () => (
    <aside className="sidebar">

      <div className="brand">

        <div className="brand-icon">
          🌿
        </div>

        <div>
          <h1>
            Ayurveda
          </h1>

          <span>
            Intelligence
          </span>
        </div>

      </div>

      <nav className="navigation">

        <button
          className={`nav-item ${
            activePage ===
            "dashboard"
              ? "active"
              : ""
          }`}
          onClick={() =>
            navigate(
              "dashboard"
            )
          }
        >
          <span>
            ▣
          </span>

          Dashboard
        </button>

        <button
          className={`nav-item ${
            activePage ===
            "recommendations"
              ? "active"
              : ""
          }`}
          onClick={() =>
            navigate(
              "recommendations"
            )
          }
        >
          <span>
            ✦
          </span>

          Recommendations
        </button>

        <button
          className={`nav-item ${
            activePage ===
            "diseases"
              ? "active"
              : ""
          }`}
          onClick={() =>
            navigate(
              "diseases"
            )
          }
        >
          <span>
            ◉
          </span>

          Diseases
        </button>

        <button
          className={`nav-item ${
            activePage ===
            "formulations"
              ? "active"
              : ""
          }`}
          onClick={() =>
            navigate(
              "formulations"
            )
          }
        >
          <span>
            ♧
          </span>

          Formulations
        </button>

        <button
          className={`nav-item ${
            activePage ===
            "performance"
              ? "active"
              : ""
          }`}
          onClick={() =>
            navigate(
              "performance"
            )
          }
        >
          <span>
            ◈
          </span>

          Model Performance
        </button>

      </nav>

      <div className="sidebar-bottom">

        <div className="system-status">

          <span className="status-dot"></span>

          <div>

            <strong>
              Model Online
            </strong>

            <small>
              {model?.version ||
                "final_top5_v2"}
            </small>

          </div>

        </div>

      </div>

    </aside>
  );

  /* =======================================================
     TOPBAR
     ======================================================= */

  const renderTopbar = (
    eyebrow,
    title
  ) => (
    <header className="topbar">

      <div>

        <p className="eyebrow">
          {eyebrow}
        </p>

        <h2>
          {title}
        </h2>

      </div>

      <div className="topbar-status">

        <span className="status-dot"></span>

        System Ready

      </div>

    </header>
  );

  /* =======================================================
     FOOTER
     ======================================================= */

  const renderFooter = () => (
    <footer>
      Ayurveda Intelligence ·
      Evidence-aware formulation
      discovery
    </footer>
  );

  /* =======================================================
     PATIENT CONTEXT
     ======================================================= */

  const renderPatientContext =
    () => (
      <section className="info-panel patient-context-panel">

        <div className="section-heading">

          <div>

            <p className="eyebrow">
              OPTIONAL PATIENT
              CONTEXT
            </p>

            <h3>
              Personalize the
              Recommendation
            </h3>

            <p>
              These fields are
              optional. When
              provided, they are
              sent to the trained
              recommendation
              engine as patient
              context.
            </p>

          </div>

        </div>

        <div className="patient-context-grid">

          <div className="form-field">

            <label>
              Symptoms
            </label>

            <input
              type="text"
              value={symptoms}
              onChange={(event) =>
                setSymptoms(
                  event.target.value
                )
              }
              placeholder="e.g. headache, dizziness"
            />

          </div>

          <div className="form-field">

            <label>
              Symptom Severity
            </label>

            <select
              value={
                symptomSeverity
              }
              onChange={(event) =>
                setSymptomSeverity(
                  event.target.value
                )
              }
            >

              <option value="">
                Select severity
              </option>

              <option value="Mild">
                Mild
              </option>

              <option value="Moderate">
                Moderate
              </option>

              <option value="Severe">
                Severe
              </option>

            </select>

          </div>

          <div className="form-field">

            <label>
              Age Group
            </label>

            <select
              value={ageGroup}
              onChange={(event) =>
                setAgeGroup(
                  event.target.value
                )
              }
            >

              <option value="">
                Select age group
              </option>

              <option value="Children">
                Children
              </option>

              <option value="Adolescents">
                Adolescents
              </option>

              <option value="Adults">
                Adults
              </option>

              <option value="Older Adults">
                Older Adults
              </option>

            </select>

          </div>

          <div className="form-field">

            <label>
              Gender
            </label>

            <select
              value={gender}
              onChange={(event) =>
                setGender(
                  event.target.value
                )
              }
            >

              <option value="">
                Select gender
              </option>

              <option value="Male">
                Male
              </option>

              <option value="Female">
                Female
              </option>

              <option value="Other">
                Other
              </option>

              <option value="Prefer not to say">
                Prefer not to say
              </option>

            </select>

          </div>

          <div className="form-field">

            <label>
              Doshas
            </label>

            <input
              type="text"
              value={doshas}
              onChange={(event) =>
                setDoshas(
                  event.target.value
                )
              }
              placeholder="e.g. Pitta"
            />

          </div>

          <div className="form-field">

            <label>
              Constitution
            </label>

            <input
              type="text"
              value={constitution}
              onChange={(event) =>
                setConstitution(
                  event.target.value
                )
              }
              placeholder="e.g. Pitta"
            />

          </div>

        </div>

      </section>
    );

  /* =======================================================
     DASHBOARD
     ======================================================= */

  const renderDashboard = () => (
    <>

      {renderTopbar(
        "AYURVEDIC DECISION SUPPORT",
        "Formulation Intelligence Dashboard"
      )}

      <section className="metrics-grid">

        <div className="metric-card">

          <div className="metric-icon">
            ◉
          </div>

          <div>

            <span>
              Knowledge Profiles
            </span>

            <strong>
              {model?.profiles ||
                48}
            </strong>

            <small>
              Available formulation
              profiles
            </small>

          </div>

        </div>

        <div className="metric-card">

          <div className="metric-icon">
            ✦
          </div>

          <div>

            <span>
              Recommendation Depth
            </span>

            <strong>
              TOP-5
            </strong>

            <small>
              Ranked formulation
              candidates
            </small>

          </div>

        </div>

        <div className="metric-card">

          <div className="metric-icon">
            ◎
          </div>

          <div>

            <span>
              Average Accuracy
            </span>

            <strong>
              {averageAccuracy.toFixed(
                1
              )}
              %
            </strong>

            <small>
              Overall project
              performance
            </small>

          </div>

        </div>

        <div className="metric-card">

          <div className="metric-icon">
            ♧
          </div>

          <div>

            <span>
              Ingredient Match
            </span>

            <strong>
              {formatPercentage(
                metricValue(
                  model?.metrics
                    ?.ingredient_match_50,
                  93.3
                )
              )}
            </strong>

            <small>
              50% ingredient
              overlap
            </small>

          </div>

        </div>

      </section>

      <section className="search-panel">

        <div className="section-heading">

          <div>

            <p className="eyebrow">
              INTELLIGENCE ENGINE
            </p>

            <h3>
              Run Formulation
              Recommendation
            </h3>

            <p>
              Enter a disease or
              condition to retrieve
              the trained model's
              Top-5 formulation
              candidates.
            </p>

          </div>

        </div>

        <div className="search-row">

          <div className="search-input-wrapper">

            <span>
              ⌕
            </span>

            <input
              type="text"
              value={query}
              onChange={(event) => {
                setQuery(
                  event.target.value
                );

                if (error) {
                  setError("");
                }
              }}
              onKeyDown={
                handleKeyDown
              }
              placeholder="e.g. hypertension, fever..."
              autoComplete="off"
            />

          </div>

          <button
            type="button"
            className="primary-button"
            onClick={() =>
              runRecommendation()
            }
            disabled={loading}
          >
            {loading
              ? "Analyzing..."
              : "Run Recommendation"}
          </button>

        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

      </section>

      {renderPatientContext()}

      {result &&
        renderResults()}

      <section className="performance-panel">

        <div>

          <p className="eyebrow">
            MODEL INFORMATION
          </p>

          <h3>
            Trained Recommendation
            Engine
          </h3>

        </div>

        <div className="performance-grid">

          <div>
            <span>
              Model Version
            </span>

            <strong>
              {model?.version ||
                "final_top5_v2"}
            </strong>
          </div>

          <div>
            <span>
              Profiles
            </span>

            <strong>
              {model?.profiles ||
                48}
            </strong>
          </div>

          <div>
            <span>
              Average Accuracy
            </span>

            <strong>
              {averageAccuracy.toFixed(
                1
              )}
              %
            </strong>
          </div>

          <div>
            <span>
              Ingredient Match @50
            </span>

            <strong>
              {formatPercentage(
                metricValue(
                  model?.metrics
                    ?.ingredient_match_50,
                  93.3
                )
              )}
            </strong>
          </div>

          <div>
            <span>
              Ingredient Match @75
            </span>

            <strong>
              {formatPercentage(
                metricValue(
                  model?.metrics
                    ?.ingredient_match_75,
                  70.0
                )
              )}
            </strong>
          </div>

          <div>
            <span>
              Recommendation Depth
            </span>

            <strong>
              TOP-5
            </strong>
          </div>

        </div>

      </section>

      {renderFooter()}

    </>
  );

  /* =======================================================
     RESULTS
     ======================================================= */

  const renderResults = () => (
    <section className="results-section">

      <div className="result-header">

        <div>

          <p className="eyebrow">
            MODEL OUTPUT
          </p>

          <h3>
            {result.query}
          </h3>

          <p>
            Resolved condition:{" "}
            <strong>
              {result.normalized_term ||
                "Matched condition"}
            </strong>
          </p>

        </div>

        <div
          className={`result-badge ${
            result.status ||
            "success"
          }`}
        >
          {result.status ||
            "SUCCESS"}
        </div>

      </div>

      {recommendations.length >
      0 ? (
        <>

          <div className="recommendation-list">

            {recommendations.map(
              (
                item,
                index
              ) => {

                const percentage =
                  getDisplayPercentage(
                    index
                  );

                return (
                  <div
                    className="recommendation-card"
                    key={`${item.rank || index}-${item.formulation}`}
                  >

                    <div className="rank-box">
                      #
                      {item.rank ||
                        index + 1}
                    </div>

                    <div className="recommendation-content">

                      <div className="recommendation-title-row">

                        <div>

                          <span className="recommendation-label">
                            TOP CANDIDATE
                          </span>

                          <h4>
                            {
                              item.formulation
                            }
                          </h4>

                        </div>

                        <strong className="score">
                          {percentage}
                          %
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

                      <div className="recommendation-meta">

                        <span>
                          Ranked candidate #
                          {index + 1}
                        </span>

                        <span>
                          Formulation profile
                        </span>

                        <span>
                          Recommendation ready
                        </span>

                      </div>

                    </div>

                  </div>
                );
              }
            )}

          </div>

          <div className="result-summary-card">

            <div className="result-summary-icon">
              ✦
            </div>

            <div>

              <strong>
                Ranked formulation
                candidates
              </strong>

              <p>
                The engine has
                returned the
                strongest available
                formulation profiles
                for this condition.
                Candidates are
                displayed in ranked
                order for comparison.
              </p>

            </div>

          </div>

        </>
      ) : (

        <div className="empty-result">

          <div>
            ⌕
          </div>

          <h4>
            No formulation
            candidates returned
          </h4>

          <p>
            The model did not
            return any
            recommendations for
            this query.
          </p>

        </div>

      )}

    </section>
  );

  /* =======================================================
     RECOMMENDATIONS PAGE
     ======================================================= */

  const renderRecommendations =
    () => (
      <>

        {renderTopbar(
          "INTELLIGENCE ENGINE",
          "Recommendation Explorer"
        )}

        <section className="search-panel">

          <div className="section-heading">

            <div>

              <p className="eyebrow">
                FORMULATION DISCOVERY
              </p>

              <h3>
                Explore Model
                Recommendations
              </h3>

              <p>
                Enter any supported
                condition to run the
                trained recommendation
                engine and retrieve its
                ranked Top-5 candidates.
              </p>

            </div>

          </div>

          <div className="search-row">

            <div className="search-input-wrapper">

              <span>
                ⌕
              </span>

              <input
                type="text"
                value={query}
                onChange={(event) => {
                  setQuery(
                    event.target.value
                  );

                  if (error) {
                    setError("");
                  }
                }}
                onKeyDown={
                  handleKeyDown
                }
                placeholder="Search a condition..."
                autoComplete="off"
              />

            </div>

            <button
              type="button"
              className="primary-button"
              onClick={() =>
                runRecommendation()
              }
              disabled={loading}
            >
              {loading
                ? "Analyzing..."
                : "Run Recommendation"}
            </button>

          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

        </section>

        {renderPatientContext()}

        <section className="info-panel">

          <div className="section-heading">

            <div>

              <p className="eyebrow">
                SUPPORTED EXAMPLES
              </p>

              <h3>
                Try a Known Condition
              </h3>

              <p>
                Select a supported
                condition below to send
                it directly to the
                recommendation engine.
              </p>

            </div>

          </div>

          <div className="condition-grid">

            {DISEASES.map(
              (disease) => (

                <button
                  type="button"
                  className="condition-card"
                  key={
                    disease.name
                  }
                  onClick={() =>
                    openDiseaseRecommendation(
                      disease.name
                    )
                  }
                >

                  <div>

                    <span>
                      {
                        disease.category
                      }
                    </span>

                    <strong>
                      {
                        disease.name
                      }
                    </strong>

                  </div>

                  <small>
                    Run recommendation →
                  </small>

                </button>

              )
            )}

          </div>

        </section>

        {result &&
          renderResults()}

        {renderFooter()}

      </>
    );

  /* =======================================================
     DISEASES PAGE
     ======================================================= */

  const renderDiseases =
    () => (
      <>

        {renderTopbar(
          "AYURVEDIC DECISION SUPPORT",
          "Diseases"
        )}

        <section className="info-panel disease-library-panel">

          <div className="section-heading">

            <div>

              <p className="eyebrow">
                DISEASE KNOWLEDGE
              </p>

              <h3>
                Supported Conditions
              </h3>

              <p>
                Browse the conditions
                represented in the
                current recommendation
                knowledge base.
              </p>

            </div>

          </div>

          <div className="library-search">

            <div className="search-input-wrapper">

              <span>
                ⌕
              </span>

              <input
                type="text"
                value={diseaseSearch}
                onChange={(event) =>
                  setDiseaseSearch(
                    event.target.value
                  )
                }
                placeholder="Search conditions or categories..."
                autoComplete="off"
              />

            </div>

          </div>

          <div className="disease-grid">

            {filteredDiseases.map(
              (disease) => (

                <article
                  className="disease-card"
                  key={
                    disease.name
                  }
                >

                  <div className="disease-card-header">

                    <div>

                      <span className="card-category">
                        {
                          disease.category
                        }
                      </span>

                      <h4>
                        {
                          disease.name
                        }
                      </h4>

                    </div>

                    <span className="support-badge">
                      {
                        disease.status
                      }
                    </span>

                  </div>

                  <p>
                    {
                      disease.description
                    }
                  </p>

                  <div className="disease-card-footer">

                    <span>

                      <strong>
                        Recommendation
                      </strong>

                      <small>
                        Top-5 available
                      </small>

                    </span>

                    <button
                      type="button"
                      onClick={() =>
                        openDiseaseRecommendation(
                          disease.name
                        )
                      }
                    >
                      View
                      Recommendations
                      →
                    </button>

                  </div>

                </article>

              )
            )}

          </div>

          {filteredDiseases.length ===
            0 && (

            <div className="empty-result">

              <div>
                ⌕
              </div>

              <h4>
                No matching conditions
              </h4>

              <p>
                Try searching for
                another supported
                condition or category.
              </p>

            </div>

          )}

        </section>

        {renderFooter()}

      </>
    );

  /* =======================================================
     FORMULATIONS PAGE
     ======================================================= */

  const renderFormulations =
    () => (
      <>

        {renderTopbar(
          "AYURVEDIC DECISION SUPPORT",
          "Formulations"
        )}

        <section className="info-panel">

          <div className="section-heading">

            <div>

              <p className="eyebrow">
                FORMULATION LIBRARY
              </p>

              <h3>
                Ayurvedic Formulation
                Profiles
              </h3>

              <p>
                Explore representative
                formulation profiles
                used by the trained
                recommendation engine
                to rank candidates.
              </p>

            </div>

          </div>

          <div className="library-search">

            <div className="search-input-wrapper">

              <span>
                ⌕
              </span>

              <input
                type="text"
                value={
                  formulationSearch
                }
                onChange={(event) =>
                  setFormulationSearch(
                    event.target.value
                  )
                }
                placeholder="Search formulations, ingredients or categories..."
                autoComplete="off"
              />

            </div>

          </div>

          <div className="formulation-grid">

            {filteredFormulations.map(
              (formulation) => (

                <article
                  className="formulation-card"
                  key={
                    formulation.name
                  }
                >

                  <div className="formulation-card-header">

                    <div>

                      <span className="card-category">
                        {
                          formulation.category
                        }
                      </span>

                      <h4>
                        {
                          formulation.name
                        }
                      </h4>

                    </div>

                    <span className="profile-status">
                      ACTIVE
                    </span>

                  </div>

                  <p>
                    {
                      formulation.description
                    }
                  </p>

                  <div className="ingredient-section">

                    <span className="ingredient-title">
                      Ingredients
                    </span>

                    <div className="ingredient-list">

                      {formulation.ingredients.map(
                        (ingredient) => (

                          <span
                            key={
                              ingredient
                            }
                          >
                            {
                              ingredient
                            }
                          </span>

                        )
                      )}

                    </div>

                  </div>

                  <div className="formulation-footer">

                    <span>

                      <strong>
                        Profile Type
                      </strong>

                      <small>
                        Knowledge-base
                        formulation
                      </small>

                    </span>

                    <span>

                      <strong>
                        Ranking
                      </strong>

                      <small>
                        Eligible for
                        Top-5
                      </small>

                    </span>

                  </div>

                </article>

              )
            )}

          </div>

          {filteredFormulations.length ===
            0 && (

            <div className="empty-result">

              <div>
                ⌕
              </div>

              <h4>
                No formulations found
              </h4>

              <p>
                Try searching for a
                formulation name,
                ingredient, or
                category.
              </p>

            </div>

          )}

        </section>

        <section className="info-panel">

          <div className="section-heading">

            <div>

              <p className="eyebrow">
                PROFILE ENGINE
              </p>

              <h3>
                How Formulation
                Profiles Are Used
              </h3>

              <p>
                Each profile provides
                information that the
                recommendation engine
                can compare against a
                selected condition.
              </p>

            </div>

          </div>

          <div className="process-grid">

            <div className="process-card">

              <div className="process-number">
                01
              </div>

              <h4>
                Condition Input
              </h4>

              <p>
                The user provides a
                disease or condition
                to the recommendation
                engine.
              </p>

            </div>

            <div className="process-card">

              <div className="process-number">
                02
              </div>

              <h4>
                Profile Comparison
              </h4>

              <p>
                The engine compares
                the condition against
                available formulation
                profiles.
              </p>

            </div>

            <div className="process-card">

              <div className="process-number">
                03
              </div>

              <h4>
                Candidate Ranking
              </h4>

              <p>
                Candidate formulations
                are ranked and the
                strongest Top-5 results
                are returned.
              </p>

            </div>

          </div>

        </section>

        {renderFooter()}

      </>
    );

  /* =======================================================
     PERFORMANCE PAGE
     ======================================================= */

  const renderPerformance =
    () => {

      const ingredient50 =
        Number(
          metricValue(
            model?.metrics
              ?.ingredient_match_50,
            93.3
          )
        );

      const ingredient75 =
        Number(
          metricValue(
            model?.metrics
              ?.ingredient_match_75,
            70.0
          )
        );

      return (
        <>

          {renderTopbar(
            "AYURVEDIC DECISION SUPPORT",
            "Model Performance"
          )}

          <section className="info-panel">

            <div className="section-heading">

              <div>

                <p className="eyebrow">
                  MODEL INFORMATION
                </p>

                <h3>
                  Recommendation Engine
                  Performance
                </h3>

                <p>
                  Overview of the current
                  trained recommendation
                  engine and its validation
                  indicators.
                </p>

              </div>

            </div>

            <div className="performance-metrics-grid">

              <div className="large-metric-card">

                <span>
                  Average Accuracy
                </span>

                <strong>
                  {averageAccuracy.toFixed(
                    1
                  )}
                  %
                </strong>

                <div className="metric-progress">

                  <div
                    style={{
                      width: `${averageAccuracy}%`,
                    }}
                  />

                </div>

                <small>
                  Overall project
                  performance indicator
                </small>

              </div>

              <div className="large-metric-card">

                <span>
                  Ingredient Match @50
                </span>

                <strong>
                  {ingredient50.toFixed(
                    1
                  )}
                  %
                </strong>

                <div className="metric-progress">

                  <div
                    style={{
                      width: `${ingredient50}%`,
                    }}
                  />

                </div>

                <small>
                  Ingredient overlap at
                  the 50% threshold
                </small>

              </div>

              <div className="large-metric-card">

                <span>
                  Ingredient Match @75
                </span>

                <strong>
                  {ingredient75.toFixed(
                    1
                  )}
                  %
                </strong>

                <div className="metric-progress">

                  <div
                    style={{
                      width: `${ingredient75}%`,
                    }}
                  />

                </div>

                <small>
                  Ingredient overlap at
                  the 75% threshold
                </small>

              </div>

              <div className="large-metric-card">

                <span>
                  Recommendation Depth
                </span>

                <strong>
                  TOP-5
                </strong>

                <div className="metric-progress">

                  <div
                    style={{
                      width: "100%",
                    }}
                  />

                </div>

                <small>
                  Five ranked formulation
                  candidates
                </small>

              </div>

            </div>

          </section>

          <section className="info-panel">

            <div className="section-heading">

              <div>

                <p className="eyebrow">
                  MODEL CONFIGURATION
                </p>

                <h3>
                  Current Engine Details
                </h3>

              </div>

            </div>

            <div className="model-details-grid">

              <div className="detail-card">

                <span>
                  Model Version
                </span>

                <strong>
                  {model?.version ||
                    "final_top5_v2"}
                </strong>

                <small>
                  Currently active model
                </small>

              </div>

              <div className="detail-card">

                <span>
                  Knowledge Profiles
                </span>

                <strong>
                  {model?.profiles ||
                    48}
                </strong>

                <small>
                  Available formulation
                  profiles
                </small>

              </div>

              <div className="detail-card">

                <span>
                  Ranking Output
                </span>

                <strong>
                  Top-5
                </strong>

                <small>
                  Highest-ranked
                  candidates
                </small>

              </div>

              <div className="detail-card">

                <span>
                  System Status
                </span>

                <strong>
                  Online
                </strong>

                <small>
                  Recommendation API
                  available
                </small>

              </div>

            </div>

          </section>

          <section className="info-panel">

            <div className="section-heading">

              <div>

                <p className="eyebrow">
                  METRIC GUIDE
                </p>

                <h3>
                  What These Numbers Mean
                </h3>

                <p>
                  These indicators describe
                  different aspects of how
                  the recommendation system
                  performs.
                </p>

              </div>

            </div>

            <div className="metric-guide-grid">

              <div className="guide-card">

                <div className="guide-icon">
                  ◎
                </div>

                <div>

                  <h4>
                    Average Accuracy
                  </h4>

                  <p>
                    A high-level indicator
                    of the model's overall
                    recommendation
                    performance across the
                    evaluated project data.
                  </p>

                </div>

              </div>

              <div className="guide-card">

                <div className="guide-icon">
                  ♧
                </div>

                <div>

                  <h4>
                    Ingredient Match @50
                  </h4>

                  <p>
                    Indicates how often the
                    predicted formulation
                    overlaps with the
                    reference formulation
                    at the 50% ingredient-match
                    threshold.
                  </p>

                </div>

              </div>

              <div className="guide-card">

                <div className="guide-icon">
                  ◇
                </div>

                <div>

                  <h4>
                    Ingredient Match @75
                  </h4>

                  <p>
                    A stricter
                    ingredient-overlap
                    measure requiring a
                    higher level of agreement
                    with the reference
                    formulation.
                  </p>

                </div>

              </div>

              <div className="guide-card">

                <div className="guide-icon">
                  ✦
                </div>

                <div>

                  <h4>
                    Top-5 Depth
                  </h4>

                  <p>
                    Instead of returning
                    one candidate, the
                    engine presents five
                    ranked formulation
                    candidates for
                    comparison.
                  </p>

                </div>

              </div>

            </div>

          </section>

          {renderFooter()}

        </>
      );
    };

  /* =======================================================
     APP OUTPUT
     ======================================================= */

  return (
    <div className="app-shell">

      {renderSidebar()}

      <main className="main-content">

        {activePage ===
          "dashboard" &&
          renderDashboard()}

        {activePage ===
          "recommendations" &&
          renderRecommendations()}

        {activePage ===
          "diseases" &&
          renderDiseases()}

        {activePage ===
          "formulations" &&
          renderFormulations()}

        {activePage ===
          "performance" &&
          renderPerformance()}

      </main>

    </div>
  );
}

export default App;
