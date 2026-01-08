# AI-Assisted Development Framework v2

A streamlined system for building complex software projects with AI coding assistants (Claude).

## The Idea

Instead of one AI session trying to do everything, you (the Vision Lead) collaborate with specialized AI sessions at each phase of development. Work is organized into stages with natural checkpoints for testing and review.

## Roles

| Role | Type | What They Do |
|------|------|--------------|
| **Vision Lead** | Human (you) | Hub of all decisions, works with every AI session |
| **Lead Architect** | AI | Co-designs project plan with you (tech stack, features, structure) |
| **Project Planner** | AI | Breaks project into stages, creates implementation instructions |
| **Stage Manager** | AI | Implements one stage, writes tests, updates project state |
| **Project Tester** | AI | Tests integrations and pipelines between stages |
| **Project Deployer** | AI | Deploys via MCP (Cloudflare, GitHub, Render, etc.) |

## Workflow

```
You + Lead Architect  →  project-plan.md
         ↓
You + Project Planner →  stage instructions
         ↓
Stage Managers        →  code + tests + project-state.md updates
         ↓
You review            →  invoke Tester if needed → next stages
         ↓
Project Deployer      →  live system
```

## Key Documents

| Document | Created By | Purpose |
|----------|------------|---------|
| `project-plan.md` | You + Lead Architect | Architecture, tech stack, features, structure |
| `deploy-instruct.md` | You + Lead Architect | Deployment strategy and prompt for Project Deployer |
| `stage-N-instruct.md` | You + Project Planner | Instructions for each Stage Manager |
| `project-state.md` | Stage Managers | Living doc of current system state (git tracks history) |

## File Structure

```
project-root/
├── docs/
│   ├── project-plan.md
│   ├── project-state.md
│   ├── deploy-instruct.md
│   └── stage-instructions/
│       ├── stage-1-instruct.md
│       ├── stage-2-instruct.md
│       └── ...
├── src/                    # Structure defined in project-plan.md
├── tests/
└── ...
```

## Getting Started

1. **Start a new Claude session**
2. **Paste the Lead Architect prompt** (`lead-architect-prompt.md`)
3. **Discuss your project idea** — produce `project-plan.md` + `deploy-instruct.md`
4. **Start a new session** with Project Planner prompt — produce stage instructions
5. **Start Stage Manager sessions** — implement each stage
6. **Invoke Project Tester** when pipelines connect or at checkpoints
7. **Invoke Project Deployer** when ready (using `deploy-instruct.md` from step 3)

## Files in This Repo

| File | Description |
|------|-------------|
| `README.md` | This file — quick overview |
| `ai-development-framework-v2.md` | Full framework documentation |
| `lead-architect-prompt.md` | Prompt to start a project (also creates deployment strategy) |
| `project-planner-prompt.md` | Prompt for breaking project into stages (creates Stage Manager prompts) |
| `project-tester-prompt.md` | Prompt for integration and pipeline testing |

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
