# AI-Assisted Development Framework v2

A streamlined system for building complex software projects with AI coding assistants (Claude).

## The Idea

Instead of one AI session trying to do everything, you (the Vision Lead) collaborate with specialized AI sessions at each phase of development. Work is organized into stages with natural checkpoints for testing and review.

## Roles

| Role | Type | What They Do |
|------|------|--------------|
| **Vision Lead** | Human (you) | Hub of all decisions, works with every AI session |
| **Vision Assistant** | AI | Helps VL explore and clarify ideas before architecture |
| **Lead Architect** | AI | Co-designs project plan with you (tech stack, features, structure, standards) |
| **Project Planner** | AI | Breaks project into stages, creates contracts and SM instructions, manages merges |
| **Stage Manager** | AI | Implements one stage, writes tests, updates project state |
| **Project Tester** | AI | Tests integrations and pipelines between stages |
| **Security Auditor** | AI | Reviews system for vulnerabilities and security risks |
| **Project Deployer** | AI | Deploys via MCP (Cloudflare, GitHub, Render, etc.) |

## Workflow

```
You + Vision Assistant →  vision-document.md (optional but recommended)
         ↓
You + Lead Architect  →  project-plan.md (v1.0.0) + deploy-instruct.md
         ↓
You + Project Planner →  stage instructions + contracts
         ↓
Stage Managers        →  implement on branches → tests pass
         ↓
You + PP merge        →  merge to main → invoke Tester if needed
         ↓
[Major change?]       →  You + LA bump version → fresh Tester (full system)
         ↓
Security Auditor      →  review before deployment (recommended)
         ↓
Project Deployer      →  live system
```

## Key Documents

| Document | Created By | Purpose |
|----------|------------|---------|
| `vision-document.md` | You + Vision Assistant | Clarified idea before architecture (optional) |
| `project-plan.md` | You + Lead Architect | Architecture, tech stack, features, standards |
| `deploy-instruct.md` | You + Lead Architect | Deployment strategy and prompt for Project Deployer |
| `stage-N-instruct.md` | You + Project Planner | Instructions for each Stage Manager |
| `contracts/*.md` | Project Planner | Interface definitions between stages |
| `project-state.md` | Stage Managers | Living doc of current system state (git tracks history) |

## File Structure

```
project-root/
├── docs/
│   ├── project-plan.md
│   ├── project-state.md
│   ├── deploy-instruct.md
│   ├── stage-instructions/
│   │   └── stage-N-instruct.md
│   └── contracts/
│       └── [interface contracts]
├── src/                    # Structure defined in project-plan.md
├── tests/
├── .env.example            # Environment template (committed)
├── .env                    # Actual secrets (git-ignored)
└── ...
```

## Versioning

**VL + Lead Architect** control the project version (in `project-plan.md` and `project-state.md`).

Version bumps are **rare** — only for major architectural or deployment changes.

**Effect of version bump**: Spawns a fresh Project Tester session that does a full system test with no assumptions from prior testing.

## Getting Started

1. **Have a rough idea?** Paste `vision-assistant-prompt.md` → produce `vision-document.md`
2. **Ready for architecture?** Paste `lead-architect-prompt.md` → produce `project-plan.md` + `deploy-instruct.md`
3. **Break it down:** Paste `project-planner-prompt.md` → produce stage instructions + contracts
4. **Build stages:** Start Stage Manager sessions → implement on branches
5. **Merge & test:** VL + PP merge to main → invoke Tester when pipelines connect
6. **Security check:** Invoke Security Auditor before major deployments
7. **Deploy:** Invoke Project Deployer with `deploy-instruct.md`

## Files in This Repo

| File | Description |
|------|-------------|
| `README.md` | This file — quick overview |
| `ai-development-framework-v2.md` | Full framework documentation |
| `vision-assistant-prompt.md` | Prompt to explore and clarify an idea (before LA) |
| `lead-architect-prompt.md` | Prompt to design architecture and deployment |
| `project-planner-prompt.md` | Prompt for breaking project into stages + contracts |
| `project-tester-prompt.md` | Prompt for integration and pipeline testing |
| `security-auditor-prompt.md` | Prompt for security vulnerability review |

*Note: Stage Manager prompts are created by the Project Planner for each specific stage. The Project Deployer prompt is created by the Lead Architect as `deploy-instruct.md`.*

## When to Use This

**Good for:**
- Multi-component projects (backend + frontend + integrations)
- Projects with clear implementation phases
- When you want structured checkpoints and testing
- When you need a living record of what's been built

**Overkill for:**
- Simple scripts or single-file tools
- Rapid prototyping / MVPs
- Projects you can build in one session

---

*See `ai-development-framework-v2.md` for complete documentation.*
