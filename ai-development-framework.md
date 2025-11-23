# AI-Assisted Development Framework

## Overview

A hierarchical, git-driven framework for managing complex software development using AI coding assistants (Claude Code). The system automatically partitions complexity across multiple AI sessions, enabling parallel development through domain-based decomposition.

## Core Principles

- **Bounded Context**: Each AI session operates within a clearly defined scope via `instruct.md` files
- **Git-Triggered Execution**: Code changes to instruction files automatically trigger AI coding sessions
- **Hierarchical Decomposition**: Complexity naturally partitions along feature domain boundaries
- **Human-in-the-Loop Quality**: Human testing validates completion before integration

## Organizational Structure

```mermaid
graph TD
    LA[Lead Architect] --> PM[Project Manager]
    LA --> PD1[Project Designer - Domain 1]
    PM -.coordinates.-> PD1
    PM -.coordinates.-> PD2
    PM -.coordinates.-> PD3
    
    PD1 --> C1[Coder 1]
    PD1 --> C2[Coder 2]
    
    PD2[Project Designer - Domain 2] --> C3[Coder 3]
    
    PD3[Project Designer - Domain 3] --> C4[Coder 4]
    PD3 --> C5[Coder 5]
    PD3 --> C6[Coder 6]
    
    style LA fill:#ff6b6b
    style PM fill:#4ecdc4
    style PD1 fill:#45b7d1
    style PD2 fill:#45b7d1
    style PD3 fill:#45b7d1
    style C1 fill:#96ceb4
    style C2 fill:#96ceb4
    style C3 fill:#96ceb4
    style C4 fill:#96ceb4
    style C5 fill:#96ceb4
    style C6 fill:#96ceb4
```

## Role Definitions

### Lead Architect(s)
- **Responsibility**: Define overall project direction and architecture
- **Output**: Creates initial Project Designer(s) via `instruct.md` files
- **Scope**: Global project vision and high-level technical decisions

### Project Manager(s)
- **Responsibility**: Coordinate between Project Designer domains
- **Trigger**: Automatically required when n+1 Project Designers exist
- **Output**: Integration requirements, interface contracts, cross-domain coordination
- **Scope**: Inter-domain communication and dependency management

### Project Designer(s)
- **Responsibility**: Generate detailed implementation instructions for specific feature domains
- **Output**: Domain-specific `instruct.md` with precise coder instructions
- **Scope**: Single feature domain
- **Ratio**: 1 PD per feature domain

### Coder(s)
- **Responsibility**: Implement code according to their PD's instructions
- **Output**: Working code that satisfies `instruct.md` requirements
- **Scope**: Subset of tasks within a single domain
- **Ratio**: n coders per PD (flexible based on workload)

## Workflow

```mermaid
sequenceDiagram
    participant LA as Lead Architect
    participant Git as Git Repository
    participant PM as Project Manager
    participant PD as Project Designer
    participant CC as Claude Code (VSCode)
    participant Human as Human Tester
    
    LA->>Git: Create/Update instruct.md
    Git->>PM: Trigger on file change
    PM->>Git: Create coordination docs
    
    LA->>Git: Create PD instruct.md
    Git->>PD: Trigger on file change
    PD->>Git: Create detailed coder instruct.md
    
    Git->>CC: Trigger on instruct.md update
    CC->>CC: Execute coding tasks
    CC->>Git: Commit implementation
    
    Git->>Human: Notify for testing
    Human->>Human: Run pytest / manual testing
    
    alt Tests Pass
        Human->>Git: Approve & mark complete
        Git->>PD: Notify completion
        PD->>Git: Mark domain complete
    else Tests Fail
        Human->>Git: Update instruct.md with feedback
        Git->>CC: Re-trigger coding session
    end
```

## File Structure

```
project-root/
├── instruct.md                          # Lead Architect instructions
├── pm/
│   └── instruct.md                      # Project Manager coordination
├── domains/
│   ├── authentication/
│   │   ├── instruct.md                  # PD instructions for auth domain
│   │   ├── coders/
│   │   │   ├── coder-1-instruct.md     # Specific coder tasks
│   │   │   └── coder-2-instruct.md
│   │   └── src/                         # Implementation code
│   ├── payments/
│   │   ├── instruct.md
│   │   ├── coders/
│   │   │   └── coder-1-instruct.md
│   │   └── src/
│   └── analytics/
│       ├── instruct.md
│       └── src/
└── integration/
    └── tests/                           # Cross-domain integration tests
```

## Git-Driven Automation

```mermaid
flowchart LR
    A[instruct.md updated] --> B{Git detects change}
    B --> C[Trigger Claude Code session]
    C --> D[AI reads instruct.md]
    D --> E[AI executes tasks]
    E --> F[AI commits code]
    F --> G{Instruct.md complete?}
    G -->|Yes| H[Mark session complete]
    G -->|No| E
    H --> I[Human validation]
    I -->|Pass| J[Domain complete]
    I -->|Fail| K[Update instruct.md]
    K --> B
```

## Completion Criteria

Each role is considered "done" when:

1. **Lead Architect**: All necessary PDs have been spawned with clear instruct.md files
2. **Project Manager**: All inter-domain interfaces are defined and documented
3. **Project Designer**: Detailed coder instructions are complete and unambiguous
4. **Coder**: All tasks in instruct.md are implemented and committed

**Final validation**: Human tester confirms functionality via pytest or manual testing

## Scalability & Fractal Growth

The framework supports recursive depth:

```mermaid
graph TD
    LA[Lead Architect] --> PD1[PD: User Management]
    PD1 --> SubPD1[Sub-PD: Authentication]
    PD1 --> SubPD2[Sub-PD: Authorization]
    PD1 --> SubPD3[Sub-PD: User Profiles]
    
    SubPD1 --> C1[Coder: OAuth]
    SubPD1 --> C2[Coder: JWT]
    
    SubPD2 --> C3[Coder: RBAC]
    SubPD2 --> C4[Coder: Permissions]
    
    SubPD3 --> C5[Coder: Profile API]
```

When a domain becomes too complex, a PD can spawn sub-PDs, creating deeper hierarchies while maintaining bounded context for each AI session.

## Technology Stack

- **AI Engine**: Claude Code (via VSCode extension)
- **Version Control**: Git (triggers automation)
- **Testing**: pytest + human validation
- **Documentation**: Markdown (instruct.md files)
- **Orchestration**: Git hooks / CI/CD watching instruct.md changes

## Benefits

### Complexity Management
- Each AI session has a clear, bounded scope
- Natural decomposition along domain boundaries
- Self-documenting architecture via instruct.md files

### Parallelization
- Multiple PD-Coder groups work independently
- No coordination overhead within domains
- PM handles only inter-domain concerns

### Quality Control
- Human-in-the-loop testing ensures quality
- Git history provides full audit trail
- Clear completion criteria prevent scope creep

### Scalability
- Fractal structure grows with project complexity
- New domains easily added without restructuring
- Can handle projects of arbitrary size

## Example: E-commerce Project

```mermaid
graph TD
    LA[Lead Architect: E-commerce Platform] --> PM[PM: Integration Coordinator]
    
    LA --> PD1[PD: Product Catalog]
    LA --> PD2[PD: Shopping Cart]
    LA --> PD3[PD: Payment Processing]
    LA --> PD4[PD: Order Management]
    
    PM -.coordinates.-> PD1
    PM -.coordinates.-> PD2
    PM -.coordinates.-> PD3
    PM -.coordinates.-> PD4
    
    PD1 --> C1[Coder: Product API]
    PD1 --> C2[Coder: Search Engine]
    PD1 --> C3[Coder: Image Service]
    
    PD2 --> C4[Coder: Cart State]
    PD2 --> C5[Coder: Cart API]
    
    PD3 --> C6[Coder: Stripe Integration]
    PD3 --> C7[Coder: Payment Validation]
    
    PD4 --> C8[Coder: Order Processing]
    PD4 --> C9[Coder: Fulfillment API]
    
    style LA fill:#ff6b6b
    style PM fill:#4ecdc4
    style PD1 fill:#45b7d1
    style PD2 fill:#45b7d1
    style PD3 fill:#45b7d1
    style PD4 fill:#45b7d1
```

## Getting Started

1. Lead Architect creates root `instruct.md` defining project vision
2. Lead Architect creates domain folders with PD `instruct.md` files
3. If multiple domains exist, create PM with coordination `instruct.md`
4. PDs create detailed coder `instruct.md` files
5. Git hook triggers Claude Code on instruct.md changes
6. Coders implement and commit code
7. Human tests and validates
8. Rinse and repeat until project complete

---

*This framework enables systematic AI-assisted development at scale while maintaining human oversight and quality control.*
