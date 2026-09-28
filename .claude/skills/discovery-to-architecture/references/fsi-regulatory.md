# FSI Regulatory Mapping

Use this when the client is a financial services firm. For each regulation, decide whether it applies from what the notes say (jurisdiction, firm type, use case, customers affected) and state why. If jurisdiction or firm type isn't clear, raise it as an open question — it determines most of the mapping.

This is orientation for solution design, not legal advice. Application dates and guidance change, so recommend the client's compliance team confirm the mapping and current timelines.

## Quick applicability guide

| Regulation | Jurisdiction | Applies when |
|---|---|---|
| EU AI Act | EU (and non-EU providers placing AI on the EU market or whose output is used in the EU) | Almost any AI system used in or aimed at the EU; obligations scale with risk tier |
| Consumer Duty | UK (FCA-regulated firms) | The solution affects outcomes for retail customers |
| PRA SS1/23 | UK (PRA-regulated banks and building societies) | The solution includes models, including AI/ML, used in decisions or risk management |
| DORA | EU financial entities | The solution relies on ICT services, including cloud or LLM providers |
| GDPR / UK GDPR | EU / UK | Personal data is processed |

## EU AI Act

**What it is:** risk-based regulation of AI systems and general-purpose AI models.

**Key tests:**
- **Prohibited practices** — e.g. manipulative techniques or social scoring. Rarely relevant, but check.
- **High-risk (Annex III)** — in FSI, notably AI used to **evaluate creditworthiness or establish credit scores** of natural persons (fraud detection is carved out) and **risk assessment and pricing for life and health insurance**. High-risk systems carry obligations for risk management, data governance, technical documentation, record-keeping and logging, transparency to deployers, human oversight, and accuracy, robustness and cybersecurity.
- **Transparency obligations** — people must be told when they are interacting with an AI system such as a chatbot, and some AI-generated content must be marked.
- **Limited or minimal risk** — most internal productivity, summarisation and search use cases. Few obligations beyond transparency and AI literacy.

**Design implications:** classify each use case by risk tier in the Risks section. For high-risk use cases, plan for human oversight, logging and documentation from Proof of Value onwards rather than bolting them on later. Add an AI disclosure to customer-facing assistants. Obligations apply in stages, so record which ones matter for the proposed Production date and ask compliance to confirm current dates.

## Consumer Duty (FCA, UK)

**What it is:** a standard that firms act to deliver good outcomes for retail customers.

**Structure:** the cross-cutting rules (act in good faith, avoid causing foreseeable harm, enable and support customers to pursue their financial objectives) and four outcomes: **products and services**, **price and value**, **consumer understanding**, and **consumer support**.

**Design implications:**
- **Consumer understanding:** AI-generated customer communications must be clear, accurate and not misleading. Evals should test for this.
- **Consumer support:** don't create sludge. Customers must be able to reach a human easily, especially to complain, cancel or switch.
- **Vulnerable customers:** detect signs of vulnerability and route those customers appropriately.
- **Monitoring:** firms must evidence outcomes, so log and monitor outcomes by customer segment, including vulnerable customers.

## PRA SS1/23 — Model risk management principles for banks (UK)

**What it is:** PRA expectations for model risk management. It applies directly to banks with internal model (IRB) approval and is widely treated as good practice by other PRA-regulated firms. It explicitly covers AI and ML models.

**Five principles:** (1) model identification and classification (a model inventory and risk tiering); (2) governance (board oversight and a senior manager accountable for model risk); (3) model development, implementation and use; (4) independent model validation; (5) model risk mitigants, including post-model adjustments and restrictions on use.

**Design implications:** register LLM-based components in the model inventory with a risk tier. Document the intended use and its limitations. Plan independent validation before Production, and use the eval suite as validation evidence. Monitor performance and drift continuously. Define fallback behaviour when the model is unavailable or underperforming. Third-party models such as hosted LLMs still need to be covered.

## DORA — Digital Operational Resilience Act (EU)

**What it is:** EU regulation on ICT risk for financial entities, in application since January 2025.

**Pillars:** ICT risk management; ICT incident classification and reporting; digital operational resilience testing; ICT third-party risk management (including the register of information and mandatory contract provisions); information sharing. Critical ICT third-party providers are subject to direct EU oversight.

**Design implications:** an LLM or cloud AI provider is an ICT third-party provider. Include it in third-party risk assessment and the register of information, and check contract terms (audit rights, exit strategy, incident notification). Design for resilience with fallbacks and degraded modes. Include AI components in incident management and resilience testing.

**UK note:** DORA doesn't apply to UK-only firms. The UK equivalents are the operational resilience regime (important business services and impact tolerances) and the critical third parties regime. Flag these instead where relevant.

## GDPR / UK GDPR

**Design implications:**
- **Lawful basis and purpose limitation** for each use of personal data, including use for evaluation and improvement.
- **DPIA:** likely required for novel AI processing of customer data. Plan it in Proof of Value.
- **Automated decision-making (Article 22):** decisions based solely on automated processing with legal or similarly significant effects, such as credit decisions, need a valid condition and safeguards, including the right to human intervention and an explanation. The UK regime has been amended, so ask compliance to confirm the current position.
- **Data minimisation:** redact or pseudonymise before sending data to the model where possible, and set retention limits on prompts and logs.
- **Processors and transfers:** a data processing agreement with the model provider, and a check on where data is processed and whether international transfer mechanisms are needed.
- **Data subject rights:** make sure logs and any vector stores can support access and erasure requests.
