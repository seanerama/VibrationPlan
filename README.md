# VibrationPlan

An AI-assisted development framework for building software with Claude.

## Quick Start

### 1. Fork or Clone This Repo

```bash
# Option A: Fork on GitHub, then clone your fork
git clone https://github.com/YOUR-USERNAME/VibrationPlan.git my-new-project

# Option B: Clone directly and remove git history
git clone https://github.com/seanerama/VibrationPlan.git my-new-project
cd my-new-project
rm -rf .git
git init
```

### 2. Rename Your Project

```bash
mv VibrationPlan my-new-project  # if you didn't specify name in clone
cd my-new-project
```

### 3. Set Up .gitignore

Create a `.gitignore` at the root with:

```
# AI framework (stays local, not committed)
vibration-plan/

# Secrets
.env
```

### 4. Start Building

1. Open Claude
2. Paste the **Lead Architect** prompt from `vibration-plan/prompts/lead-architect-prompt.md`
3. Work with LA to create your `project-plan.md`
4. Continue through the workflow...

## Folder Structure

```
my-new-project/
├── vibration-plan/                  # GIT-IGNORED (all AI stuff stays here)
│   ├── prompts/                     # Framework prompts
│   │   ├── lead-architect-prompt.md
│   │   ├── project-planner-prompt.md
│   │   ├── project-tester-prompt.md
│   │   ├── handoff-tester-prompt.md
│   │   ├── feature-manager-prompt.md
│   │   ├── security-auditor-prompt.md
│   │   └── vision-assistant-prompt.md
│   ├── framework-docs/              # Framework reference
│   │   ├── README.md                # Detailed framework overview
│   │   └── ai-development-framework-v2.md
│   ├── project-plan.md              # Created by Lead Architect
│   ├── project-state.md             # Living doc, updated by SMs
│   ├── deploy-instruct.md           # Created by Lead Architect
│   ├── stage-instructions/          # Created by Project Planner
│   │   └── stage-N-instruct.md
│   ├── contracts/                   # Created by Project Planner
│   ├── tests/                       # Project Tester documentation
│   └── ux-feedback/                 # Handoff Tester documentation
├── src/                             # Your project code (structure from project-plan.md)
├── tests/                           # Your test files
├── .gitignore                       # Must include: vibration-plan/, .env
├── .env.example                     # Environment template (committed)
├── .env                             # Actual secrets (git-ignored)
└── README.md                        # Your project's README (replace this file)
```

## The Workflow

```
You (Vision Lead)
     │
     ├── Vision Assistant ──→ Clarify your idea (optional)
     │
     ├── Lead Architect ────→ project-plan.md + deploy-instruct.md
     │
     ├── Project Planner ───→ Stage instructions + contracts
     │
     ├── Stage Managers ────→ Implementation (one per stage)
     │         │
     │         └── Commit to branch → merge to main
     │
     ├── Project Tester ────→ Test pipelines, fix bugs
     │
     ├── Handoff Tester ────→ UX feedback with end users
     │
     ├── Security Auditor ──→ Security review (before deployment)
     │
     └── Project Deployer ──→ Deploy via MCP
```

## Roles

| Role | What They Do |
|------|--------------|
| **Vision Lead** | You — hub of all decisions |
| **Vision Assistant** | Helps clarify ideas before architecture |
| **Lead Architect** | Co-designs project plan (tech stack, features, structure) |
| **Project Planner** | Breaks project into stages, creates contracts |
| **Stage Manager** | Implements one stage, writes tests |
| **Feature Manager** | Assesses mid-development feature requests |
| **Project Tester** | Tests pipelines, finds and fixes bugs |
| **Handoff Tester** | Documents UX feedback with end users |
| **Security Auditor** | Reviews for vulnerabilities |
| **Project Deployer** | Deploys via MCP |

## Key Principles

- **vibration-plan/ is git-ignored** — Framework stays invisible in your final repo
- **Stage 1 initializes git** — Creates .gitignore with vibration-plan/ and .env
- **Each role is a fresh Claude session** — Prevents context overload
- **project-state.md is the living doc** — Always current, git tracks history

## Documentation

- [Full Framework Documentation](vibration-plan/framework-docs/ai-development-framework-v2.md)
- [Framework Overview](vibration-plan/framework-docs/README.md)

## After You Start Your Project

Replace this README.md with your project's own README. The framework docs stay in `vibration-plan/framework-docs/` for reference.
