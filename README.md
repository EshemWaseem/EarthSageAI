# EarthSage AI — Empirical Geospatial Climate Trend Detective

[![NASA Space Apps Challenge](https://img.shields.io/badge/NASA%20Space%20Apps-Be%20An%20Earth%20System%20Trend%20Detective!-blue.svg)](https://www.spaceappschallenge.org/)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.0.0-009688.svg)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/React-18.3.1-61DAFB.svg)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6.svg)](https://www.typescriptlang.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Production%20Ready-2496ED.svg)](https://www.docker.com/)
[![Tests Passing](https://img.shields.io/badge/Tests-25%20Passed-success.svg)](#6-automated-testing--scientific-verification)

> **EarthSage AI** is an authentic scientific research workstation and geospatial analytical platform built for the **NASA International Space Apps Challenge: "Be An Earth System Trend Detective!"**  
> It ingests continuous gridded atmospheric reanalysis from **NASA POWER / MERRA-2**, executes non-parametric statistical hypothesis tests, diagnoses multi-lag serial autocorrelation, detects climatological anomalies, assesses atmospheric variable coupling, and outputs self-documenting research artifacts—with zero fabricated data and transparent scientific provenance.

---

## 1. Project Links & Disclaimers

- **Public Demonstration URL:** `https://earthsage.example.org` *(Ready for deployment via `docker-compose.prod.yml`)*
- **GitHub Repository:** `https://github.com/your-team/earthsage-ai`
- **NASA Space Apps Challenge Page:** [Be An Earth System Trend Detective!](https://www.spaceappschallenge.org/)
- **Non-Endorsement Disclaimer:** *This project is an independent hackathon submission developed for the NASA International Space Apps Challenge. Meteorological and solar data are provided courtesy of the NASA Langley Research Center POWER Project. This application is not formally endorsed by or affiliated with the National Aeronautics and Space Administration (NASA).*

---

## 2. Scientific Philosophy & Design Standards

Unlike typical AI dashboard templates, EarthSage AI is engineered as an **evidence-driven scientific workstation**:

- **Evidence Over Aesthetics:** Completely eliminates purple/cyan neon gradients, glassmorphism, glowing borders, and arbitrary "AI confidence percentage" badges. The UI features restrained high-contrast neutral grey surfaces, clean typography (Inter), and an information-dense 4px layout.
- **Empirical Reproducibility:** Every statistical metric ($p$-values, Kendall's rank correlation $\tau$, Sen's slope, Ljung-Box $Q$, Pearson $r$, Spearman $\rho$) is computed on demand from raw NASA observations and validated against independent numerical scripts.
- **Methodological Transparency:** All unit conventions, leap-year calculations, and spatial resolution limitations are explicitly documented. If data are insufficient or constant, the system halts with structured scientific diagnostics rather than silently defaulting to "no trend."
- **Strict Separation of Correlation and Causation:** Coupled Earth system variables are presented with explicit non-causal disclosures acknowledging external seasonal and synoptic drivers.

---

## 3. Core Scientific Capabilities

### A. Climate Trend Explorer (Dual-Tier Non-Parametric Engine)
- **Seasonal Mann-Kendall (Hirsch-Slack, period=12):** Evaluates monotonic trends across years within corresponding calendar months while rigorously accounting for the annual seasonal cycle.
- **Calendar Day-Weighted Annual Mann-Kendall:** Evaluates net decadal shifts on series aggregated using calendar day-weights ($d_m / 365$ or $d_m / 366$ for leap years). Validated against NASA POWER's raw `YYYY13` daily assimilation aggregates to within $< 0.005$ units.
- **Theil-Sen Median Slope Estimator:** Provides a robust median rate of change resistant to extreme outliers. All slope rates are strictly computed and labelled in **physical units per calendar year (`{units}/yr`)**.
- **Ordinary Least Squares (OLS) Linear Regression:** Evaluated alongside non-parametric metrics to contrast median monotonic slope against mean parametric linear change.

### B. Serial Autocorrelation Diagnostic & Variance Adjustment
- **Multi-Lag Ljung-Box Test ($k = 1, 2, 3, 4$):** Evaluates whether annual time series exhibit significant memory ($p < 0.05$) using `statsmodels.stats.diagnostic.acorr_ljungbox`.
- **Hamed-Rao (1998) Modified Mann-Kendall:** When serial autocorrelation is detected, detrends the series by Sen's slope, evaluates rank autocorrelations against Gaussian critical bounds ($\pm 1.96 / \sqrt{N}$), and calculates the variance expansion factor ($V^*/V$) to prevent false positive trend claims.
- **Small-Sample Limitations Disclosed:** Acknowledges power limitations of portmanteau tests on 30-year climatological normal periods ($N = 30$).

### C. Climatological Anomaly Detection
- **Standardized Monthly Departures ($Z \ge 2.0\sigma$):** Normalizes each observation against its specific calendar month's 30-year mean and standard deviation:
  $$Z_{y,m} = \frac{x_{y,m} - \mu_m}{\sigma_m}$$
- **Disaster Attribution Disclosure:** Clearly distinguishes mathematical statistical outliers ($Z \ge 2.0\sigma$) from ground-level damage or declared natural disasters.

### D. Atmospheric Variable Comparison
- **Unified Z-Score Scale:** Normalizes divergent parameters (e.g., surface temperature `°C` and precipitation rate `mm/day`) into standard deviations to visualize simultaneous co-variation over multi-decadal time spans.
- **Dual Correlation Metrics:** Computes both Pearson linear correlation ($r$) and Spearman non-parametric rank correlation ($\rho$) with two-tailed $p$-values.
- **Prominent Causal Disclaimer:** Highlights that atmospheric co-variation represents planetary-scale monsoon dynamics and thermal feedbacks rather than direct unidirectional causation.

### E. Open Science Research Reports (PDF & CSV)
- **Dynamic ReportLab PDF Generator:** Compiles executive summaries, geographic provenance, observation completeness, statistical metrics, autocorrelation audits, and findings into publication-ready PDFs with XML sanitization (`html.escape()`).
- **Reproducible CSV Data Export:** Generates machine-readable tables accompanied by commented metadata headers (`#`) detailing coordinates, data sources, spatial resolutions, analytical formulas, and limitations according to FAIR scientific data standards.

### F. Google Gemini AI Research Assistant
- **Optional AI Integration:** Built using the official `google-genai` Python SDK.
- **Backend-Only Security:** `GEMINI_API_KEY` is loaded strictly by FastAPI backend configuration; secrets are never bundled or exposed to the client.
- **Hallucination Prevention:** Operates strictly on pre-computed statistical tables from the mathematical engine. Prompts enforce strict fidelity to computed $p$-values, slopes, and sample sizes.
- **Deterministic Offline Fallback:** When `AI_PROVIDER=none` or when the API key is unconfigured, the platform seamlessly runs rule-based planning and synthesis routines without service disruption.

### G. Production JWT Authentication & Session Security
- **PostgreSQL User & Session Models:** `users` table (`id` UUID, `full_name`, `email` unique index, `password_hash`, `is_active`, timestamps) and `refresh_tokens` table (`id`, `user_id`, `token_hash` SHA-256, `expires_at`, `revoked`, `created_at`).
- **Cryptographic Password Hashing:** Passwords hashed with bcrypt (12 rounds) or Argon2id. Plaintext passwords and raw refresh tokens are never persisted in the database.
- **In-Memory JWT Access Tokens:** 15-minute expiration, HS256 algorithm. Kept strictly in frontend memory (JavaScript closure) rather than `localStorage`, preventing XSS token exfiltration.
- **HttpOnly Refresh Cookies:** 7-day cryptographic tokens stored as SHA-256 hashes in PostgreSQL and transmitted exclusively via `HttpOnly`, `SameSite=Lax`, and `Secure` cookie attributes.
- **Token Rotation & Replay Theft Detection:** Every `/api/auth/refresh` request revokes the incoming refresh token and issues a fresh replacement. If an already-revoked token is submitted, the system flags a theft condition and revokes all sessions for that user.
- **Data Isolation & Research Attribution:** Investigations created by logged-in researchers are tagged with `user_id` and restricted from unauthorized mutation/execution (HTTP 403 Forbidden). Baseline studies (`user_id is NULL`) remain accessible to all authenticated researchers.
- **Automated Silent Refresh:** The frontend HTTP interceptor automatically intercepts 401 Unauthorized responses, requests a fresh access token via HttpOnly cookie, and retries the original request seamlessly.

---

## 4. NASA Data Source Eligibility & Challenge Resources Audit

### Challenge Mandate Alignment:
The NASA Space Apps Challenge **"Be An Earth System Trend Detective!"** tasks participants with selecting variables measured by NASA Earth science missions or produced by Earth science models, visualizing changes over time, and evaluating statistical significance.

### Evaluated Data Sources:
1. **NASA POWER / MERRA-2 (Active Implementation):**
   - **Provider:** NASA Langley Research Center / Global Modeling and Assimilation Office (GMAO).
   - **Mission/Model:** Modern-Era Retrospective analysis for Research and Applications, Version 2 (MERRA-2 atmospheric assimilation).
   - **Why Selected:** MERRA-2 integrates satellite observations with advanced numerical modeling to produce a continuous, global meteorological record (1981–present). NASA POWER provides a dedicated public REST API allowing synchronous, real-time query execution for instant user investigation workflows without authentication gates.
2. **NASA Giovanni (GES DISC) & AppEEARS (Challenge Resources Audit):**
   - **Giovanni:** Listed on the challenge Resources tab as an interactive exploratory visualization tool. Programmatic API access requires NASA Earthdata Login (EDL) user credentials, asynchronous job submission, and NetCDF OPeNDAP parsing.
   - **AppEEARS:** Listed on the challenge Resources tab for extracting analysis-ready samples (MODIS, VIIRS). Operates on an asynchronous batch queue where tasks often wait in queue for multi-hour processing.
   - **Eligibility & Roadmap Classification:** To deliver reliable, sub-second interactive analysis during live hackathon evaluation without requiring each judge to register an individual Earthdata Login account, EarthSage AI utilizes NASA POWER's MERRA-2 assimilation model as its primary real-time pipeline. Giovanni and AppEEARS are documented in the application dataset catalog as future batch-queue integrations.

---

## 5. System Architecture

```
                                  +---------------------------------------+
                                  |         NASA POWER REST API           |
                                  |  MERRA-2 Gridded Atmospheric Flux     |
                                  +---------------------------------------+
                                                      |
                                                      v [Async HTTP Client]
+---------------------------------------------------------------------------------------------------+
| EarthSage AI Backend (FastAPI - Python 3.11)                                                      |
|                                                                                                   |
|  [Data Cleaning & Verification] ---> [Calendar Day-Weighted Aggregation Engine]                  |
|                                              |                                                    |
|                                              +---> [Seasonal Mann-Kendall Engine (Hirsch-Slack)]   |
|                                              +---> [Annual Mann-Kendall Engine (Standard)]        |
|                                              +---> [Multi-Lag Autocorrelation Audit (Ljung-Box)]  |
|                                              +---> [Hamed-Rao Variance Adjustment (V*/V)]         |
|                                              +---> [Climatological Anomaly Detector (|Z| >= 2.0)] |
|                                              +---> [Variable Comparator (Pearson r & Spearman rho)]|
|                                              |                                                    |
|  [ReportLab Dynamic PDF] <-------------------+---> [FAIR-Compliant Commented CSV Generator]       |
|  [Gemini AI Assistant (google-genai SDK)] <---+---> [Deterministic Scientific Fallback Planner]   |
+---------------------------------------------------------------------------------------------------+
       |                                                                     |
       v [SQLAlchemy 2.0]                                                    v [REST API - Port 8000/8020]
+-------------------------------+                                 +---------------------------------+
| PostgreSQL 16 Relational DB   |                                 | React 18 + TypeScript + Vite    |
| Port: 5439 (Dev) / 5432 (Prod)|                                 | Port: 5174 (Dev) / 80 (Prod)    |
| Isolated Private Network      |                                 | Tailwind CSS + Recharts         |
+-------------------------------+                                 +---------------------------------+
```

---

## 6. Automated Testing & Scientific Verification

EarthSage AI includes a rigorous multi-tier automated test suite covering mathematical data cleaning, leap-year calculations, non-parametric statistics, autocorrelation audits, report generation, AI fallbacks, and JWT authentication:

### 1. Scientific Statistical Engine Test Suite (18 tests):
```bash
docker exec earthsage-backend bash -c "export PYTHONPATH=/app; pytest /app/tests/test_scientific_engine.py"
```
**Result:** `18 passed in ~12s (100% pass rate)`.

### 2. JWT Authentication & Security Test Suite (7 tests):
```bash
docker exec earthsage-backend bash -c "export PYTHONPATH=/app; pytest /app/tests/test_auth.py"
```
**Result:** `7 passed in ~25s (100% pass rate)`. Verifies bcrypt password hashing, JWT issue/decode, refresh token rotation, replay theft detection, unauthenticated rejection, and cross-user data isolation.

### 3. Live End-to-End Regression Suite (14 Verification Points):
```bash
docker exec earthsage-backend python /app/tests/run_e2e_regression.py
```
**Result:** `ALL 14 E2E FUNCTIONAL & SCIENTIFIC REGRESSION TESTS PASSED (100% VERIFIED)`.

### 4. Live Authentication & Data Isolation E2E Demo Flow (11 Steps):
```bash
docker exec earthsage-backend python /app/scripts/verify_auth_e2e_demo.py
```
**Result:** `ALL 11 AUTHENTICATION & DATA ISOLATION VERIFICATION STEPS PASSED (100%)`.

### 5. Frontend Production Build & Type Checking:
```bash
docker exec earthsage-frontend npm run build
```
**Result:** `✓ built in ~7s (0 TypeScript errors)`.

---

## 7. Validated Numerical Benchmark: Lahore (1991–2020)

To provide an independently auditable scientific baseline, the system includes a 30-year climatological investigation covering the Lahore, Pakistan grid cell ($31.5497^\circ\text{N}, 74.3436^\circ\text{E}$):

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
| **PRECTOTCORR** | Day-Weighted Annual Mean | $1.4952 \text{ mm/d}$ | $1.4952 \text{ mm/d}$ | $0.0000$ |
| **PRECTOTCORR** | Annual MK Tau ($\tau$) | $+0.3379$ | $+0.3379$ | $0.0000$ |
| **PRECTOTCORR** | Annual MK $p$-value | $0.009193$ | $0.009193$ | $0.0000$ |
| **PRECTOTCORR** | Annual Sen's Slope | $+0.025846 \text{ mm/d/yr}$ | $+0.025846 \text{ mm/d/yr}$ | $0.0000$ |
| **PRECTOTCORR** | Seasonal MK $p$-value | $0.000178$ | $0.000178$ | $0.0000$ |
| **PRECTOTCORR** | Seasonal MK Sen's Slope | $+0.010000 \text{ mm/d/yr}$ | $+0.010000 \text{ mm/d/yr}$ | $0.0000$ |

For comprehensive mathematical proofs, autocorrelation matrices, and verification scripts, inspect [`SCIENTIFIC_AUDIT.md`](./SCIENTIFIC_AUDIT.md).

---

## 8. Local Development Setup

To run locally in development mode:

### Port Allocation:
| Service | Port | Description |
| :--- | :--- | :--- |
| **Frontend** | `5174` | React 18 + Vite development interface |
| **Backend API** | `8020` | FastAPI application (`/docs`, `/redoc`, `/health`) |
| **PostgreSQL** | `5439` | PostgreSQL 16 database |

### Launch Commands:
```bash
# 1. Copy development environment file
cp .env.example .env

# 2. Start containers
docker-compose up -d --build

# 3. Access web application
open http://localhost:5174
```

---

## 9. Production Deployment Guide (Ubuntu 24.04 VPS)

EarthSage AI includes a production-hardened Docker Compose stack (`docker-compose.prod.yml`) utilizing Caddy reverse proxy, Let's Encrypt automated TLS, multi-worker ASGI backend, and isolated PostgreSQL networking.

### Hardware Prerequisites:
- **OS:** Ubuntu 22.04 LTS or 24.04 LTS (x86_64)
- **Minimum Specs:** 1 vCPU, 2 GB RAM, 25 GB SSD
- **Recommended Specs:** 2 vCPUs, 4 GB RAM, 50 GB SSD
- **Network:** Public IPv4 address, inbound Ports 80 and 443 open in firewall

### Step 1: Server Initialization & Firewall Setup
Connect via SSH to your fresh VPS:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git ufw

# Configure UFW firewall (restrict everything except SSH, HTTP, and HTTPS)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Step 2: Install Docker & Docker Compose
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
docker --version
```

### Step 3: Clone Repository & Configure Production Environment
```bash
git clone https://github.com/your-team/earthsage-ai.git /opt/earthsage
cd /opt/earthsage

# Copy production environment configuration template
cp .env.production.example .env.production
```

Edit `.env.production` using `nano`:
```bash
nano .env.production
```
Configure your domain and credentials:
```env
DOMAIN=earthsage.yourdomain.org
ACME_EMAIL=admin@yourdomain.org
POSTGRES_DB=earthsage
POSTGRES_USER=earthsage_user
POSTGRES_PASSWORD=generate_a_secure_24_char_password_here
CORS_ORIGINS=https://earthsage.yourdomain.org
AI_PROVIDER=none
```

### Step 4: Configure DNS Records
In your domain registrar / DNS provider, create an **A Record**:
- **Host:** `earthsage` (or `@`)
- **Points to:** Your VPS public IPv4 address (e.g. `123.45.67.89`)
- **TTL:** 300 seconds

### Step 5: Launch Production Stack
```bash
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```

### Step 6: Verify Deployment & HTTPS
```bash
# Check container status
docker ps

# Check proxy logs for Let's Encrypt certificate acquisition
docker logs earthsage-prod-proxy

# Verify health endpoint via curl
curl -k https://localhost/health
```

### Step 7: Database Backup & Restore Procedures
- **Create Backup:**
  ```bash
  docker exec earthsage-prod-postgres pg_dump -U earthsage_user earthsage > /opt/backups/earthsage_$(date +%F).sql
  ```
- **Restore Backup:**
  ```bash
  cat backup_file.sql | docker exec -i earthsage-prod-postgres psql -U earthsage_user -d earthsage
  ```

### Step 8: Production Rollback Procedure
```bash
# If an update fails, rollback to previous git tag or commit:
git checkout <previous-tag>
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```

---

## 10. Third-Party Libraries & Acknowledgments

| Component | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Frontend Framework** | React | `18.3.1` | Scientific component rendering |
| **Type Safety** | TypeScript | `5.5.3` | Rigorous static typing |
| **Build Tooling** | Vite | `5.4.2` | Fast production compilation |
| **Visual Charts** | Recharts | `2.12.7` | Non-parametric time series & Z-score charts |
| **Icons** | Lucide React | `0.344.0` | Restrained functional UI icons |
| **Backend Framework** | FastAPI | `0.115.0+` | Asynchronous REST API |
| **ASGI Server** | Gunicorn + Uvicorn | `27.0.1` | Production multi-worker execution |
| **Relational ORM** | SQLAlchemy | `2.0+` | Type-safe persistence |
| **Statistical Engine** | PyMannKendall | `1.4.3` | Hirsch-Slack Seasonal & Sen's slope |
| **Time Series Diagnostics**| Statsmodels | `0.14+` | Multi-lag Ljung-Box autocorrelation test |
| **Numerical Computing** | SciPy & NumPy | `1.14+` / `2.0+` | Pearson $r$, Spearman $\rho$, distributions |
| **Data Cleaning** | Pandas | `2.2+` | Day-weighted annual aggregation |
| **Report Generation** | ReportLab | `4.2+` | Dynamic PDF compilation with XML escaping |
| **AI SDK** | Google Gen AI | `0.1+` | Official Python SDK for Gemini 2.5 Flash |
| **Reverse Proxy** | Caddy | `2.8` | Automated TLS & HTTP/3 reverse proxy |
| **Database** | PostgreSQL | `16` | Relational store with pre-ping connection pool |

---

## 11. Hackathon Demonstration Guide

For judges and reviewers conducting an evaluation of EarthSage AI for the NASA Space Apps Challenge, consult [`HACKATHON_DEMO.md`](./HACKATHON_DEMO.md) for a structured 7-step walkthrough script and scientific defense guide.

---

## 12. License

This project is licensed under the Apache 2.0 License. NASA POWER data are provided courtesy of the NASA Langley Research Center POWER Project.
