# EarthSage AI — Hackathon Demonstration & Judging Guide

**NASA International Space Apps Challenge**  
**Challenge Track:** *Be An Earth System Trend Detective!*  
**Project:** EarthSage AI — Empirical Geospatial Climate Trend Detective  
**Target Environment:** Local Docker Stack (Frontend: `5174`, Backend: `8020`, PostgreSQL: `5439`)

---

## 1. Executive Summary for Judges

Welcome, NASA Space Apps Challenge judges! 

When investigating Earth system trends, **data integrity, statistical rigor, and defensible scientific methodology** must take precedence over visual fluff or hallucinated AI claims. EarthSage AI was built specifically to solve the "Earth System Trend Detective" challenge with uncompromising scientific fidelity:

1. **Authentic NASA Data:** Ingests continuous, gridded atmospheric reanalysis from the **NASA POWER / MERRA-2** project without fabrication or synthetic extrapolation.
2. **Defensible Statistical Engine:** Implements dual-tier non-parametric trend detection:
   - **Hirsch-Slack Seasonal Mann-Kendall** ($p=12$) accounting for annual seasonality.
   - **Day-Weighted Annual Mann-Kendall** accounting for leap-year calendar days.
   - **Theil-Sen Robust Slope** strictly reported in **physical units per year (`{units}/yr`)**.
   - **Statsmodels Multi-Lag Ljung-Box Test** ($k=1..4$) and **Hamed-Rao Variance Correction** ($V^*/V$).
3. **Climatological Anomaly Isolation:** Detects month-of-year standardized departures ($|Z| \ge 2.0\sigma$) with transparent disclosures distinguishing statistical extremities from ground disasters.
4. **Coupled Variable Co-Variation:** Normalizes divergent physical parameters into standardized Z-scores, computes Pearson $r$ and Spearman $\rho$, and enforces a strict **"Correlation does not imply causation"** disclaimer.
5. **Open Science Exports:** Generates dynamic **ReportLab PDF** research reports and FAIR-compliant **commented metadata CSV** exports.
6. **Safe AI Assistance:** Google Gemini integration operates strictly as an explanatory synthesizer bounded by pre-computed statistical tables, with a deterministic offline fallback.

---

## 2. Pre-Flight System Verification (30 Seconds)

Before starting your demonstration, verify that the EarthSage AI containers are running and healthy.

### Check Container Status
Open PowerShell or your terminal and run:
```powershell
docker ps --filter "name=earthsage"
```
**Expected Output:**
```
NAMES                STATUS         PORTS
earthsage-frontend   Up (healthy)   0.0.0.0:5174->80/tcp
earthsage-backend    Up (healthy)   0.0.0.0:8020->8000/tcp
earthsage-postgres   Up (healthy)   0.0.0.0:5439->5432/tcp
```

### Verify Automated Tests (Unit Tests, Auth Tests, & Regression Checks)
```powershell
# 1. Scientific Statistical Engine Test Suite (18 tests)
docker exec earthsage-backend bash -c "export PYTHONPATH=/app; pytest /app/tests/test_scientific_engine.py"

# 2. JWT Authentication & Security Test Suite (7 tests)
docker exec earthsage-backend bash -c "export PYTHONPATH=/app; pytest /app/tests/test_auth.py"

# 3. End-to-End Scientific & Functional Regression Suite (14 validation points)
docker exec earthsage-backend python /app/tests/run_e2e_regression.py

# 4. Live Authentication & Data Isolation E2E Demo Flow (11 steps)
docker exec earthsage-backend python /app/scripts/verify_auth_e2e_demo.py
```
**Expected Output:** All test suites pass 100% with zero errors.

### Open the Application
- **Frontend Research Workstation:** [http://localhost:5174](http://localhost:5174)
- **FastAPI Backend Documentation:** [http://localhost:8020/docs](http://localhost:8020/docs)
- **Backend Health Check:** [http://localhost:8020/health](http://localhost:8020/health)

---

## 3. Step-by-Step Live Demonstration Script (5–7 Minutes)

### Step 0: Authentication & Secure Session Management (45s)
1. Open [http://localhost:5174](http://localhost:5174) in your browser.
2. If unauthenticated, the application presents the clean **Researcher Sign In** screen.
3. Click **Register Account** (or navigate to `/signup`):
   - Enter Full Name: `Dr. Sarah Khan`
   - Enter Institutional Email: `sarah.khan@earthscience.org`
   - Enter Password: `SecurePassword@2026!`
   - Click **Complete Registration & Launch Station**.
4. **Key Talking Point for Judges:**
   *"Notice the authentication architecture: We implemented production-grade JWT authentication backed by PostgreSQL 16. Passwords are never stored in plaintext—they are hashed using bcrypt with 12 rounds. Access tokens are kept strictly in-memory (preventing XSS theft), while refresh tokens are stored as SHA-256 hashes in PostgreSQL and transmitted via HttpOnly, SameSite, and Secure cookies. It includes automatic token rotation, replay-attack detection that revokes all sessions on reuse, and silent 401 token refresh."*
5. Point out the top bar: Displays `Dr. Sarah Khan (sarah.khan@earthscience.org)` and a functional **Sign Out** button.
6. Refresh the browser: The session persists seamlessly via the HttpOnly refresh cookie without requiring re-entry of credentials.

### Step 1: Scientific Workstation Overview (30s)
1. Open [http://localhost:5174](http://localhost:5174) in your browser.
2. **Key Talking Point:**  
   *"Notice the interface aesthetic: We deliberately avoided the generic AI SaaS look (neon gradients, purple glow, glassmorphism, floating cards). EarthSage AI is designed as a focused, high-density scientific workstation with a neutral grey palette, restrained blue functional accents, and Inter typography."*
3. In the investigations table, click on the pre-loaded 30-year climatological study:  
   **"Lahore Meteorological Trend Analysis (1991–2020)"**.

---

### Step 2: Climate Trend Explorer (90s)
You are now viewing the **Climate Trend Explorer** tab.

1. **Parameter Toggle:**
   - Look at the top selector showing `T2M (°C)` and `PRECTOTCORR (mm/day)`.
   - The interactive chart displays the **observed 30-year annual series** alongside the **Ordinary Least Squares (OLS) trend line**.
2. **Temperature (T2M) Trend Analysis:**
   - Scroll down to the **Scientific Findings** card.
   - Point out the **Dual-Tier Mann-Kendall Evaluation**:
     - **Seasonal Mann-Kendall ($p=12$):** $p = 0.00146$ ($p < 0.05$), Kendall's $\tau = -0.119$, Sen's Slope = **$-0.0287 \text{ °C/yr}$**.
     - **Annual Day-Weighted Mann-Kendall:** $p = 0.1535$ ($p \ge 0.05$, non-significant), Kendall's $\tau = -0.186$, Sen's Slope = **$-0.0303 \text{ °C/yr}$**.
   - **Key Scientific Talking Point:**  
     *"Notice the critical scientific distinction: Seasonal MK tests for monotonic trends across years within corresponding calendar months while accounting for the seasonal cycle. It detects a statistically significant intra-monthly cooling pattern in certain months. However, the day-weighted annual mean does not reach the 95% confidence threshold ($p = 0.1535$). EarthSage AI reports both transparently rather than cherry-picking only the significant result."*
3. **Sen's Slope Units:**
   - Highlight the slope label: **`°C/yr`** (NOT `°C/mo`).
   - Package source code inspection proves Seasonal Sen's slope calculates step increments across years, meaning the physical unit is per year.
4. **Autocorrelation Diagnostic Table:**
   - Point to the **Serial Autocorrelation Audit** card.
   - Show the **Multi-Lag Ljung-Box Test** across lags 1 to 4:
     - Lag 1: $r_1 = +0.3574$, $Q = 4.230$, $p = 0.0397$ (Marginally significant).
     - Lags 2, 3, 4: $p > 0.08$ (Non-significant).
     - Hamed-Rao Variance Ratio: $V^*/V = 1.0000$ (Detrended rank autocorrelations fall within $\pm 1.96/\sqrt{30} = \pm 0.3579$, leaving variance uninflated).

---

### Step 3: Climatological Anomaly Detection (60s)
1. Click on the **"Anomaly Detection"** tab.
2. **Methodology:**
   - Standardized Z-score departures computed relative to each specific calendar month's 1991–2020 distribution:
     $$Z_{y,m} = \frac{x_{y,m} - \mu_m}{\sigma_m}$$
3. **Observed Extremities:**
   - **Temperature:** 7 monthly anomalies ($|Z| \ge 2.0\sigma$) across 360 months.
     - **February 2006:** Observed $20.59\text{ °C}$ vs baseline mean $15.84\text{ °C}$ ($Z = +3.19\sigma$, extreme positive anomaly).
     - **November 2020:** Observed $17.23\text{ °C}$ vs baseline mean $19.97\text{ °C}$ ($Z = -2.47\sigma$, cold departure).
   - **Precipitation:** 16 monthly anomalies.
     - **November 2020:** Observed $2.08\text{ mm/day}$ vs baseline mean $0.24\text{ mm/day}$ ($Z = +4.44\sigma$, extreme unseasonal rain).
     - **September 2014:** Observed $10.88\text{ mm/day}$ vs baseline mean $2.25\text{ mm/day}$ ($Z = +4.25\sigma$, late-monsoon surge).
4. **Key Scientific Talking Point:**  
   *"Notice the prominent callout banner: Statistical anomalies indicate mathematical departure ($\ge 2.0\sigma$). They represent statistical extremities and do not automatically confirm specific ground damage or declared disaster events without auxiliary ground verification."*

---

### Step 4: Variable Comparison & Non-Causality (60s)
1. Click on the **"Variable Comparison"** tab.
2. **Unified Z-Score Chart:**
   - Shows both Temperature (T2M) and Precipitation (PRECTOTCORR) plotted as normalized standard deviations ($Z_t$) over the entire 360-month timeline.
3. **Correlation Metrics:**
   - **Spearman Rank Correlation:** $\rho = +0.426$, $p = 2.72 \times 10^{-17}$ (Significant).
   - **Pearson Linear Correlation:** $r = +0.377$, $p = 1.43 \times 10^{-13}$ (Significant).
4. **Key Scientific Talking Point:**  
   *"Direct your attention to the banner: **'CORRELATION DOES NOT IMPLY CAUSATION.'**  
   In South Asia, the summer monsoon peaks in July and August—the hottest months of the year. This produces a positive correlation between temperature and precipitation driven by external astronomical and synoptic solar forcing, not by temperature directly creating rainfall."*

---

### Step 5: AI Research Assistant (Synthesis & Planning) (60s)
1. Click on the **"AI Research Assistant"** tab.
2. **Factual Grounding:**
   - The assistant displays a structured 5-part synthesis:
     1. Plain Language Summary
     2. Statistical Deep Dive (citing exact $p$-values and Kendall $\tau$)
     3. Physical Mechanisms (monsoon circulation, aerosol optical depth)
     4. Scientific Limitations (0.5° x 0.625° reanalysis grid cell vs local station thermistors)
     5. Recommended Follow-ups (spatial correlation across neighboring grid cells)
3. **Safety & Fallback:**
   - Point out the footer: *"Rule-based scientific synthesis generated from backend statistical engine (or Google Gemini when active)."*
   - The AI is never permitted to recalculate or fabricate statistical numbers; it interprets only the verified results generated by the mathematical engine.

---

### Step 6: Reproducible Open Science Reports (45s)
1. Look at the top right of the investigation view:
   - Click the **"Export PDF"** button.
     - A formatted, publication-ready PDF opens.
     - Inspect the document: It includes research metadata, exact coordinate hemispheres (`31.5497°N, 74.3436°E`), observation counts, full autocorrelation audit tables, and finding summaries. All text is XML-escaped to prevent injection or compilation errors.
   - Click the **"Export CSV"** button.
     - Open the downloaded CSV file.
     - Notice the commented metadata header (`#`) containing investigation ID, title, hypothesis, data provider (NASA POWER), reanalysis resolution, and analytical methodology according to Open Science FAIR principles.

---

### Step 7: Formulating a New Live Investigation (45s)
1. Click **"New Investigation"** in the top navigation.
2. In the AI Assistant prompt card, enter a research query:  
   *"Investigate precipitation patterns and temperature trends in Karachi from 1995 to 2020."*
3. Click **"Formulate Plan"**:
   - The planner extracts the coordinates, selects parameters (`T2M`, `PRECTOTCORR`), sets temporal bounds (`1995` to `2020`), and generates physical justifications.
4. Click **"Create & Run Investigation"**:
   - The system calls the live NASA POWER API asynchronously.
   - It performs calendar day-weighted aggregation, calculates Mann-Kendall statistics, detects anomalies, and displays the freshly generated findings in real time.

---

## 4. Judge Q&A & Scientific Defense Guide

### Q1: Why does Seasonal Mann-Kendall show a trend ($p = 0.0015$), while Annual Mann-Kendall does not ($p = 0.1535$)?
> **Answer:**  
> "Seasonal Mann-Kendall evaluates monotonic trends across years *within* corresponding calendar months (e.g. comparing all Januaries to each other, all Februaries to each other) and sums their individual Kendall scores. In Lahore, specific shoulder or winter months show consistent negative shifts over the 30-year period. However, when aggregated into day-weighted annual means, the net yearly shift does not achieve statistical significance at $\alpha = 0.05$ ($p = 0.1535$). Reporting both numbers prevents false positive claims while preserving the intra-annual signal."

### Q2: Why are Sen's slopes reported in `{units}/yr` rather than `{units}/mo`?
> **Answer:**  
> "PyMannKendall's `seasonal_sens_slope` reshapes the series into an $(N_{years} \times 12)$ matrix and computes slopes between identical months across different years: $(x_{j,m} - x_{i,m}) / (j - i)$. Since the denominator $(j - i)$ represents the time step in calendar years, the resulting median slope is intrinsically in physical units per year. Reporting this as per month would understate the annual rate by a factor of 12."

### Q3: Why is Calendar Day-Weighting necessary for Annual Aggregation?
> **Answer:**  
> "Months have unequal day lengths (28, 29, 30, or 31 days). A simple arithmetic average of 12 monthly values gives February (28 days) the same weight as July (31 days), introducing systematic mathematical distortion. EarthSage AI weights each month by its exact day count ($d_m / 365$ or $d_m / 366$ in leap years). This matches NASA POWER's raw `YYYY13` daily assimilation annual aggregates to within $< 0.005$ units."

### Q4: How is Serial Autocorrelation handled?
> **Answer:**  
> "Positive autocorrelation inflates the variance of the Mann-Kendall test statistic $S$, leading to falsely rejected null hypotheses (false trends). We run a multi-lag Ljung-Box test ($k=1..4$) via `statsmodels`. When autocorrelation is present, we evaluate Hamed-Rao (1998) variance correction ($V^*/V$). In the Lahore annual series, detrended rank autocorrelations fall within the Gaussian critical bounds ($\pm 1.96/\sqrt{30} = \pm 0.3579$), so $V^*/V = 1.0000$."

### Q5: How do you prevent AI hallucinations in climate findings?
> **Answer:**  
> "The AI never computes statistical metrics. All mathematical calculations ($p$-values, Sen's slope, $\tau$, $Z$-scores, Ljung-Box $Q$, Pearson $r$, Spearman $\rho$) are calculated deterministically by our Python statistical engine. The Google Gemini prompt is strictly constrained to summarize and explain the verified results table. If the API key is not configured, the platform falls back to a deterministic rule-based scientific synthesizer."

### Q6: Can these results be interpreted as physical station data?
> **Answer:**  
> "No, and we explicitly disclose this in the UI, PDF, and CSV reports. The data are from NASA POWER's MERRA-2 assimilation grid ($0.5^\circ \times 0.625^\circ$). They represent model-assimilated gridded reanalysis, which integrates satellite observations and atmospheric models, rather than direct in-situ thermometer readings at a specific street corner."

### Q7: Why did you use NASA POWER instead of Giovanni or AppEEARS?
> **Answer:**  
> "The challenge prompt explicitly encourages investigating variables from NASA Earth science missions or produced by Earth science models. NASA POWER directly serves the Modern-Era Retrospective analysis for Research and Applications, Version 2 (MERRA-2) assimilation model produced by NASA's Global Modeling and Assimilation Office (GMAO). While Giovanni and AppEEARS are excellent tools featured in challenge resources, their programmatic interfaces require authenticated Earthdata Login (EDL) accounts and asynchronous job queue processing that can take hours to return subsets. To provide a live, responsive, sub-second research experience for users and hackathon judges without demanding personal EDL account creation, NASA POWER's open REST API was selected. Giovanni and AppEEARS are cataloged in EarthSage AI as future roadmap integrations."

---

## 5. Summary Matrix for Judges

| Evaluation Criterion | Implementation in EarthSage AI | Verification Artifact |
| :--- | :--- | :--- |
| **Authentic NASA Data** | NASA POWER REST API / MERRA-2 Atmospheric Reanalysis | `nasa_power.py` & live API calls |
| **Non-Parametric Trends** | Seasonal MK ($p=12$), Annual MK, Sen's Slope (`{units}/yr`) | `trend_analysis.py`, 18 passing tests |
| **Mathematical Precision** | Day-weighted annual aggregation with leap-year accounting | `< 0.005` error vs NASA `YYYY13` |
| **Autocorrelation Control** | Multi-lag Ljung-Box diagnostic and Hamed-Rao variance | `statsmodels` integration & audit table |
| **Anomaly Detection** | Month-of-year standardized departure ($|Z| \ge 2.0\sigma$) | `anomalies.py`, Anomaly UI tab |
| **Variable Comparison** | Normalized Z-scores, Pearson $r$, Spearman $\rho$, Non-causality | `comparison.py`, Comparison UI tab |
| **Reproducibility** | ReportLab dynamic PDF & FAIR commented metadata CSV | `pdf_generator.py`, `csv_generator.py` |
| **AI Safety & Utility** | Bound to calculated tables, deterministic offline fallback | `ai_service.py`, `ai.py` route |
| **Product Design** | Restrained scientific workstation, light theme, zero visual fluff | React 18, Tailwind, Recharts |
| **Zero Regressions** | Production ports preserved, other Docker projects untouched | `5174`, `8020`, `5439` healthy |

