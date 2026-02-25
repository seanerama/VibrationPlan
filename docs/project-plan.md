# Project Plan: VME Compatibility Analyzer

**Version**: 1.0.0

---

## Vision

A hosted, browser-based internal tool that ingests RVTools or CloudPhysics VM inventory exports, automatically classifies each VM against the HPE VM Essentials (VME) compatibility matrix, and produces a branded, color-coded Excel spreadsheet with migration path guidance for customer delivery. Eliminates manual cross-referencing by US Signal Solutions Architects and ensures consistent, professional output for every VME pre-sales engagement.

---

## Features

**File Upload & Detection**
- Accepts RVTools (.xlsx) and CloudPhysics (.xlsx) export formats
- Auto-detects format based on column headers
- Synchronous processing (files expected under 10MB)

**OS Parsing**
- RVTools: Uses "OS according to VMware Tools" as primary, "OS according to configuration file" as fallback when primary is empty/null; both columns preserved in output
- CloudPhysics: Uses "Guest OS" column
- Fuzzy matching to normalize OS strings before classification

**VM Classification Engine**
Classifies each VM into one of 6 tiers:

| Tier | Color Name | Hex | Row Bg Tint | Logic |
|---|---|---|---|---|
| Officially Supported | Emerald | `#10B981` | `#052E1A` | Exact/version-range match in VME Guest OS matrix |
| Unofficially Supported | Teal | `#14B8A6` | `#042322` | KVM-compatible OS not in HPE-validated list |
| Supported VDI VM | Teal (same) | `#14B8A6` | `#042322` | Matches ISV VDI table (Citrix, Omnissa Horizon, HP Anyware) |
| Needs Review with Customer | Amber | `#F59E0B` | `#2D1A00` | OS identified but version ambiguous; unsupported but may work |
| Needs Additional Info | Brand Blue | `#0028FA` | `#00082F` | Insufficient OS string to classify (e.g., "Other Linux") |
| Not Supported | Rose | `#F43F5E` | `#2D0A14` | KVM-incompatible OS (Windows XP/Vista/2003, pre-3.x Linux kernels, DOS, OS/2, Netware, non-x86-64 architectures) |

**Classification Reason** field explains exactly why each VM landed in its tier.

**Output Spreadsheet (3 tabs)**
- **VM Detail**: One row per VM — VM Name, Host/Cluster, OS (Raw), OS (Interpreted), Classification, Classification Color, Classification Reason, Migration Path, Notes
- **Summary**: Count and percentage per classification tier, with color coding
- **Executive Summary**: Narrative-ready summary paragraph + key stats suitable for customer-facing use

**Migration Path Guidance**
Fixed lookup table by classification tier, with light branching by OS family where relevant. Authored and stored in app config, editable via admin UI.

**US Signal Branding on Output**
- Logo in spreadsheet header (asset: `USSBlueBurst.png` — place on dark background `#0A0D12`)
- Brand blue: `#0028FA` — primary actions, badges, active states
- Dark background: `#0A0D12`, surface: `#111827`
- Typography: DM Serif Display (headings), IBM Plex Sans (body/UI), IBM Plex Mono (data/VM names)
- Optional customer name field injected into output header and output filename

**Admin Matrix Management UI (`/admin`)**
- No authentication (internal tool)
- View current VME compatibility matrix entries
- Add, edit, or remove Guest OS entries
- Update migration path guidance text per tier
- Changes take effect immediately (no activation step)
- Matrix stored in persistent database, not hardcoded

---

## Tech Stack

| Layer | Technology | Rationale |
|---|---|---|
| Frontend | React (Vite) + CSS Custom Properties | Fast, modern SPA; design system uses CSS vars — no Tailwind required |
| Backend | Python (FastAPI) | Excellent xlsx/pandas support; fast async API |
| Database | Azure SQL (Basic tier) | Persistent matrix storage; fits Azure deployment target |
| File Processing | pandas + openpyxl | RVTools/CloudPhysics parsing and output generation |
| OS Fuzzy Matching | rapidfuzz | Robust string matching for inconsistent OS strings |
| Hosting | Azure App Service (Linux, B1) | Fits existing Azure subscription; easy SSO hookup for v2 |
| Static Assets | Served from App Service | No separate CDN needed at this scale |
| Secrets | Azure App Service Environment Variables | Standard Azure approach |

---

## Architecture

```
Browser (React SPA)
    │
    │  HTTP (multipart upload + JSON)
    ▼
FastAPI Backend (Azure App Service)
    ├── /api/analyze        → File upload, parse, classify, return xlsx
    ├── /api/admin/matrix   → CRUD for VME compatibility matrix
    └── /api/admin/migration-paths → CRUD for migration path text
    │
    ├── FileParser          → Detects format, extracts VM rows
    ├── OSNormalizer        → Fuzzy matching, OS string normalization
    ├── ClassificationEngine → Tier assignment + reason generation
    ├── OutputBuilder       → Generates branded xlsx (3 tabs)
    │
    ▼
Azure SQL Database
    ├── vme_matrix          → OS entries and classification tier
    └── migration_paths     → Guidance text per tier/OS family
```

All processing is synchronous. No job queue needed at this scale. The output xlsx is returned directly as a file download response.

---

## Project Structure

```
vme-analyzer/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UploadForm.jsx          # File upload + customer name input
│   │   │   ├── ResultsPreview.jsx      # Classification summary before download
│   │   │   └── AdminMatrix.jsx         # Matrix management UI
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   └── Admin.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── public/
│   │   └── assets/
│   │       └── uss-logo.png            # PLACEHOLDER — swap with real asset
│   ├── index.html
│   └── vite.config.js
│
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI app, route registration
│   │   ├── routers/
│   │   │   ├── analyze.py              # /api/analyze endpoint
│   │   │   └── admin.py                # /api/admin/* endpoints
│   │   ├── services/
│   │   │   ├── file_parser.py          # RVTools/CloudPhysics detection + extraction
│   │   │   ├── os_normalizer.py        # Fuzzy matching + OS string normalization
│   │   │   ├── classification_engine.py # Tier assignment logic
│   │   │   └── output_builder.py       # xlsx generation (3 tabs, branding)
│   │   ├── models/
│   │   │   ├── database.py             # SQLAlchemy setup
│   │   │   ├── vme_matrix.py           # VME matrix ORM model
│   │   │   └── migration_paths.py      # Migration path ORM model
│   │   └── config.py                   # Settings from env vars
│   ├── tests/
│   │   ├── test_file_parser.py
│   │   ├── test_os_normalizer.py
│   │   ├── test_classification_engine.py
│   │   └── test_output_builder.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── docs/
│   ├── project-plan.md                 # This file
│   ├── project-state.md                # Living state doc (updated by Stage Managers)
│   ├── deploy-instruct.md              # Deployment prompt
│   └── design-system.md                # UI/UX design system — source of truth for all frontend work
│
├── .env.example
└── README.md
```

---

## Data Models

### `vme_matrix`
| Column | Type | Notes |
|---|---|---|
| id | INT PK | Auto-increment |
| os_vendor | VARCHAR(100) | e.g., "Microsoft", "RHEL" |
| os_family | VARCHAR(100) | e.g., "Windows Server", "RHEL" |
| os_versions | VARCHAR(500) | Comma-separated version strings, e.g., "2016,2019,2022,2025" |
| classification_tier | VARCHAR(50) | One of the 6 tier keys |
| notes | TEXT | Optional — e.g., "HPE validated" |
| updated_at | DATETIME | Last modified timestamp |

### `migration_paths`
| Column | Type | Notes |
|---|---|---|
| id | INT PK | Auto-increment |
| classification_tier | VARCHAR(50) | FK to tier key |
| os_family | VARCHAR(100) | NULL = applies to all OS families in this tier |
| guidance_text | TEXT | The migration path sentence(s) shown in output |
| updated_at | DATETIME | Last modified timestamp |

---

## Classification Logic (Detailed)

**Step 1 — OS Extraction**
Extract raw OS string from the appropriate column(s) based on detected file format.

**Step 2 — OS Normalization**
Apply rapidfuzz matching against known OS patterns to produce a normalized OS name and version. Flag as "Needs Additional Info" if confidence score is below threshold (suggested: 70).

**Step 3 — Tier Assignment**
```
IF normalized OS matches vme_matrix with classification_tier = "officially_supported"
    → Officially Supported

ELSE IF normalized OS matches ISV VDI products (Citrix, Omnissa Horizon, HP Anyware)
    → Supported VDI VM

ELSE IF normalized OS is in known KVM-compatible list (Debian, Fedora, older Ubuntu, etc.)
    → Unofficially Supported

ELSE IF OS is identified but version is ambiguous or edge case
    → Needs Review with Customer

ELSE IF OS string is too vague to classify (e.g., "Other Linux", "Unknown")
    → Needs Additional Info

ELSE IF OS is in known KVM-incompatible list (Windows XP/Vista/2003, DOS, OS/2, Netware, etc.)
    → Not Supported
```

**Step 4 — Reason Generation**
Produce a human-readable Classification Reason string explaining the decision (e.g., "Matched Windows Server 2022 — HPE validated", "OS family recognized as KVM-compatible but not HPE-tested", "OS string 'Other Linux' lacks sufficient detail").

**Step 5 — Migration Path Lookup**
Query `migration_paths` for matching tier + OS family. Fall back to tier-level guidance if no OS-family-specific row exists.

---

## Migration Path Content (Seed Data)

These are the initial values to seed at deployment. Editable via admin UI post-deployment.

| Tier | Migration Path |
|---|---|
| Officially Supported | VM is HPE-validated and ready for migration to HPE VME with no OS changes required. Proceed with standard P2V migration tooling. |
| Unofficially Supported | OS is KVM-compatible but not HPE-validated. Migration is likely to succeed but HPE support coverage may be limited. Recommend testing in a non-production environment before full migration. |
| Supported VDI VM | VM is running a validated VDI workload (Citrix, Omnissa Horizon, or HP Anyware) and is supported on HPE VME. Proceed with standard VDI migration procedures. |
| Needs Review with Customer | OS was identified but version information is ambiguous or incomplete. Review with customer to confirm exact OS version before making a migration recommendation. |
| Needs Additional Info | Insufficient OS data to classify this VM. Gather additional information from the customer (exact OS name and version) and re-run analysis. |
| Not Supported | OS is not compatible with the KVM hypervisor underlying HPE VME. Options: (1) upgrade OS to a supported version before migration, (2) re-platform to a supported OS, or (3) retain on existing VMware infrastructure. |

---

## External Integrations

None in v1. The compatibility matrix is maintained internally via the admin UI. No external API calls at runtime.

---

## Deployment Target

Azure App Service (Linux, B1 tier) in an existing US Signal Azure subscription. Backend and frontend served from a single App Service. Azure SQL Basic tier for database. Full details in `docs/deploy-instruct.md`.

---

## Standards

### Logging
- **Format**: Structured JSON logs
- **Levels**: DEBUG (local only), INFO (normal operations), WARNING (fuzzy match below threshold, unexpected OS strings), ERROR (parse failures, DB errors)
- **Location**: stdout → Azure App Service Log Stream
- **Key events to log**: File upload received (format detected, row count), classification complete (summary counts per tier), admin matrix update (who/what changed — timestamp only since no auth)

### Error Handling
- **API errors**: Return JSON `{ "error": true, "code": "ERROR_CODE", "message": "Human-readable message" }`
- **Parse failures**: Return 400 with specific error (unrecognized format, missing required columns)
- **Classification errors on individual rows**: Never fail the whole batch — assign "Needs Additional Info" tier with reason "Parse error: [detail]" and continue
- **Database errors**: Return 500, log full stack trace
- **Frontend**: Display user-friendly error messages; never expose raw stack traces

### Authentication
None in v1. `/admin` is open but internal. Plan for Azure AD SSO integration in v2.

### Code Style
- **Python**: PEP 8, enforced via `ruff`. Type hints required on all function signatures. Docstrings on all public functions.
- **JavaScript/React**: ESLint + Prettier. Functional components only. No class components.
- **Naming**: snake_case for Python, camelCase for JS, kebab-case for CSS classes.
- **Imports**: Absolute imports only (no relative `../../../`).

### Testing
- **Framework**: pytest (backend), Vitest (frontend)
- **Coverage target**: 80% on classification engine and OS normalizer (the critical path)
- **Naming convention**: `test_[function_name]_[scenario]` (e.g., `test_classify_windows_xp_returns_not_supported`)
- **Required tests per stage**: Each Stage Manager must write tests before marking a stage complete
- **Test data**: Include sample RVTools and CloudPhysics xlsx files in `tests/fixtures/`

---

## Secrets Management

Use Azure App Service Environment Variables (equivalent to `.env` at runtime). Stage Managers should reference a `.env.example` file at repo root. Never commit secrets to git.

Required environment variables:
```
DATABASE_URL=         # Azure SQL connection string
AZURE_SQL_SERVER=     # Server hostname
AZURE_SQL_DATABASE=   # Database name
AZURE_SQL_USERNAME=   # DB username
AZURE_SQL_PASSWORD=   # DB password
ENVIRONMENT=          # "development" or "production"
```

---

## Constraints & Considerations

- **Data sensitivity**: VM inventory files contain customer infrastructure details. No files should be persisted server-side — process in memory and discard immediately after generating output.
- **File size**: Max 10MB upload enforced at API layer.
- **OS string inconsistency**: The OS normalizer is the highest-risk component. The "Needs Additional Info" and "Needs Review" tiers are intentional safety nets — prefer over-flagging to under-flagging.
- **Matrix updates**: When HPE releases a new compatibility matrix, an SA manually reviews the changes and updates entries via the admin UI. No automated scraping.
- **Browser compatibility**: Target Chrome and Edge (internal SA team uses Windows/Mac with modern browsers).

---

## Out of Scope (v1)

- Customer login or customer-facing portal
- Authentication / SSO (v2)
- Customer logo on output
- Automated matrix update detection or web scraping
- Support for VM export formats beyond RVTools and CloudPhysics
- VM right-sizing or performance analysis
- Audit trail / usage logging per SA
- Email delivery of output
