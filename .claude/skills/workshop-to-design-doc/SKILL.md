---
name: workshop-to-design-doc
description: Turn raw workshop, discovery-session, or meeting notes into a structured Solution Design Document in Markdown. Use this whenever the user shares notes, transcripts, whiteboard dumps, or bullet lists from a workshop, kickoff, requirements session, or client call and wants a design doc, solution design, SDD, technical design, proposal, or "write this up properly" — even if they don't say "solution design" explicitly. Works for software, AI/agent, and business-process solutions.
---

# Workshop Notes → Solution Design Doc

Workshop notes are messy: half-sentences, decisions mixed with brainstorming, owners mentioned in passing, contradictions between early and late discussion. The reader of a solution design doc needs the opposite — a clear statement of the problem, the chosen approach, and what's still undecided. Your job is to do that translation **faithfully**: organize and clarify what was said, never invent what wasn't.

## Workflow

1. **Get the notes.** They may be pasted inline, in a file path, or spread across several files. Read all of them before writing anything. If there are no notes at all, ask for them rather than producing a generic template.

2. **Extract before you write.** Make a quick internal pass and sort every meaningful statement into buckets:
   - Problem / pain points / business drivers
   - Goals, success metrics, KPIs
   - Scope (in / out), constraints (budget, timeline, tech, compliance)
   - Stakeholders, users, owners
   - Current state
   - Proposed solution: components, flows, data, integrations, tools, models
   - **Decisions** (something was agreed) vs. **options** (still being weighed)
   - Risks, dependencies, assumptions
   - Action items and open questions

   Separating decisions from options matters most: workshops brainstorm many ideas and settle on a few. Presenting a discarded idea as the design is the most damaging mistake you can make here. If a later note overrides an earlier one, the later one wins — and mention the change if it's significant.

3. **Pick the sections.** Start from the template in `references/template.md`. It is a superset: keep the core sections always, and include optional sections only when the notes contain material for them (e.g., "AI / Model Design" only for AI solutions, "Process Changes" only for business-process work). An empty optional section is noise; an empty core section becomes an open question.

4. **Write the doc.** Follow the template's structure and the writing rules below.

5. **Save and report.** Write the doc to a Markdown file — default `docs/solution-design-<short-slug>.md` unless the user names a location — and give the user a short summary: what the solution is, how many open questions remain, and the 2–3 most important gaps to close.

## Writing rules

- **No fabrication.** Every requirement, number, name, date, system, and decision must trace back to the notes. If a section needs something the notes don't provide, write `**TBD** — see Open Questions (Q#)` and add a matching entry to the Open Questions section. Readers will make decisions from this doc; a plausible-sounding invented detail is worse than an honest gap.
- **Reasonable inference is OK, but label it.** If the notes strongly imply something (e.g., "integrate with their Salesforce" implies a CRM integration component), you may state it. If you're connecting dots the participants didn't, mark it _(inferred)_.
- **Preserve specifics.** Keep exact figures, system names, acronyms, and people's names/roles as written. Don't round "~40k tickets/month" into "high volume."
- **Attribute decisions.** When the notes say who decided or owns something, keep it.
- **Write for someone who wasn't in the room.** Expand shorthand on first use, turn fragments into full sentences, and give context a newcomer would need.
- **Be concise.** Tables and bullets over paragraphs where the content is list-shaped. Aim for a doc someone can read in 10 minutes.
- **Diagrams:** when the notes describe components talking to each other or a multi-step flow, include a Mermaid diagram (`flowchart` or `sequenceDiagram`) in the Architecture section. Only include elements that appear in the notes.

## Open Questions section

This is often the most valuable part of the doc for the team, because it becomes the agenda for the next session. Each question should be specific and answerable, and say why it matters:

| # | Question | Why it matters | Suggested owner |
|---|----------|----------------|-----------------|
| Q1 | What is the target response time for the chatbot? | Drives model choice and hosting cost | TBD |

Include: explicit questions raised in the workshop, gaps you found while filling core sections, and contradictions in the notes you couldn't resolve.

## Reference files

- `references/template.md` — the full document template with core and optional sections. Read it before writing.
