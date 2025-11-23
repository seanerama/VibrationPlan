# Project Designer Instructions Template

> **Template Version**: 1.0  
> **Domain**: `[DOMAIN_NAME]`  
> **Created**: `[DATE]`  
> **Lead Architect**: `[NAME/ID]`

---

## 1. Domain Overview

### Purpose
<!-- What is this domain responsible for in the overall system? -->
`[Describe the core responsibility and purpose of this domain]`

### Scope Boundaries
<!-- What is explicitly IN and OUT of scope for this domain? -->

**In Scope:**
- `[Feature/responsibility 1]`
- `[Feature/responsibility 2]`
- `[Feature/responsibility 3]`

**Out of Scope:**
- `[What this domain does NOT handle]`
- `[Dependencies managed by other domains]`

### Success Criteria
<!-- What does "done" look like for this domain? -->
- `[Measurable outcome 1]`
- `[Measurable outcome 2]`
- `[Measurable outcome 3]`

---

## 2. Technical Context

### Architecture Overview
<!-- High-level technical approach for this domain -->
```
[Describe the architectural pattern, e.g., microservice, module, layer, etc.]
```

### Technology Stack
- **Language**: `[e.g., Python 3.11, TypeScript, etc.]`
- **Framework**: `[e.g., FastAPI, React, Django, etc.]`
- **Database**: `[e.g., PostgreSQL, MongoDB, Redis, etc.]`
- **Key Libraries**: `[List important dependencies]`

### Design Patterns & Principles
<!-- Architectural patterns to follow -->
- `[e.g., Repository pattern, CQRS, Event-driven, etc.]`
- `[Coding standards to maintain]`
- `[Performance requirements]`

---

## 3. Domain Interfaces

### Dependencies (What this domain consumes)
<!-- Other domains/services this domain relies on -->

| Domain/Service | Interface | Purpose |
|----------------|-----------|---------|
| `[Domain name]` | `[API endpoint/method]` | `[Why needed]` |
| `[Domain name]` | `[API endpoint/method]` | `[Why needed]` |

### Exports (What this domain provides)
<!-- APIs/interfaces this domain exposes to others -->

| Interface | Consumer(s) | Description |
|-----------|-------------|-------------|
| `[API/method]` | `[Which domains use it]` | `[What it does]` |
| `[API/method]` | `[Which domains use it]` | `[What it does]` |

### Data Contracts
<!-- Expected input/output formats -->
```json
{
  "exampleInput": {
    "field1": "type",
    "field2": "type"
  },
  "exampleOutput": {
    "field1": "type", 
    "field2": "type"
  }
}
```

---

## 4. Functional Requirements

### Core Features
<!-- Prioritized list of features to implement -->

#### Feature 1: `[Feature Name]`
**Priority**: `[Critical/High/Medium/Low]`  
**Description**: `[What this feature does]`  
**Acceptance Criteria**:
- `[Specific, testable criterion 1]`
- `[Specific, testable criterion 2]`
- `[Specific, testable criterion 3]`

#### Feature 2: `[Feature Name]`
**Priority**: `[Critical/High/Medium/Low]`  
**Description**: `[What this feature does]`  
**Acceptance Criteria**:
- `[Specific, testable criterion 1]`
- `[Specific, testable criterion 2]`

#### Feature 3: `[Feature Name]`
**Priority**: `[Critical/High/Medium/Low]`  
**Description**: `[What this feature does]`  
**Acceptance Criteria**:
- `[Specific, testable criterion 1]`
- `[Specific, testable criterion 2]`

---

## 5. Non-Functional Requirements

### Performance
- **Response Time**: `[e.g., < 200ms for API calls]`
- **Throughput**: `[e.g., 1000 requests/second]`
- **Scalability**: `[e.g., horizontal scaling to 10 instances]`

### Security
- **Authentication**: `[e.g., JWT tokens, OAuth2]`
- **Authorization**: `[e.g., RBAC, specific permissions]`
- **Data Protection**: `[e.g., encryption at rest, PII handling]`

### Reliability
- **Availability**: `[e.g., 99.9% uptime]`
- **Error Handling**: `[Expected error handling approach]`
- **Logging**: `[What should be logged and at what level]`

### Testing Requirements
- **Unit Test Coverage**: `[e.g., > 80%]`
- **Integration Tests**: `[Required integration test scenarios]`
- **Test Data**: `[Any specific test data requirements]`

---

## 6. Code Organization

### Directory Structure
<!-- Expected file/folder organization -->
```
domains/[DOMAIN_NAME]/
├── instruct.md                 # This file
├── coders/
│   ├── coder-1-instruct.md    # PD will create these
│   └── coder-2-instruct.md
├── src/
│   ├── api/                   # API endpoints
│   ├── models/                # Data models
│   ├── services/              # Business logic
│   ├── repositories/          # Data access
│   └── utils/                 # Utilities
├── tests/
│   ├── unit/
│   └── integration/
└── README.md                  # Domain documentation
```

### Naming Conventions
- **Files**: `[e.g., snake_case for Python, camelCase for TypeScript]`
- **Classes**: `[e.g., PascalCase]`
- **Functions**: `[e.g., snake_case or camelCase]`
- **Constants**: `[e.g., UPPER_SNAKE_CASE]`

---

## 7. Storage Strategy

### Storage Ownership
**Ownership Model**: `[Dedicated/Shared/Hybrid]`

#### Option 1: Dedicated Storage (This domain owns its storage)
<!-- This domain has its own database/schema -->
- **Storage Type**: `[e.g., PostgreSQL database, MongoDB collection, Redis namespace]`
- **Access Pattern**: `[Exclusive - only this domain writes/reads]`
- **Migrations**: `[This domain manages its own migrations]`

#### Option 2: Shared Storage (Multiple domains share storage)
<!-- Storage is shared with other domains - PM COORDINATION REQUIRED -->
⚠️ **PM Coordination Required**: `[YES/NO]`

**Shared With Domains**:
- `[Domain 1]`: `[Shares: tables/collections/keys]`
- `[Domain 2]`: `[Shares: tables/collections/keys]`

**Coordination Requirements**:
- **Schema Changes**: Must coordinate with PM before modifying shared tables
- **Migration Sequence**: `[Which domain runs migrations first]`
- **Ownership Boundaries**: `[Which tables/fields each domain owns]`
- **Access Patterns**: `[Read-only vs. read-write for each domain]`

**Shared Storage Contract**:
```yaml
# Coordinated by PM - DO NOT MODIFY WITHOUT PM APPROVAL
shared_tables:
  - table_name: users
    owner_domain: user-management
    this_domain_access: read-only
    fields_used: [id, email, name]
  
  - table_name: shared_entity
    owner_domain: THIS_DOMAIN
    other_domains_access: read-only
    fields_owned: [field1, field2]
```

#### Option 3: Hybrid (Mix of dedicated and shared)
- **Dedicated Tables**: `[Tables only this domain owns]`
- **Shared Tables**: `[Tables shared with other domains - see PM coordination above]`

---

## 8. Data Models

### Primary Entities
<!-- Key data structures for this domain -->

#### Entity: `[EntityName]`
**Storage Location**: `[Dedicated table / Shared table - owner: DomainX / Shared table - owner: THIS_DOMAIN]`

```python
# Example schema
{
  "id": "uuid",
  "name": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Relationships**:
- `[Related entity and relationship type]`

**Validations**:
- `[Field validation rules]`

**Access Pattern**:
- `[Read/Write/Read-Only]`
- `[If shared: must coordinate changes with PM]`

---

## 8. Integration Points

### External APIs
<!-- Third-party services this domain integrates with -->
- **Service**: `[e.g., Stripe API]`
  - **Purpose**: `[Why integrated]`
  - **Endpoints Used**: `[List key endpoints]`
  - **Auth Method**: `[API key, OAuth, etc.]`

### Message Queues / Events
<!-- If using event-driven architecture -->
- **Publishes**: `[Events this domain emits]`
- **Subscribes**: `[Events this domain listens to]`
- **Queue/Topic**: `[Queue names/topics]`

---

## 9. Configuration & Environment

### Environment Variables
```bash
# Required environment variables
DOMAIN_API_KEY=[description]
DATABASE_URL=[description]
CACHE_URL=[description]
LOG_LEVEL=[description]
```

### Feature Flags
<!-- Any feature toggles needed -->
- `[FEATURE_FLAG_NAME]`: `[Purpose and default value]`

---

## 10. Migration & Deployment

### Database Migrations
<!-- If database changes are needed -->
- `[Migration description and approach]`
- `[Rollback strategy]`

### Deployment Strategy
- **Strategy**: `[e.g., blue-green, rolling update, canary]`
- **Dependencies**: `[What must be deployed first]`
- **Rollback Plan**: `[How to rollback if needed]`

---

## 11. Monitoring & Observability

### Metrics to Track
- `[Metric 1: e.g., request latency p95]`
- `[Metric 2: e.g., error rate]`
- `[Metric 3: e.g., cache hit ratio]`

### Alerts
- `[Alert condition 1]`
- `[Alert condition 2]`

### Logs
<!-- What events should be logged -->
- **Info**: `[Normal operation events]`
- **Warning**: `[Concerning but non-critical events]`
- **Error**: `[Failures requiring attention]`

---

## 12. Documentation Requirements

### API Documentation
- `[e.g., OpenAPI/Swagger spec required]`
- `[Example requests/responses needed]`

### Code Comments
- `[When to comment: complex algorithms, business logic, etc.]`
- `[Docstring format: e.g., Google style, NumPy style]`

### README Updates
<!-- What should be documented in the domain README -->
- Setup instructions
- Running tests
- Common troubleshooting

---

## 13. PM Coordination Requirements

### When PM Coordination is Required
<!-- Explicit flags for when you MUST coordinate with PM -->

**PM Exists**: `[YES/NO]`

If YES, you MUST coordinate with PM before:

#### Shared Storage Changes
- [ ] Modifying any shared database tables/collections
- [ ] Adding/removing fields to shared entities
- [ ] Changing shared table schemas
- [ ] Running migrations that affect shared storage
- [ ] Changing access patterns to shared data

#### Cross-Domain Interfaces
- [ ] Changing any API contracts that other domains depend on
- [ ] Modifying data formats that other domains consume
- [ ] Adding new endpoints that other domains will use
- [ ] Deprecating any interfaces other domains rely on

#### Infrastructure Changes
- [ ] Adding new shared services (caches, queues, etc.)
- [ ] Modifying shared message queue topics/schemas
- [ ] Changing shared authentication/authorization mechanisms

#### Performance/Scaling Impacts
- [ ] Changes that could impact other domains' performance
- [ ] Introducing new rate limits or quotas
- [ ] Significant changes to request/response patterns

### PM Contact Protocol
**PM Instruct File**: `[path/to/pm/instruct.md]`

**Coordination Process**:
1. Document your proposed change in `pm-coordination-request.md`
2. Flag the PM by updating their coordination queue
3. Wait for PM approval/feedback
4. Proceed only after coordination is complete

### PM-Approved Contracts
<!-- Once PM approves interfaces, document here -->

**Status**: `[Pending/Approved/In Revision]`

**Approved Interfaces**: `[Link to PM-approved interface contracts]`

**Approved Storage Boundaries**: `[Link to PM-approved storage access patterns]`

---

## 14. Project Designer Tasks

### Your Responsibilities
As the Project Designer for this domain, you must:

1. **Understand** this entire specification thoroughly
2. **Decompose** the work into discrete, manageable coding tasks
3. **Create** detailed `coder-instruct.md` files for each task
4. **Define** clear completion criteria for each coder task
5. **Ensure** all inter-domain interfaces are properly defined
6. **Coordinate** with Project Manager on cross-domain concerns (if PM exists)

### Coder Instruction Guidelines
When creating instructions for coders, ensure each `coder-instruct.md` includes:
- Specific files to create/modify
- Clear acceptance criteria
- Test cases to implement
- Code examples where helpful
- Links to relevant documentation

### Questions/Clarifications
<!-- If you need clarification from the Lead Architect -->
If anything in this specification is unclear or ambiguous:
1. Document your questions in a `questions.md` file
2. Propose a reasonable interpretation
3. Proceed with implementation based on your best judgment
4. Flag for review during testing phase

---

## 14. Timeline & Milestones

### Estimated Complexity
**Domain Complexity**: `[Simple/Medium/Complex/Very Complex]`

### Suggested Phases
1. **Phase 1**: `[Core functionality]` - `[Estimated completion]`
2. **Phase 2**: `[Extended features]` - `[Estimated completion]`
3. **Phase 3**: `[Optimization/Polish]` - `[Estimated completion]`

### Critical Path Items
<!-- Tasks that block other work -->
- `[Critical task 1]`
- `[Critical task 2]`

---

## 15. Reference Materials

### Related Documentation
- `[Link to overall architecture docs]`
- `[Link to API standards]`
- `[Link to security guidelines]`

### Example Implementations
<!-- If there are reference implementations -->
- `[Link to similar domain implementation]`
- `[Link to code examples]`

### External Resources
- `[Relevant tutorials, documentation, etc.]`

---

## Status Tracking

**Current Status**: `[Not Started / In Progress / Coder Instructions Complete / Implementation In Progress / Testing / Complete]`

**Last Updated**: `[DATE]`

**Blockers**: `[Any blockers preventing progress]`

**Notes**: `[Any important notes or decisions made]`

---

## Appendix: Glossary

<!-- Domain-specific terminology -->
- **`[Term 1]`**: `[Definition]`
- **`[Term 2]`**: `[Definition]`
- **`[Term 3]`**: `[Definition]`