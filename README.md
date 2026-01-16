# VibrationPlan

An AI-assisted development framework for building software with Claude.

## Quick Start: New Project

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

### 2. Set Up .gitignore

Create a `.gitignore` at the root with:

```
# AI framework (stays local, not committed)
vibration-plan/

# Secrets
.env
```

### 3. Start Building

1. Open Claude
2. Paste the **Lead Architect** prompt from `vibration-plan/prompts/lead-architect-prompt.md`
3. Work with LA to create your `project-plan.md`
4. Continue through the workflow...

---

## Quick Start: Existing Project

Use this when you want to apply VibrationPlan to a project that already exists.

### 1. Clone VibrationPlan into Your Project

```bash
cd your-existing-project

# Clone just the vibration-plan folder
git clone https://github.com/seanerama/VibrationPlan.git temp-vp
mv temp-vp/vibration-plan ./vibration-plan
rm -rf temp-vp
```

### 2. Add to .gitignore

Add to your existing `.gitignore`:

```
# AI framework (stays local, not committed)
vibration-plan/
```

### 3. Start with Retrofit Planner

1. Open Claude
2. Paste the **Retrofit Planner** prompt from `vibration-plan/prompts/retrofit-planner-prompt.md`
3. Work with RP to analyze your codebase and document the current state
4. Define what changes you want to make
5. Then use **Project Planner** to break changes into stages

## Folder Structure

```
my-new-project/
├── vibration-plan/                  # GIT-IGNORED (all AI stuff stays here)
│   ├── prompts/                     # Framework prompts
│   │   ├── lead-architect-prompt.md
│   │   ├── retrofit-planner-prompt.md  # For existing projects
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

### New Projects
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

### Existing Projects
```
You (Vision Lead)
     │
     ├── Retrofit Planner ──→ Analyze codebase, document state, define changes
     │                        (replaces Vision Assistant + Lead Architect)
     │
     ├── Project Planner ───→ Stage instructions for changes
     │
     └── (same as above from here)
```

## Roles

| Role | What They Do |
|------|--------------|
| **Vision Lead** | You — hub of all decisions |
| **Vision Assistant** | Helps clarify ideas before architecture |
| **Lead Architect** | Co-designs project plan (tech stack, features, structure) |
| **Retrofit Planner** | Analyzes existing codebase, documents state, plans changes (replaces VA + LA) |
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
