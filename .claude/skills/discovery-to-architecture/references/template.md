# Solution Design Template

Follow this structure. Guidance in _italics_ is for you — remove it from the final document. Keep every numbered section; if the notes give nothing for a section, say so in one line and point to the relevant open questions rather than padding it.

Label content consistently throughout:
- **Decided** — agreed by the client in the notes
- **Recommended** — your proposal, with rationale
- **Open** — unresolved; links to a Q#

Tag individual facts **[stated]** or **[assumed]** where the distinction isn't obvious from context (you don't need to tag every line of a table built entirely from the notes).

---

```markdown
# <Client or project> — AI Solution Design

| | |
|---|---|
| **Client** | <from notes, or TBD> |
| **Discovery session(s)** | <date(s) from notes, or TBD> |
| **Participants** | <names and roles from notes> |
| **Status** | Draft v0.1 — generated from discovery notes, for client review |

## 1. Executive summary
_4–6 sentences: the problem, the recommended solution and lead use case, the expected outcome, the proposed first phase, and the biggest open issue._

## 2. Context
_Why this work exists: business drivers, pain points, triggering events. Quote figures from the notes. Include desired outcomes and any constraints (budget, timeline, technology, regulation)._

### Stakeholders
| Name / role | Interest or responsibility |
|---|---|

## 3. Current state
_How things work today: systems, data sources, process, manual steps, known limitations. A short table of systems is often clearest:_

| System | Purpose | Integration options | Notes |
|---|---|---|---|

## 4. Use cases
| # | Use case | Pattern | Success metric | Data needed | Value | Feasibility | Data readiness | Risk |
|---|---|---|---|---|---|---|---|---|
| UC1 | ... | RAG / extraction / agent / ... | ... or TBD | ... | H/M/L | H/M/L | H/M/L | H/M/L |

_Below the table: one line of reasoning per score where it isn't obvious, then the recommended lead use case(s) and why._

## 5. Architecture

### Overview
_One paragraph describing the approach._

### Diagram
_Mermaid flowchart or sequence diagram. Label proposed components as such._

### Components
| Area | Design | Status |
|---|---|---|
| Model | ... | Decided / Recommended / Open |
| Orchestration | ... | |
| Retrieval and data | ... | |
| Integrations | ... | |
| Security and access | ... | |

### Key flows
_Numbered steps for the main user and data flows, including hand-off to humans._

### Cost and latency
_Main cost drivers (volumes, tokens, hosting) and latency expectations from the notes. No invented numbers — open questions where targets are missing._

## 6. Evals and guardrails

### Evaluation approach
_How quality will be measured before and after launch: test sets, metrics tied to the use-case success metrics, human review, online monitoring._

### Guardrails
_Hard constraints from the notes (e.g. "must not issue refunds") first, then recommended controls: scope limits, grounding and citation, PII handling, escalation to humans, prompt-injection defences, logging._

## 7. Risks
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| ... | H/M/L | H/M/L | ... |

### Regulatory mapping (FSI clients only)
| Regulation | Applies? | Why | Design implications |
|---|---|---|---|

_Recommend the mapping is confirmed with the client's compliance and legal teams._

## 8. Roadmap
| Phase | Scope | Key activities | Exit criteria | Timing |
|---|---|---|---|---|
| Proof of Value | ... | ... | measurable gate | from notes, or TBD |
| Pilot | ... | ... | ... | ... |
| Production | ... | ... | ... | ... |

## 9. Assumptions and open questions

### Assumptions
| # | Assumption | Impact if wrong | To confirm with |
|---|---|---|---|
| A1 | ... | ... | ... |

### Open questions
| # | Question | Why it matters | Suggested owner |
|---|---|---|---|
| Q1 | ... | ... | ... |

## 10. Next steps
| Action | Owner | Due |
|---|---|---|
_Start with action items agreed in the session, then the actions needed to close the most important open questions._
```
