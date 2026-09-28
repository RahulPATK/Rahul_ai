---
name: discovery-to-architecture
description: Turn client discovery workshop notes or transcripts into a structured AI solution design document with use cases, architecture, evals and guardrails, risks, and a phased roadmap (Proof of Value → Pilot → Production). Use this whenever the user shares notes, transcripts, whiteboard dumps or bullet lists from a discovery session, kickoff, requirements workshop or client call and wants a solution design, target architecture, SDD, proposal or "write this up properly" — even if they don't say "architecture". Includes regulatory mapping (EU AI Act, Consumer Duty, SS1/23, DORA, GDPR) for financial services clients.
---

# Discovery to Architecture

Discovery notes are messy: half-sentences, decisions mixed with brainstorming, owners mentioned in passing, early ideas overturned later in the session. The reader of a solution design needs the opposite — a clear problem, a justified architecture, honest risks and a credible path to production. Your job is to make that translation **faithfully**: organise, clarify and design from what was said, and make every gap visible rather than papering over it. A plausible-sounding invented detail is worse than an honest gap, because the client will make decisions from this document.

## Process

### 1. Extract facts

Read all the notes before writing anything (they may be pasted, in one file or across several). If there are no notes, ask for them rather than producing a generic document.

Pull out: problem and drivers, desired outcomes, users, current systems, data sources, constraints (budget, timeline, technology, regulation), stakeholders and owners, decisions, and open questions. Tag each fact:

- **[stated]** — said or written in the notes
- **[assumed]** — your inference; must also appear in the Assumptions table so the client can confirm or reject it

While extracting, watch for three things that commonly go wrong:

- **Decisions vs options.** Workshops brainstorm many ideas and settle on a few. Only record something as decided if the notes show agreement. Presenting a discarded idea as the design is the most damaging mistake you can make.
- **Later overrides earlier.** If a later note changes an earlier one (e.g. a launch date moves), the later one wins. Mention the change if it matters.
- **Requirements the stated systems can't support.** Cross-check each requirement against the systems described (e.g. "the bot must create returns" but the returns system has no API and only a read-only view is offered). Surface these as risks and open questions — they are often the most valuable finding in the document.

### 2. Frame use cases

For each candidate use case, give: the pattern (RAG, extraction, classification, summarisation, agent/tool use, generation, etc.), the success metric, and the data needed. Score each **High / Medium / Low** on value, feasibility, data readiness and risk, with a one-line reason per score grounded in the notes. If the notes don't support a score, mark it TBD rather than guessing. Recommend which use case(s) to lead with and why.

### 3. Design the architecture

Cover model choice, orchestration, retrieval and data, integrations, evals, guardrails, and cost and latency. Include a Mermaid diagram (`flowchart` or `sequenceDiagram`) showing only components that are stated or clearly labelled as proposed.

Distinguish three things clearly: what the client **decided**, what you **recommend**, and what is **open**. Recommending an approach is part of the job — just label it as a recommendation with a short rationale, and don't attribute it to the client. Don't invent specific figures for cost or latency; give the drivers and the order of magnitude only if you can justify it, otherwise make it an open question.

### 4. Assess risks

Table: risk, likelihood (H/M/L), impact (H/M/L), mitigation. Include delivery, data, technical, adoption and model risks (hallucination, bias, drift, prompt injection where relevant).

**Financial services clients** (banks, insurers, lenders, payments, wealth, pension providers): also map the solution to the relevant regulations. Read `references/fsi-regulatory.md` before doing this — it explains when each regulation applies and what it means for design. Only map what applies; say why each regulation is or isn't relevant rather than listing all five by default. You are not giving legal advice, so recommend confirming the mapping with the client's compliance team.

### 5. Build the roadmap

Three phases — **Proof of Value**, **Pilot**, **Production** — each with scope, key activities, and measurable exit criteria (the gate to the next phase). Use any dates, pilot sizes or targets from the notes; don't invent dates. Exit criteria should tie back to the use-case success metrics and the eval approach.

## Output

Write the document to a Markdown file — default `docs/solution-design-<client-or-project-slug>.md` unless the user names a location. Follow the structure in `references/template.md`:

1. Executive summary
2. Context
3. Current state
4. Use cases
5. Architecture
6. Evals and guardrails
7. Risks (and regulatory mapping for FSI)
8. Roadmap
9. Assumptions and open questions
10. Next steps

Then give the user a short summary in chat: what the solution is, the recommended lead use case, how many open questions remain, and the two or three most important gaps to close.

## Rules

- **Never invent client names, metrics, systems, people, or dates.** Where a section needs something the notes don't provide, write `TBD — see Q#` and add a matching open question.
- **Preserve specifics.** Keep exact figures, system names, acronyms and people's names and roles as written. Don't round "~40k tickets/month" into "high volume".
- **Open questions are an agenda.** Each should be specific and answerable, say why it matters, and suggest an owner where the notes indicate one. They often become the agenda for the next session.
- **Write for someone who wasn't in the room.** Expand shorthand on first use and give the context a newcomer needs.
- **Plain, concise British English** (organise, optimise, programme, licence as a noun). Prefer tables and bullets for list-shaped content. Aim for a document a client sponsor can read in 15 minutes.
