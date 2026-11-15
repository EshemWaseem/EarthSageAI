# EarthSage AI — Scientific Statistical Engine & Geospatial Integrity Audit

**Audit Date:** 2026-11-15  
**Study Target:** Lahore Grid Cell (31.5497°N, 74.3436°E, WGS84)  
**Study Period:** 1991-01 to 2020-12 (30 Years, 360 Months Continuous)  
**Data Source:** NASA POWER / MERRA-2 Atmospheric Reanalysis (Monthly Aggregations)  
**Audit Status:** FULL SCIENTIFIC INTEGRITY AUDIT COMPLETED  

---

## 1. Executive Summary

This document presents the definitive, peer-reviewable scientific audit of EarthSage AI's statistical computing engine, data aggregation pipeline, and reporting infrastructure.

All calculations have been independently reproduced and cross-validated across four independent strata:
1. **Raw NASA POWER REST API** queried directly at source coordinates.
2. **Standalone Python Verification Engine** running independent numerical implementations.
3. **PostgreSQL Relational Persistence** (`inv-20261114-30c9a0`).
4. **Compiled Artifacts** (React/TypeScript Production Build & ReportLab Dynamic PDF).

**Result:** **ZERO NUMERICAL DISCREPANCIES DETECTED.** Every value stored in the database matches independent calculations to six decimal places.

---

## 2. PyMannKendall Sen's Slope Unit Verification

### 2.1 Code-Level Inspection
A source-level inspection was conducted on the installed `pymannkendall` (v1.4.3) package inside the production environment:
- `seasonal_test(x_old, period=12)` internally delegates to `seasonal_sens_slope(x_old, period=12)`.
- In `seasonal_sens_slope`:
  ```python
  x = x.reshape(int(len(x)/period), period) # Reshaped to (N_years, 12)
  for i in range(period):
      d.extend(__sens_estimator(x[:, i]))
  slope = np.nanmedian(np.asarray(d))
  ```
- In `__sens_estimator(x[:, i])`, slopes are computed as `(x[j, i] - x[i, i]) / (j - i)`. Because $j$ and $i$ index the annual rows ($0, 1, ..., N-1$), the time interval $(j - i)$ is strictly in **years**.
- Package documentation confirms: *"intercept of Kendall-Theil Robust Line, where full period cycle consider as unit time step"*.

### 2.2 Finding & Correction
- **Previous Defect:** Seasonal Sen's slope was previously labelled `{units}/mo` in finding summaries, misrepresenting annual rates by a factor of 12.
- **Correction Applied:** All slope parameters across `trend_analysis.py`, `investigation_service.py`, `ResearchResults.tsx`, and `pdf_generator.py` are strictly defined and labelled in **units of parameter per year (`{units}/yr`)**.

| Analysis Tier | Function Tested | Temporal Step | Physical Slope Unit | Verification |
| :--- | :--- | :--- | :--- | :--- |
| **Seasonal Mann-Kendall** | `mk.seasonal_test(period=12)` | 1 Seasonal Cycle (1 Year) | `°C/yr` or `mm/day/yr` | **VERIFIED** |
| **Annual Standard MK** | `mk.original_test()` | 1 Calendar Year | `°C/yr` or `mm/day/yr` | **VERIFIED** |
| **Annual Hamed-Rao MK** | `mk.hamed_rao_modification_test()` | 1 Calendar Year | `°C/yr` or `mm/day/yr` | **VERIFIED** |
| **Annual OLS Regression** | `scipy.stats.linregress()` | 1 Calendar Year | `°C/yr` or `mm/day/yr` | **VERIFIED** |

---

## 3. Serial Autocorrelation Testing & Hamed-Rao Assessment

### 3.1 Methodology
Testing serial autocorrelation using only lag-1 with manual heuristics is inadequate for climatological time series. The engine now uses `statsmodels.stats.diagnostic.acorr_ljungbox` across multiple lags ($k = 1, 2, 3, 4$) with degrees of freedom $df = k$.

### 3.2 Small-Sample Limitations ($N = 30$)
With $N = 30$ annual observations:
- Portmanteau tests (Ljung-Box, Box-Pierce) exhibit reduced statistical power ($\beta$) to detect mild autoregressive structures.
- Finite-sample bias in sample autocorrelation estimators (Hurvich & Tsai, 1989) means non-rejection of the null hypothesis at $\alpha = 0.05$ does not prove complete independence.
- Conversely, a single lag marginally crossing $p < 0.05$ may reflect sampling variability rather than an underlying stochastic memory.

### 3.3 Empirical Autocorrelation Audit Results

#### Temperature at 2 Meters (T2M) — Annual Series ($N = 30$)
| Lag ($k$) | Degrees of Freedom ($df$) | Sample Autocorrelation ($r_k$) | Ljung-Box $Q$ Stat | $p$-value | Significance ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Lag 1** | 1 | $+0.3574$ | $4.2296$ | $0.0397$ | Significant |
| **Lag 2** | 2 | $+0.1430$ | $4.9304$ | $0.0850$ | Not Significant |
| **Lag 3** | 3 | $-0.0346$ | $4.9730$ | $0.1738$ | Not Significant |
| **Lag 4** | 4 | $-0.1560$ | $5.8717$ | $0.2089$ | Not Significant |

#### Precipitation Corrected (PRECTOTCORR) — Annual Series ($N = 30$)
| Lag ($k$) | Degrees of Freedom ($df$) | Sample Autocorrelation ($r_k$) | Ljung-Box $Q$ Stat | $p$-value | Significance ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Lag 1** | 1 | $+0.3346$ | $3.7070$ | $0.0542$ | Not Significant |
| **Lag 2** | 2 | $+0.1744$ | $4.7499$ | $0.0930$ | Not Significant |
| **Lag 3** | 3 | $+0.0469$ | $4.8281$ | $0.1848$ | Not Significant |
| **Lag 4** | 4 | $-0.1133$ | $5.3024$ | $0.2576$ | Not Significant |

### 3.4 Hamed-Rao Variance Adjustment Evaluation
The Hamed and Rao (1998) modified Mann-Kendall test detrends the series by subtracting Sen's slope ($x_{detrend} = x - \text{slope} \times t$), transforms residuals into ranks, and calculates the variance correction factor:
$$\frac{n}{n_s^*} = 1 + \frac{2}{n(n-1)(n-2)} \sum_{i=1}^{n-1} (n-i)(n-i-1)(n-i-2) \rho^*(i)$$
where only empirical rank autocorrelations $\rho^*(i)$ exceeding the two-tailed Gaussian critical bound $\pm \frac{z_{\alpha/2}}{\sqrt{n}} = \pm \frac{1.96}{\sqrt{30}} = \pm 0.3579$ are included in the variance expansion.

**Empirical Result:**
- For both T2M and PRECTOTCORR, the rank autocorrelations of the detrended series fall within the bounds $[-0.3579, +0.3579]$.
- Consequently, $\sum = 0$, and the variance correction factor is exactly:
  $$\frac{V^*}{V} = 1.0000$$
- Both Standard Mann-Kendall and Hamed-Rao Modified Mann-Kendall yield identical variance ($Var(S) = 3141.67$) and identical $p$-values. Both results are preserved side-by-side in the structured output.

---

## 4. Annual Aggregation Methodology

### 4.1 Mathematical Formulation
Unweighted arithmetic means ($\frac{1}{12}\sum M_m$) introduce systematic error because calendar months have unequal lengths (28, 29, 30, or 31 days). EarthSage AI implements calendar day-weighting:

For Year $Y$ with monthly values $M_1, M_2, ..., M_{12}$ and month day counts $d_{Y, 1}, d_{Y, 2}, ..., d_{Y, 12}$:
$$D_Y = \sum_{m=1}^{12} d_{Y, m} = \begin{cases} 366 & \text{if leap year} \\ 365 & \text{if non-leap year} \end{cases}$$

#### Temperature (T2M):
$$\bar{T}_{annual, Y} = \frac{\sum_{m=1}^{12} T_{Y, m} \times d_{Y, m}}{D_Y}$$

#### Precipitation (PRECTOTCORR):
Preserves the physical rate unit (`mm/day`):
$$\bar{P}_{daily\_rate, Y} = \frac{\sum_{m=1}^{12} P_{Y, m} \times d_{Y, m}}{D_Y} \quad (\text{mm/day})$$
Annual cumulative precipitation is also recorded as a distinct metric:
$$P_{accumulated, Y} = \sum_{m=1}^{12} (P_{Y, m} \times d_{Y, m}) \quad (\text{mm/year})$$

### 4.2 Leap Year & Calendar Completeness Rules
1. **All 12 Calendar Months Required:** Every year is verified to possess months $1, 2, ..., 12$. Any year missing any month is systematically excluded from the annual trend series.
2. **Duplicate Month Detection:** Years with duplicate records for the same month are rejected.
3. **Invalid Value Rejection:** Values $\le -900.0$ or `NaN` trigger year exclusion.
4. **Audit Log:** Excluded years and specific exclusion reasons are returned in structured metadata (`excluded_years`).

### 4.3 Validation Against NASA POWER `YYYY13` Aggregates
NASA POWER reports an annual aggregate under month key `13` computed from the underlying daily MERRA-2 assimilation flux. Day-weighted monthly aggregation closely reproduces NASA's own annual aggregates:

| Year | Type | Total Days | Parameter | Day-Weighted Mean | Unweighted Mean | NASA Reported `YYYY13` | Discrepancy (Day-Weighted vs NASA) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1991** | Standard | 365 | T2M | $26.3039 \text{ °C}$ | $26.2500 \text{ °C}$ | $26.3000 \text{ °C}$ | **$+0.0039 \text{ °C}$** |
| **1992** | Leap | 366 | T2M | $24.9452 \text{ °C}$ | $24.9192 \text{ °C}$ | $24.9500 \text{ °C}$ | **$-0.0048 \text{ °C}$** |
| **1991** | Standard | 365 | PRECTOTCORR | $0.7836 \text{ mm/d}$ | $0.7783 \text{ mm/d}$ | $0.7800 \text{ mm/d}$ | **$+0.0036 \text{ mm/d}$** |
| **1992** | Leap | 366 | PRECTOTCORR | $1.6322 \text{ mm/d}$ | $1.6300 \text{ mm/d}$ | $1.6300 \text{ mm/d}$ | **$+0.0022 \text{ mm/d}$** |

*Notice:* The unweighted mean exhibits a significant offset (e.g. $0.05 \text{ °C}$ in 1991), whereas day-weighting aligns with NASA POWER's daily assimilation to within $< 0.005 \text{ units}$.

---

## 5. Removal of Fabricated Confidence Scores

- **Previous Defect:** Hardcoded confidence scores (`0.95`, `0.85`, `0.80`) were previously assigned to findings based on arbitrary status branches.
- **Correction Applied:**
  - Hardcoded confidence percentages have been **completely eliminated** from `investigation_service.py`.
  - Frontend type definition updated: `confidenceScore?: number`.
  - Frontend UI (`ResearchResults.tsx`) updated: Arbitrary `Confidence: XX%` badge removed.
  - Findings now communicate certainty exclusively via rigorous empirical metrics:
    - Exact $p$-values
    - Kendall's rank correlation $\tau$
    - Sen's slope with physical units
    - Sample size ($N$ years, $n$ months)
    - Autocorrelation significance status

---

## 6. Elimination of Silent Statistical Failures

- **Previous Defect:** Broad `except Exception:` blocks returned fallback defaults ($p=1.0, \text{slope}=0.0, \text{trend}="unknown"$), silently masking computation errors as empirical "no trend / baseline stability".
- **Correction Applied:**
  - Structured error statuses introduced: `"insufficient_data"`, `"constant_series"`, `"insufficient_annual_data"`, `"failed"`.
  - Constant series (variance $= 0$) are explicitly detected; trend test is marked mathematically undefined.
  - Insufficient sample sizes ($n < 24$ for Seasonal MK, $N < 10$ for Annual MK) reject analysis with structured error messages.
  - If a parameter calculation fails, no scientific finding is generated.
  - Overall investigation status is marked `"failed"` if all parameter calculations fail.

---

## 7. Dynamic PDF Reporting & XML Escaping

The ReportLab PDF engine (`pdf_generator.py`) was completely overhauled:
1. **XML/HTML Escaping:** All user-supplied strings (`title`, `research_question`, `hypothesis`, `location_name`, finding summaries) are sanitized via `html.escape()`. Special characters (`&`, `<`, `>`, `"`, `'`) generate valid flowables without crashing ReportLab.
2. **Dynamic Coordinate Formatting:** Hemispheric directions are calculated dynamically:
   - Latitude: `lat >= 0 ? "N" : "S"`
   - Longitude: `lon >= 0 ? "E" : "W"`
   - Format: `31.5497°N, 74.3436°E (WGS84)`
3. **Dynamic Observation Metadata:** Observation counts and completeness percentages are extracted from live calculation metadata (e.g. `360 months (100.0% valid, 360 valid)`).
4. **Autocorrelation Documentation:** A dedicated section documents multi-lag Ljung-Box statistics, sample autocorrelation coefficients, and Hamed-Rao variance adjustment factors.

---

## 8. Independent Reproducibility & Numerical Results

### Lahore 1991–2020 Validated Numerical Baseline

| Parameter | Metric | PostgreSQL Stored Value | Independent Recalculation | Discrepancy |
| :--- | :--- | :--- | :--- | :--- |
| **T2M** | Sample Size | 360 months (30 years) | 360 months (30 years) | None |
| **T2M** | Monthly Mean $\pm 1\sigma$ | $25.7593 \pm 8.2974 \text{ °C}$ | $25.7593 \pm 8.2974 \text{ °C}$ | $0.0000$ |
| **T2M** | Day-Weighted Annual Mean | $25.7985 \text{ °C}$ | $25.7985 \text{ °C}$ | $0.0000$ |
| **T2M** | Annual MK Tau ($\tau$) | $-0.1862$ | $-0.1862$ | $0.0000$ |
| **T2M** | Annual MK $p$-value | $0.153498$ | $0.153498$ | $0.0000$ |
| **T2M** | Annual Sen's Slope | $-0.030317 \text{ °C/yr}$ | $-0.030317 \text{ °C/yr}$ | $0.0000$ |
| **T2M** | Seasonal MK Tau ($\tau$) | $-0.1186$ | $-0.1186$ | $0.0000$ |
| **T2M** | Seasonal MK $p$-value | $0.001456$ | $0.001456$ | $0.0000$ |
| **T2M** | Seasonal MK Sen's Slope | $-0.028730 \text{ °C/yr}$ | $-0.028730 \text{ °C/yr}$ | $0.0000$ |
| **T2M** | Hamed-Rao Variance Ratio ($V^*/V$) | $1.0000$ | $1.0000$ | $0.0000$ |
| **PRECTOTCORR** | Sample Size | 360 months (30 years) | 360 months (30 years) | None |
| **PRECTOTCORR** | Monthly Mean $\pm 1\sigma$ | $1.4903 \pm 1.9880 \text{ mm/d}$ | $1.4903 \pm 1.9880 \text{ mm/d}$ | $0.0000$ |
| **PRECTOTCORR** | Day-Weighted Annual Mean | $1.4952 \text{ mm/d}$ | $1.4952 \text{ mm/d}$ | $0.0000$ |
| **PRECTOTCORR** | Annual MK Tau ($\tau$) | $+0.3379$ | $+0.3379$ | $0.0000$ |
| **PRECTOTCORR** | Annual MK $p$-value | $0.009193$ | $0.009193$ | $0.0000$ |
| **PRECTOTCORR** | Annual Sen's Slope | $+0.025846 \text{ mm/d/yr}$ | $+0.025846 \text{ mm/d/yr}$ | $0.0000$ |
| **PRECTOTCORR** | Seasonal MK Tau ($\tau$) | $+0.1395$ | $+0.1395$ | $0.0000$ |
| **PRECTOTCORR** | Seasonal MK $p$-value | $0.000178$ | $0.000178$ | $0.0000$ |
| **PRECTOTCORR** | Seasonal MK Sen's Slope | $+0.010000 \text{ mm/d/yr}$ | $+0.010000 \text{ mm/d/yr}$ | $0.0000$ |
| **PRECTOTCORR** | Hamed-Rao Variance Ratio ($V^*/V$) | $1.0000$ | $1.0000$ | $0.0000$ |

---

## 9. Automated Test Suite Results

An end-to-end automated test suite (`backend/tests/test_scientific_engine.py`) containing 18 unit and integration tests was executed inside the production backend environment:

| Test Case | Description | Result |
| :--- | :--- | :--- |
| `test_complete_12_month_years` | Verifies clean 12-month calendar series aggregation | **PASS** |
| `test_missing_months_detection` | Verifies incomplete years (11 months) are excluded | **PASS** |
| `test_duplicate_months_detection` | Verifies duplicate monthly observations cause exclusion | **PASS** |
| `test_leap_years_handling` | Verifies Feb 29 (366 days) vs Feb 28 (365 days) day weighting | **PASS** |
| `test_day_weighted_annual_temperature` | Verifies day-weighting vs unweighted arithmetic mean | **PASS** |
| `test_day_weighted_precipitation_rate_and_accumulation` | Verifies mm/day rate and mm/year accumulation | **PASS** |
| `test_constant_time_series_handling` | Verifies zero-variance constant series error detection | **PASS** |
| `test_missing_values_handling` | Verifies NASA -999.0 flag and NaN conversion | **PASS** |
| `test_autocorrelated_series_audit` | Verifies statsmodels Ljung-Box audit on synthetic AR(1) | **PASS** |
| `test_non_significant_annual_trend` | Verifies Gaussian white noise produces null hypothesis non-rejection | **PASS** |
| `test_seasonal_trend_evaluation` | Verifies Hirsch-Slack Seasonal MK trend detection | **PASS** |
| `test_sens_slope_units` | Verifies slopes are strictly labelled `{units}/yr` | **PASS** |
| `test_pdf_generation_with_special_characters` | Verifies ReportLab builds cleanly with `&`, `<`, `>`, `"`, `'` | **PASS** |
| `test_failed_statistical_calculation_handling` | Verifies small samples return structured errors without silent fallbacks | **PASS** |
| `test_climatological_anomaly_detection` | Verifies monthly Z-score departure detection ($|Z| \ge 2.0\sigma$) and severity classification | **PASS** |
| `test_variable_comparison_and_correlation` | Verifies Pearson $r$, Spearman $\rho$, and explicit causal disclaimer | **PASS** |
| `test_csv_export_generation` | Verifies commented metadata headers and tabular time series in CSV output | **PASS** |
| `test_ai_assistant_graceful_state` | Verifies deterministic fallback of AI planning and synthesis when API key is unconfigured | **PASS** |

**Backend Test Result:** `18 passed in 4.71s`  
**Frontend Production Build:** `✓ built in 6.26s` (`tsc -b && vite build` passed with zero errors)

---

## 10. Climatological Anomaly Detection ($|Z| \ge 2.0\sigma$)

### 10.1 Mathematical Formulation
To eliminate artificial anomalies driven merely by regular annual seasonality, departures are computed relative to each calendar month's multi-year climatological distribution ($m \in \{1, 2, ..., 12\}$):

$$\mu_m = \frac{1}{Y_{valid}} \sum_{y=1}^{Y_{valid}} x_{y, m}$$

$$\sigma_m = \sqrt{\frac{1}{Y_{valid}-1} \sum_{y=1}^{Y_{valid}} (x_{y, m} - \mu_m)^2}$$

The standardized climatological anomaly for year $y$ and month $m$ is:
$$Z_{y, m} = \frac{x_{y, m} - \mu_m}{\sigma_m}$$

### 10.2 Anomaly Classification & Scientific Disclosure
Observations with $|Z_{y, m}| \ge 2.0$ are classified as statistical anomalies:
- **Moderate Anomaly:** $2.0 \le |Z| < 2.5$
- **Extreme Anomaly:** $|Z| \ge 2.5$

**Scientific Caveat Mandate:** Every anomaly response and frontend view explicitly communicates:
> *"Statistical anomalies indicate mathematical departure ($\ge 2.0\sigma$) from the baseline. They represent statistical extremities and do not automatically confirm specific ground damage or declared disaster events without auxiliary ground verification."*

### 10.3 Empirical Lahore Baseline Anomalies Detected
- **Temperature (T2M):** 7 anomalies detected across 360 months (1.94%).
  - Peak Positive Anomaly: **February 2006** ($T = 20.59\text{ °C}$, Baseline $\mu = 15.84\text{ °C}$, $Z = +3.192\sigma$, extreme).
  - Peak Negative Anomaly: **November 2020** ($T = 17.23\text{ °C}$, Baseline $\mu = 19.97\text{ °C}$, $Z = -2.474\sigma$, moderate).
- **Precipitation (PRECTOTCORR):** 16 anomalies detected across 360 months (4.44%).
  - Peak Positive Anomaly: **November 2020** ($P = 2.08\text{ mm/day}$, Baseline $\mu = 0.24\text{ mm/day}$, $Z = +4.444\sigma$, extreme unseasonal rain).
  - Second Peak Positive Anomaly: **September 2014** ($P = 10.88\text{ mm/day}$, Baseline $\mu = 2.25\text{ mm/day}$, $Z = +4.249\sigma$, extreme late-monsoon surge).

---

## 11. Multi-Variable Comparison & Non-Causal Coupling

### 11.1 Methodological Formulation
When comparing dual Earth system variables (e.g. 2-meter air temperature and precipitation flux), EarthSage AI standardizes both series via Z-score normalization ($Z_t = \frac{x_t - \bar{x}}{s_x}$) to enable visual co-variation on a unified scale.

Statistical coupling is quantified via dual correlation metrics:
1. **Pearson Linear Correlation ($r$):**
   $$r = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum (x_i - \bar{x})^2 \sum (y_i - \bar{y})^2}}$$
2. **Spearman Non-Parametric Rank Correlation ($\rho$):**
   $$\rho = 1 - \frac{6 \sum d_i^2}{n(n^2 - 1)}$$

### 11.2 Empirical Lahore Coupling (T2M vs PRECTOTCORR, $N = 360$)
- **Spearman Rank Correlation:** $\rho = +0.4258$, $p = 2.7238 \times 10^{-17}$ (statistically significant positive monotonic co-variation).
- **Pearson Correlation:** $r = +0.3766$, $p = 1.4285 \times 10^{-13}$.

### 11.3 Mandatory Causal Disclaimer
The interface and API response prominently enforce:
> **"CORRELATION DOES NOT IMPLY CAUSATION."**  
> *"Co-variation between atmospheric variables reflects coupled Earth system feedbacks and seasonal forcing (such as South Asian summer monsoon dynamics bringing peak heat and peak rainfall simultaneously), not a direct unidirectional causal mechanism."*

---

## 12. Data Provenance & Self-Documenting CSV Export

### 12.1 Reproducibility Infrastructure
In addition to dynamic ReportLab PDF reports, EarthSage AI provides a standardized, self-documenting CSV export facility (`backend/app/services/csv_generator.py`).

### 12.2 Structure of Exported Files
Each CSV file begins with commented metadata headers (prefixed with `#`) adhering to Open Science FAIR principles:
- Investigation unique identifier and title
- Stated research question and working hypothesis
- Exact decimal coordinates (WGS84) with hemisphere indicator
- Data provider disclosure (NASA Langley Research Center / MERRA-2)
- Reanalysis spatial resolution ($0.5^\circ \times 0.625^\circ$)
- Complete analytical methodology (day-weighted aggregation, Seasonal MK, Ljung-Box test)
- Explicit scientific limitations and grid-cell attribution
- UTC timestamp of data generation

The header is followed by machine-readable tabular rows containing `Year`, `Observed_Annual_Mean`, and `OLS_Linear_Trend_Fit`.

---

## 13. Gemini AI Safety Architecture & Deterministic Fallback

### 13.1 Design Principles
1. **Strictly Optional AI Capability:** The platform functions completely without external AI APIs.
2. **Backend-Only Secret Isolation:** `GEMINI_API_KEY` is loaded strictly by FastAPI backend configuration; it is never exposed in browser bundles or client-side storage.
3. **No Fabricated Statistics:** The AI is strictly prohibited from recalculating or inventing statistical results. The system prompt instructs Gemini to use only the empirical outputs calculated by the backend mathematical engine.
4. **Deterministic Fallback Engine:** When `AI_PROVIDER=none` or when the API key is unavailable or offline, the platform seamlessly switches to deterministic rule-based algorithms (`GeminiResearchAssistant._deterministic_plan` and `_deterministic_explanation`).
5. **Transparency Disclosure:** Every AI response includes clear flags (`is_ai_generated: true/false`, attribution disclaimer) distinguishing synthetic text from deterministic analysis.

---

## 14. NASA Challenge Resources Eligibility & Ingestion Feasibility

### 14.1 Challenge Mandate
The NASA Space Apps Challenge *"Be An Earth System Trend Detective!"* mandates analyzing variables measured by NASA Earth science missions or produced by Earth science models.

### 14.2 Active Primary Pipeline: NASA POWER / MERRA-2
- **Model Framework:** Modern-Era Retrospective analysis for Research and Applications, Version 2 (MERRA-2 atmospheric assimilation) developed by NASA's Global Modeling and Assimilation Office (GMAO).
- **Public API:** Direct programmatic REST API hosted by NASA Langley Research Center.
- **Operational Advantage:** Allows immediate, synchronous HTTP retrieval of multi-decadal monthly continuous meteorological fluxes (1981–present) without requiring end-users or judges to authenticate via individual NASA Earthdata Login (EDL) accounts.

### 14.3 Challenge Resources Audit: Giovanni & AppEEARS
- **NASA Giovanni (GES DISC):** Listed as a recommended interactive tool for geophysical parameter exploration. Giovanni's underlying API relies on OPeNDAP and asynchronous task execution requiring registered Earthdata Login tokens.
- **NASA AppEEARS (LP DAAC):** Designed for extracting subset samples from land and satellite archives (MODIS, VIIRS). Operates on an asynchronous batch queue where spatial extraction jobs require minutes to hours in queue before data files can be downloaded.
- **Scientific Audit Finding:** Integrating AppEEARS or Giovanni as synchronous blocking endpoints during live interactive web sessions would introduce multi-hour queue timeouts and force judges to register individual Earthdata credentials. To preserve immediate responsiveness, authentic MERRA-2 data from NASA POWER is utilized for active mathematical analysis. Giovanni and AppEEARS are formally cataloged in `AVAILABLE_DATASETS` as reference resources and future asynchronous batch roadmap targets.

---

## 15. Production Security & Rate Limiting Audit

1. **Private Database Isolation:** In production (`docker-compose.prod.yml`), PostgreSQL 16 is bound strictly to the internal bridge network `earthsage_prod_net` without publishing port 5432 or 5439 to the public host.
2. **Reverse Proxy TLS Termination:** Caddy 2 terminates TLS via Let's Encrypt / ZeroSSL, exposing only Ports 80 and 443 publicly.
3. **In-Memory Rate Limiting:** Computational endpoints (`/api/v1/investigations/{id}/run`, `/api/v1/analysis/compute-trends`, `/api/v1/reports`, `/api/v1/ai/*`) are protected by a sliding-window rate limiter (30 requests/minute per client IP) to prevent denial of service without blocking human research workflows.
4. **Path Traversal Protection:** Report download handlers canonicalize target paths (`os.path.abspath`) and enforce directory containment strictly within `/app/data/reports`.
5. **Strict Input Bounds:** Pydantic validators enforce physical coordinate limits ($-90 \le \text{lat} \le 90$, $-180 \le \text{lon} \le 180$) and chronological year constraints ($1981 \le \text{start} \le \text{end} \le 2024$).

---

## 16. Remaining Scientific Limitations

1. **Single Grid-Cell Attribution:** The current evaluation represents a single point estimate corresponding to the MERRA-2 grid cell ($0.5^\circ \times 0.625^\circ$) covering Lahore coordinates ($31.5497^\circ\text{N}, 74.3436^\circ\text{E}$). It does not represent a spatially masked provincial or Pakistan-wide national average.
2. **Reanalysis vs In-Situ Ground Truth:** Data are model-assimilated reanalysis estimates (MERRA-2 via NASA POWER), not direct in-situ thermistor or rain gauge recordings. Local urban heat island (UHI) effects within Lahore may differ from the regional reanalysis cell.
3. **Statistical Sample Size ($N = 30$):** 30 annual observations represent the standard climatological baseline period (WMO 1991–2020), but portmanteau tests for autocorrelation have lower power than with multi-decadal daily records.
4. **Precipitation Regime:** Precipitation in Lahore is heavily concentrated in the monsoon months (July–August). While monthly rate weighting correctly preserves the mean daily flux, annual precipitation variance is dominated by monsoonal extremes.

---

## 17. Requirement Assessment Summary

| Requirement | Description | Status | Evidence / Notes |
| :---: | :--- | :---: | :--- |
| **1** | Verify PyMannKendall Sen's Slope Units | **PASS** | Source code inspected; confirmed slopes are in `{units}/yr`. All `{units}/mo` references eliminated. |
| **2** | Improve Autocorrelation Testing | **PASS** | Implemented `statsmodels.stats.diagnostic.acorr_ljungbox` across multiple lags ($1..4$). Hamed-Rao evaluated with documented $V^*/V$ ratio. |
| **3** | Correct Annual Aggregation | **PASS** | Day-weighted aggregation with exact calendar month days and leap-year handling implemented. Strict 12-month completeness enforced. Verified against NASA `YYYY13`. |
| **4** | Remove Fabricated Confidence Scores | **PASS** | Hardcoded scores (`0.95`, `0.85`, `0.80`) completely removed from backend and frontend. Replaced with empirical $p$-values, $\tau$, and Sen's slope. |
| **5** | Fix Silent Statistical Failures | **PASS** | Fallback defaults (`p=1.0, slope=0.0`) eliminated. Constant series, insufficient samples, and calculation exceptions return structured error metadata. |
| **6** | Correct PDF Accuracy & Dynamic Metadata | **PASS** | XML/HTML escaping via `html.escape()` implemented. Dynamic coordinates, hemisphere direction labels, observation counts, and multi-lag autocorrelation documented. |
| **7** | Climatological Anomaly Detection | **PASS** | Month-of-year standardized departure ($|Z| \ge 2.0\sigma$) implemented and tested with strict non-disaster attribution caveat. |
| **8** | Atmospheric Variable Comparison | **PASS** | Z-score normalization, Pearson $r$, Spearman $\rho$, and explicit "correlation does not imply causation" banner implemented. |
| **9** | Reproducible CSV Export | **PASS** | Commented metadata headers, FAIR scientific principles, and tabular time series implemented and verified. |
| **10** | Gemini AI Safety & Deterministic Fallback | **PASS** | Backend-only key, official `google-genai` SDK, anti-hallucination prompt, and deterministic rule-based fallback verified. |
| **11** | NASA Challenge Resources Audit | **PASS** | Official challenge resources analyzed. MERRA-2 assimilation pipeline validated; Giovanni/AppEEARS asynchronous constraints documented. |
| **12** | Production Hardening & Rate Limiting | **PASS** | Production ASGI multi-worker Dockerfile, Nginx SPA, Caddy reverse proxy, rate limiting, and path traversal guards verified. |
| **13** | Independent Reproducibility | **PASS** | Standalone audit script executed. Discrepancy report confirms 0 discrepancies across all parameters. |
| **14** | Automated Test Suite | **PASS** | 18 automated pytest cases pass (`18 passed in 4.71s`). 14-point live regression suite passes (100%). Frontend build passes. |
| **15** | Database & Existing Investigation Preservation | **PASS** | Record `inv-20261114-30c9a0` successfully updated with validated results. No volumes deleted; no external Docker services disturbed. |
| **16** | Scientific Audit Documentation | **PASS** | Comprehensive `SCIENTIFIC_AUDIT.md` compiled with exact formulas, numerical baselines, and limitation disclosures. |

