# Solution Design Document Template

Sections marked **(core)** always appear. Sections marked **(optional)** appear only when the notes contain material for them. Remove these markers and the guidance in _italics_ from the final doc.

---

```markdown
# Solution Design: <Solution name>

| | |
|---|---|
| **Client / Team** | <from notes or TBD> |
| **Workshop date(s)** | <from notes or TBD> |
| **Participants** | <names/roles from notes> |
| **Document status** | Draft — generated from workshop notes |
| **Version** | 0.1 |

## 1. Executive Summary (core)
_3–5 sentences: the problem, the proposed solution, the expected outcome, and the biggest open item._

## 2. Background & Problem Statement (core)
_Why this work exists. Current pain points, business drivers, triggering events. Quote figures from the notes._

## 3. Goals & Success Metrics (core)
_Bulleted goals. Metrics in a table if any were given (metric, baseline, target). Missing targets → TBD + open question._

## 4. Scope (core)
### In scope
### Out of scope
_Only list items explicitly excluded or deferred in the notes._

## 5. Stakeholders & Users (core)
| Name / Role | Interest or responsibility |
|---|---|

## 6. Current State (optional)
_How things work today: systems, process, manual steps._

## 7. Requirements (core)
### Functional requirements
| ID | Requirement | Priority | Source |
|---|---|---|---|
| FR-1 | ... | Must / Should / Could / TBD | _who or where in the notes_ |

### Non-functional requirements
_Performance, availability, security, compliance, scalability, accessibility — only those discussed; otherwise note as open questions._

## 8. Proposed Solution (core)
### Overview
_One paragraph describing the approach._
### Architecture
_Mermaid diagram when components/flows are described, then a component table:_
| Component | Responsibility | Technology (if decided) |
|---|---|---|
### Key flows
_Numbered steps for the main user/data flows._

## 9. Data & Integrations (optional)
_Data sources, ownership, volumes, sensitivity; external systems and integration method._

## 10. AI / Model Design (optional — AI or agent solutions only)
_Use cases for the model/agent, model choice, prompting/RAG/tools, evaluation approach, guardrails, human-in-the-loop._

## 11. Process Changes (optional — business-process solutions)
_Current vs target process, roles affected, change management / training._

## 12. Decisions & Alternatives Considered (core)
| Decision | Rationale | Alternatives discussed | Decided by |
|---|---|---|---|
_Only record something as a decision if the notes show it was agreed. Ideas still being weighed go under Alternatives or Open Questions._

## 13. Risks, Assumptions & Dependencies (core)
| Type | Description | Impact | Mitigation |
|---|---|---|---|
| Risk / Assumption / Dependency | ... | H / M / L / TBD | ... |

## 14. Implementation Plan & Timeline (optional)
_Phases, milestones, dates — only as discussed._

## 15. Action Items (optional)
| Action | Owner | Due |
|---|---|---|

## 16. Open Questions (core)
| # | Question | Why it matters | Suggested owner |
|---|---|---|---|
```
