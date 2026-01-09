# AI-Assisted Development Framework v2

## Overview

A streamlined, git-driven framework for building complex software using AI coding assistants. The Vision Lead (human) collaborates with specialized AI sessions through defined checkpoints, with work organized into parallel-capable stages that update a living project state document.

## Core Principles

- **Human-Centered Coordination**: The Vision Lead is the hub, working directly with each AI role
- **Stage-Based Development**: Work is divided into bounded stages with natural test/review checkpoints
- **Living Documentation**: A single project state document evolves with each stage completion
- **Git as Source of Truth**: Git history captures project evolution; no redundant documentation
- **Parallel When Possible**: Independent stages can run concurrently

## Roles

### Vision Lead (VL)
- **Type**: Human (you)
- **Responsibility**: Central decision-maker, works directly with every AI session
- **Activities**:
  - Explores ideas with Vision Assistant
  - Co-designs project with Lead Architect
  - Co-plans stages with Project Planner
  - Reviews stage completions
  - Decides when to invoke Project Tester
  - Decides when to deploy
  - Commits instruction docs and major plan revisions (with PP)

### Vision Assistant (VA)
- **Type**: AI Session #0 (optional)
- **Responsibility**: Help VL explore and clarify rough ideas before architecture
- **Output**: `vision-document.md` (problem, users, core value, features, risks)
- **Invoked**: 
  - When VL has a rough idea that needs development
  - When VL is unsure what they actually want
  - When VL wants to think through an idea before committing
- **Session Ends**: When VL has a clear vision document to take to Lead Architect

### Lead Architect (LA)
- **Type**: AI Session #1
- **Responsibility**: Co-design the project foundation and deployment strategy with the Vision Lead
- **Output**: 
  - `project-plan.md` (architecture, tech stack, features, structure)
  - `deploy-instruct.md` (deployment prompt for Project Deployer)
- **Invoked**: 
  - Project start
  - Major roadblocks requiring architectural redesign
  - Deployment strategy changes (new platform, scaling needs)
- **Session Ends**: After project plan and deploy prompt are approved (re-invoked only if needed)

### Project Planner (PP)
- **Type**: AI Session #2
- **Responsibility**: Break the project into stages, create Stage Manager instructions
- **Output**: 
  - Stage breakdown and sequencing
  - `stage-N-instruct.md` files for each stage
- **Invoked**: 
  - After project plan exists
  - After each stage completes (to review and plan next stages)
- **Scaling**: Multiple PPs in a hierarchy for extremely complex projects

### Stage Manager (SM)
- **Type**: AI Session #N (one per stage)
- **Responsibility**: Implement a stage, write tests, update living documentation
- **Output**:
  - Working code committed to repository
  - Tests for the stage
  - Updated `project-state.md`
- **Invoked**: When their `stage-N-instruct.md` is ready
- **Commits**: Their own code and living doc updates

### Project Tester (PT)
- **Type**: AI Session #3
- **Responsibility**: Test and troubleshoot after stages or pipelines complete
- **Output**: Test results, bug reports, fix recommendations
- **Invoked**: At VL's discretion, typically when:
  - A pipeline connecting multiple stages is complete
  - N+1 stages have been completed
  - Before major deployments

### Feature Manager (FM)
- **Type**: AI Session (as needed)
- **Responsibility**: Assess mid-development feature requests and draft insertion plans
- **Input**: `project-plan.md`, `project-state.md`, stage instructions, the feature request
- **Output**: 
  - Feature Assessment (impact analysis, risk classification)
  - Feature Plan (if low/medium risk)
- **Invoked**: When a new feature idea comes up during development
- **Flow**:
  1. FM assesses impact and risk
  2. VL + LA review the assessment/plan
  3. If approved → PP integrates into stages
- **Escalates to LA**: If feature requires architectural changes

### Project Deployer (PD)
- **Type**: AI Session #4
- **Responsibility**: Deploy the system using available infrastructure
- **Access**: MCP servers (Cloudflare, GitHub, Render, etc.)
- **Input**: `project-plan.md` + `deploy-instruct.md`
- **Invoked**: When VL decides system is ready for deployment

### Security Auditor (SA)
- **Type**: AI Session (as needed)
- **Responsibility**: Review the system for security vulnerabilities and risks
- **Input**: `project-plan.md`, `project-state.md`, codebase, configs
- **Output**: Security audit report with findings and recommendations
- **Invoked**: 
  - Before major deployments
  - After significant new functionality
  - On version bumps (optional but recommended)
  - When security concerns arise

## Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                         PROJECT START                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  VL + Vision Assistant (optional)               │
│             Explore idea, clarify problem, define scope         │
│                              │                                  │
│                              ▼                                  │
│                  Output: vision-document.md                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VL + Lead Architect                          │
│         Design architecture, tech stack, deployment             │
│                              │                                  │
│                              ▼                                  │
│           Output: project-plan.md + deploy-instruct.md          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VL + Project Planner                         │
│            Break project into stages, define order              │
│            Identify parallel vs sequential stages               │
│                              │                                  │
│                              ▼                                  │
│              Output: stage-N-instruct.md files                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Stage Manager(s) Execute                        │
│                                                                 │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│   │     SM 1     │    │     SM 2     │    │     SM 3     │     │
│   │  (stage 1)   │    │  (stage 2)   │    │  (stage 3)   │     │
│   │              │    │  [parallel]  │    │  [parallel]  │     │
│   └──────┬───────┘    └──────┬───────┘    └──────┬───────┘     │
│          │                   │                   │              │
│          ▼                   ▼                   ▼              │
│      Implement           Implement           Implement          │
│      Write tests         Write tests         Write tests        │
│      Update state        Update state        Update state       │
│      Commit & push       Commit & push       Commit & push      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 VL + PP Review Completion                       │
│                                                                 │
│    • Review project-state.md updates                            │
│    • Decide: invoke Project Tester? (especially after           │
│      pipelines connect or n+1 stages complete)                  │
│    • Plan next stage instructions or adjustments                │
│    • Commit updated instruction docs                            │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        [More stages]   [Test pipeline]   [Deploy]
              │               │               │
              ▼               ▼               ▼
         Loop back      VL + Project     VL + Project
         to Stage       Tester           Deployer
         Managers       Session          Session
```

## File Structure

The codebase uses the **natural structure** defined by VL + LA. No artificial stage folders — stages are a coordination concept, not a folder hierarchy.

```
project-root/
├── docs/
│   ├── vision-document.md           # VL + VA output (optional, pre-architecture)
│   ├── project-plan.md              # VL + LA output (architecture, stack, features)
│   ├── project-state.md             # Living doc, updated by SMs after each stage
│   ├── deploy-instruct.md           # Instructions for Project Deployer
│   ├── stage-instructions/
│   │   ├── stage-1-instruct.md      # VL + PP create these
│   │   ├── stage-2-instruct.md
│   │   └── ...
│   └── contracts/                   # PP creates interface contracts
│       ├── user-api-contract.md
│       └── ...
├── src/                             # Project source (structure from project-plan.md)
│   └── [whatever LA + VL defined]
├── tests/                           # Test files (SMs write these)
├── .env.example                     # Environment template (committed)
├── .env                             # Actual secrets (git-ignored)
└── [other dirs as defined in project-plan.md]
```

## Document Specifications

### vision-document.md
Created by VL + Vision Assistant (optional). Contains:

```markdown
# Vision Document: [Project Name]

## The Idea (One Sentence)
[Clear, concise statement of what this is]

## The Problem
[What problem this solves and for whom]

## Target Users
[Who this is for — be specific]
[Who this is NOT for]

## Core Value Proposition
[Why someone would use this over alternatives]

## Key Features (v1)
[Essential features for a useful first version]

## Out of Scope (for now)
[What we're explicitly not building yet]

## Success Criteria
[How we'll know if this worked]

## Open Questions
[Things we still need to figure out]

## Risks & Concerns
[What could go wrong or needs careful thought]

## Personal Motivation
[Why the Vision Lead wants to build this]
```

### project-plan.md
Created by VL + Lead Architect. Contains:

```markdown
# Project Plan: [Project Name]

**Version**: [X.Y.Z]

## Vision
[2-3 sentence project description]

## Features
- Feature 1: [description]
- Feature 2: [description]
- ...

## Tech Stack
- Language: [e.g., Python 3.12]
- Framework: [e.g., FastAPI]
- Database: [e.g., PostgreSQL]
- Infrastructure: [e.g., Docker, Cloudflare Workers]
- ...

## Architecture
[High-level architecture description]
[Diagrams if helpful]

## Project Structure
```
src/
├── [defined folder structure]
```

## External Integrations
- [API 1]: [purpose]
- [Service 1]: [purpose]

## Deployment Target
[Where and how this will be deployed]
```

### stage-N-instruct.md
Created by VL + Project Planner. Contains:

```markdown
# Stage N: [Stage Name]

## Context
[Brief: what the overall project is, link to project-plan.md]

## Stage Objective
[What this stage accomplishes]

## Dependencies
- Requires: [previous stages or external dependencies]
- Blocks: [stages waiting on this]

## Implementation Requirements
- [ ] Task 1: [specific implementation task]
- [ ] Task 2: [specific implementation task]
- [ ] ...

## Interfaces
### Consumes (from previous stages)
- [API/schema/service this stage uses]

### Exposes (for future stages)
- [API/schema/service this stage provides]

## Tests Required
- [ ] Test 1: [what to test]
- [ ] Test 2: [what to test]

## Completion Criteria
[How to know this stage is done]

## On Completion
Update `project-state.md` with:
- What was implemented
- How to run it
- What's exposed for next stages
- Test coverage summary
```

### project-state.md
Living document updated by Stage Managers. Reflects **current state only** (git history preserves past states).

```markdown
# Project State: [Project Name]

**Version**: [X.Y.Z]

*Last updated: [date] by [Stage N]*

## Completed Stages
- [x] Stage 1: [name] - [one-line summary]
- [x] Stage 2: [name] - [one-line summary]
- [ ] Stage 3: [name] - in progress

## Current System State

### Running Services
| Service | Port | How to Start |
|---------|------|--------------|
| [service] | [port] | `[command]` |

### Environment Variables Required
```
VAR_NAME=description
```

### Database State
- Tables: [list]
- Migrations: [status]

### API Endpoints Available
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/... | ... |

### Docker / Infrastructure
```bash
# How to run the current system
[commands]
```

## Test Coverage
- Stage 1: [X tests passing]
- Stage 2: [X tests passing]
- Integration: [status]

## Known Issues / Technical Debt
- [Issue 1]
- [Issue 2]

## Next Stage Ready
[What the next Stage Manager needs to know]
```

### deploy-instruct.md
Created by VL + Lead Architect. This is the prompt for the Project Deployer:

```markdown
# Deployment Instructions

## Target Environment
[Cloudflare / Render / AWS / etc.]

## Prerequisites
- [ ] All stages complete
- [ ] Integration tests passing
- [ ] Environment variables configured

## Deployment Steps
1. [Step 1]
2. [Step 2]

## MCP Servers Available
- [server 1]: [purpose]
- [server 2]: [purpose]

## Post-Deployment Verification
- [ ] Check 1
- [ ] Check 2
```

## Git Commit Ownership

| Who | What They Commit |
|-----|------------------|
| VL + PP | `project-plan.md`, `stage-N-instruct.md`, `deploy-instruct.md`, major revisions |
| Stage Managers | Implementation code, tests, `project-state.md` updates |
| Project Deployer | Deployment configs (if needed) |

## Stage Sequencing

### Sequential Stages
When Stage B depends on Stage A's output:
```
Stage A (database schema) → Stage B (API layer) → Stage C (frontend)
```
Stage Managers execute one at a time; each waits for the previous to complete.

### Parallel Stages
When stages are independent:
```
Stage A (user auth)     ─┐
Stage B (payment system) ├─→ Stage D (integration)
Stage C (notification)  ─┘
```
Multiple Stage Managers can work simultaneously.

### Sub-Stages
For complex stages (e.g., large frontend):
```
Stage 3: Frontend
├── Stage 3a: Component library
├── Stage 3b: Core pages
└── Stage 3c: Advanced features
```

## When to Invoke Each Role

| Trigger | Action |
|---------|--------|
| Have a rough idea | VL + Vision Assistant session (optional) |
| Vision clarified | VL + Lead Architect session |
| Project plan approved | VL + Project Planner session |
| Stage instruction ready | Stage Manager session |
| Stage complete | VL + PP review, merge to main |
| **New feature request mid-development** | **Feature Manager session → VL + LA review → PP integrates** |
| Pipeline connects (n+1 stages) | Consider Project Tester (VL decides) |
| Major roadblock | Re-invoke Lead Architect |
| Deployment strategy changes | Re-invoke Lead Architect |
| Version bump | Fresh Project Tester session (full system test) |
| Before major deployment | Security Auditor session (recommended) |
| Security concerns arise | Security Auditor session |
| Ready to deploy | Project Deployer session (using LA's deploy-instruct.md) |

## Versioning

### Ownership
**VL + Lead Architect** control the project version. Stage Managers and Project Planner do not bump versions.

### When to Bump
Version changes are **rare** — only for:
- Major architectural changes
- Deployment strategy changes
- Significant scope shifts that alter the system's foundation

Regular stage completions do **not** trigger version bumps.

### Version Location
- `project-plan.md` — top of file
- `project-state.md` — top of file
- Git tags for historical reference

### Effect of Version Bump
When VL + LA bump the version:
1. Update version in `project-plan.md` and `project-state.md`
2. Spawn a **fresh Project Tester session**
3. PT performs a **full system test** (no assumptions from previous testing)
4. This prevents accumulated blind spots and validates the system at its new state

### Versioning Scheme
Recommended: [Semantic Versioning](https://semver.org/)
- **Major (X.0.0)**: Breaking changes, major architectural shifts
- **Minor (0.X.0)**: New features, deployment changes
- **Patch (0.0.X)**: Bug fixes (rare at this level — usually handled in stages)

## Git Branching Strategy

### Branch Structure
```
main (protected)
  │
  ├── stage-1 (SM1 works here)
  ├── stage-2 (SM2 works here)
  ├── stage-3 (SM3 works here)
  │
  └── VL + PP merge into main after review
```

### Workflow
1. **SM creates branch** from main (e.g., `stage-1`)
2. **SM commits** all implementation work to their branch
3. **SM completes** → notifies VL + PP
4. **VL + PP review** → merge into main
5. **Dependent stages** pull from main after their dependencies merge

### Merge Order
PP determines merge sequence based on dependencies:
- Independent stages: merge in any order
- Dependent stages: upstream merges first

### Conflict Resolution
- VL + PP handle all merge conflicts
- SMs do not merge into main directly
- This keeps coordination at the coordination layer

## Secrets Management

### Default Approach
Use `.env` files with `.env.example` committed to repo:
- `.env` — actual secrets (git-ignored)
- `.env.example` — template with placeholder values (committed)

### Stage Manager Access
Stage instructions should reference environment variables, not actual values:
```
DATABASE_URL=your_connection_string
API_KEY=your_api_key
```

### When .env Won't Work
LA decides on alternatives during project planning:
- Cloud secret managers (AWS Secrets Manager, GCP Secret Manager)
- Platform-specific (Render environment, Cloudflare secrets)
- External tools (Doppler, 1Password)

Document the approach in `project-plan.md` under Constraints & Considerations.

## Shared Contracts

### Purpose
Contracts define interfaces between stages to prevent drift and miscommunication.

### Ownership
**Project Planner** creates and maintains contracts in `docs/contracts/`.

### When to Create Contracts
- When Stage B depends on Stage A's output
- For APIs, data schemas, message formats
- When parallel stages will eventually integrate

### Contract Format
```markdown
# Contract: [Name]

**Producer**: Stage [N]
**Consumer**: Stage [M]

## Interface

[API endpoint / schema / message format]

## Example

[Concrete example of valid input/output]

## Notes

[Edge cases, constraints, assumptions]
```

### Contract Location
```
docs/
├── contracts/
│   ├── user-api-contract.md
│   ├── payment-event-schema.md
│   └── ...
```

Stage Managers reference contracts in their implementation. PP validates contracts are honored during merge review.

## Handling Issues

### Stage Manager Hits a Blocker
1. SM documents the blocker in their stage's instruction doc or a comment
2. SM commits partial progress with clear notes
3. VL + PP review and decide:
   - Adjust the stage instructions, OR
   - Escalate to Lead Architect for redesign

### Tests Fail After Stage Completion
1. VL invokes Project Tester to diagnose
2. PT produces bug report with recommendations
3. VL + PP decide:
   - Create fix instructions for original SM, OR
   - Create a new fix stage

### Architectural Redesign Needed
1. VL re-invokes Lead Architect
2. LA + VL revise `project-plan.md`
3. VL + PP reassess stages, update instructions
4. Affected Stage Managers get updated instructions

### Mid-Development Feature Requests
When new feature ideas come up during development (e.g., stakeholder feedback):

1. VL invokes **Feature Manager** with the request
2. FM reviews project state and assesses impact
3. FM produces:
   - **Feature Assessment** (impact analysis, risk classification)
   - **Feature Plan** (if low/medium risk)
4. VL + LA review the assessment
5. Decision:
   - **Approve** → PP integrates into stages
   - **Defer** → Add to v2 backlog
   - **Escalate** → LA reviews for architectural impact

**Risk Levels:**
- **Low**: New self-contained stage, no changes to existing work
- **Medium**: Touches existing stages, minor contract changes
- **High**: Architectural changes, significant rework → escalate to LA

**Note**: Feature Manager handles insertions that don't require version bumps. If the feature fundamentally changes the architecture, it goes to Lead Architect instead.

## Scaling for Complex Projects

### Hierarchical Project Planners
For very large projects, PPs can be hierarchical:

```
VL + PP (Master)
    │
    ├── PP (Backend subsystem)
    │   ├── Stage: Database
    │   ├── Stage: API
    │   └── Stage: Workers
    │
    └── PP (Frontend subsystem)
        ├── Stage: Components
        ├── Stage: Pages
        └── Stage: State management
```

Each sub-PP reports to the master PP; VL maintains oversight of all.

## Example: Building a Web Scraping Pipeline

### 1. VL + Lead Architect
Output (`project-plan.md`):
- Tech: Python, FastAPI, PostgreSQL, Celery, Docker
- Features: Scrape sites, parse data, store in DB, API access
- Structure: `/scraper`, `/parser`, `/api`, `/db`

### 2. VL + Project Planner
Stage breakdown:
- **Stage 1**: Database infrastructure (schema, migrations)
- **Stage 2**: Scraper module (fetch pages, handle rate limits)
- **Stage 3**: Parser module (extract structured data)
- **Stage 4**: API layer (expose data via REST)
- **Stage 5**: Worker integration (Celery tasks connecting 2→3→1)

Parallel opportunities: Stages 2 and 3 can run in parallel (both independent), then Stage 5 integrates them.

### 3. Stage Managers Execute
- SM1 builds database → updates `project-state.md` → commits
- SM2 and SM3 work in parallel on scraper and parser
- VL + PP review after SM2 and SM3 complete
- VL invokes Project Tester to verify scraper→parser pipeline
- SM4 builds API
- SM5 integrates with Celery workers

### 4. Project Deployer
Deploys to Render with PostgreSQL add-on, Celery workers on separate dyno.

---

## Quick Start Checklist

1. [ ] Create `docs/` folder in your project
2. [ ] Start VL + Lead Architect session → produce `project-plan.md`
3. [ ] Start VL + Project Planner session → produce stage breakdown
4. [ ] Create `stage-1-instruct.md`
5. [ ] Start Stage Manager 1 session
6. [ ] SM1 completes → updates `project-state.md` → commits
7. [ ] VL + PP review → create next stage instructions
8. [ ] Repeat until all stages complete
9. [ ] Invoke Project Tester as needed
10. [ ] Invoke Project Deployer when ready

---

*This framework enables systematic AI-assisted development with clear human oversight, natural checkpoints, and a living record of project evolution.*
