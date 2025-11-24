# AI-Assisted Development Framework - Quick Start Guide

A practical guide to using the AI-Assisted Development Framework for building complex software projects with Claude Code.

## What Is This?

This framework lets you scale AI-driven development by breaking projects into bounded contexts. Instead of one overwhelmed AI session, you orchestrate multiple focused AI sessions working in parallel, coordinated through git and markdown files.

## Core Concept

**The Big Idea**: Each AI session reads an `instruct.md` file, completes the tasks, commits code, then waits for human validation. Git changes to `instruct.md` files trigger new AI sessions.

**Four Roles**:
1. **Lead Architect** - You, defining the project vision
2. **Project Manager** - AI coordinating between domains (auto-spawned when needed)
3. **Project Designers** - AI planning domain implementations
4. **Coders** - AI implementing specific tasks

## When to Use This Framework

**Use it when:**
- Your project has 3+ distinct feature domains (auth, payments, analytics, etc.)
- You need multiple AI sessions working in parallel
- You want clear separation of concerns
- You need audit trails and structured coordination

**Don't use it when:**
- Building a simple single-domain app
- Rapid prototyping (overkill for MVP)
- You prefer monolithic development

## Quick Start: 30-Minute Setup

### Step 1: Set Up Your Project Structure

```bash
mkdir my-project
cd my-project

# Create the framework structure
mkdir -p pm/{contracts,coordination-queue,escalations,decisions,to-domains}
mkdir -p domains
mkdir -p integration/tests
```

### Step 2: Write Your Lead Architect Instructions

Create `instruct.md` at the root:

```markdown
# Lead Architect Instructions

## Project Vision
[Your 2-3 sentence project description]

## Domains
This project has the following domains:
- **Domain 1**: [Brief description]
- **Domain 2**: [Brief description]

## Next Steps
1. Create Project Manager using pm/instruct.md template
2. Create Project Designer for Domain 1 in domains/domain-1/
3. Create Project Designer for Domain 2 in domains/domain-2/
```

### Step 3: Create Project Manager (If You Have 2+ Domains)

Copy `project-manager-instruct-template.md` to `pm/instruct.md` and fill in the checklist (Section 0).

**Key things to define**:
- What domains exist and how they interact
- Shared resources (database, cache, message queue)
- Interface contracts between domains

### Step 4: Create Project Designers for Each Domain

For each domain, create `domains/[domain-name]/instruct.md`:

```markdown
# Project Designer: [Domain Name]

## Domain Scope
[What this domain owns and doesn't own]

## Technical Requirements
[Tech stack, architecture patterns]

## Tasks to Implement
- [ ] Task 1: [Description]
- [ ] Task 2: [Description]

## Dependencies
- Depends on: [Other domains this needs]
- Consumed by: [Domains that need this]

## Completion Criteria
[How to know when this domain is done]
```

### Step 5: Set Up Git Automation (Optional but Recommended)

Create `.github/workflows/ai-trigger.yml`:

```yaml
name: AI Coordination

on:
  push:
    paths:
      - '**/instruct.md'
      - 'pm/coordination-queue/*.md'

jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - name: Notify AI Session
        run: echo "Trigger Claude Code session for changed instruct.md"
```

### Step 6: Run Your First AI Session

1. Open VSCode with Claude Code extension
2. Open `domains/[domain-1]/instruct.md`
3. Let Claude Code read and execute the instructions
4. Review the generated code
5. Test manually or with pytest
6. If tests pass → mark domain complete
7. If tests fail → update `instruct.md` with fixes needed

## Workflow Example: E-commerce Project

Let's say you're building an e-commerce platform.

### 1. Lead Architect Defines Domains

```markdown
# E-commerce Platform

## Domains
- **Product Catalog**: Product CRUD, search, images
- **Shopping Cart**: Cart state, cart API
- **Payments**: Stripe integration, transaction processing
- **Order Management**: Order processing, fulfillment
```

### 2. Project Manager Defines Contracts

In `pm/instruct.md`, PM specifies:

```markdown
## Shared Database Tables
- `users` (owned by Product Catalog, read by all)
- `transactions` (owned by Payments, read by Order Management)

## API Contracts
- Product Catalog provides GET /api/products/{id}
- Payments publishes payment.completed events
```

### 3. Project Designers Create Coder Tasks

`domains/product-catalog/instruct.md`:

```markdown
## Tasks
- [ ] Create Product model and database schema
- [ ] Implement GET /api/products endpoint
- [ ] Add search functionality
- [ ] Write integration tests
```

### 4. Coders Implement

If Product Catalog is complex, split it:

```
domains/product-catalog/
├── instruct.md (PD instructions)
├── coders/
│   ├── coder-1-instruct.md (Product API implementation)
│   └── coder-2-instruct.md (Search engine implementation)
└── src/ (generated code)
```

## Coordination: How Domains Talk to Each Other

### Scenario: Payments needs user data from Product Catalog

**Step 1**: Payments PD creates `domains/payments/pm-requests/dep-change-001.md`:

```markdown
## Dependency Change Notification
**Domain**: Payments
**Change Type**: New
**Target Domain**: Product Catalog
**Dependency Nature**: API call
**Direction**: We consume from Product Catalog

### Rationale
Need to verify user identity before processing payment
```

**Step 2**: PM receives notification, updates dependency graph

**Step 3**: PM defines contract in `pm/contracts/user-lookup-api.json`

**Step 4**: Both domains build to the contract

**Step 5**: Integration test validates the contract works

## When Things Go Wrong

### Scenario: Two domains want conflicting database changes

**Step 1**: PM detects conflict

**Step 2**: PM creates `pm/escalations/priority-conflict-001.md`:

```markdown
## Priority Conflict
**Request A**: Payments wants to add `payment_status` column to `users` table
**Request B**: Product Catalog wants to normalize `users` table (breaks payments)

**Impact Analysis**:
- If A proceeds first: B must accommodate the column
- If B proceeds first: A must adapt to new schema
```

**Step 3**: Lead Architect (you) decides which takes priority

**Step 4**: PM coordinates the chosen solution

## Human Validation Points

**You should test and approve**:
1. After each coder completes implementation
2. When a domain marks itself complete
3. After integration tests run
4. Before deploying to production

**How to provide feedback**:
- Update the relevant `instruct.md` file with what failed
- Git commit triggers a new AI session with updated instructions

## Tips for Success

### 1. Start Small
Don't create all domains at once. Start with 1-2 domains, get them working, then add more.

### 2. Clear Boundaries
Each domain should have a clear "owns" and "does not own" list. Ambiguity causes conflicts.

### 3. Contract-First
Define interface contracts before implementation. Both sides build to the contract.

### 4. Integration Tests Are Critical
They're your proof that domains actually work together.

### 5. Use the Templates
- `project-manager-instruct-template.md` has everything PMs need
- Fill in the checklist before activating

## File Organization Reference

```
project-root/
├── instruct.md                          # Your vision (Lead Architect)
├── pm/
│   ├── instruct.md                      # PM coordination rules
│   ├── contracts/                       # Shared contracts
│   ├── coordination-queue/              # Incoming requests
│   ├── escalations/                     # Issues for you to decide
│   └── decisions/                       # Past decisions (audit trail)
├── domains/
│   └── [domain-name]/
│       ├── instruct.md                  # PD instructions
│       ├── pm-requests/                 # Requests to PM
│       ├── coders/
│       │   └── coder-N-instruct.md     # Individual coder tasks
│       └── src/                         # Generated code
└── integration/
    └── tests/                           # Cross-domain tests
```

## Common Questions

**Q: Do I need a Project Manager for 2 domains?**
A: Technically it activates at 2+ domains, but for simple projects with minimal interaction, you can skip it initially.

**Q: Can domains share code?**
A: Shared utilities should live in a common library. Don't duplicate code across domains.

**Q: What if a domain becomes too complex?**
A: Split it. Create sub-Project Designers under that domain (fractal structure).

**Q: How do I handle secrets?**
A: Never commit secrets to `instruct.md`. Reference environment variables or secret management systems.

**Q: Can I use this without Claude Code?**
A: The framework is designed for Claude Code, but the patterns work with any AI coding assistant that can read instructions and commit code.

## Next Steps

1. Read [ai-development-framework.md](ai-development-framework.md) for architectural details
2. Review [project-manager-instruct-template.md](project-manager-instruct-template.md) for PM setup
3. Create your first `instruct.md` and start building

---

**Questions or Feedback?**
This is a living framework. Adapt it to your needs. The core principle—bounded contexts with git-driven coordination—remains constant.
