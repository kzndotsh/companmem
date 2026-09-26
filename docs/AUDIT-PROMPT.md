# Prompt for AUDIT.md one-shot analysis

Paste this before the contents of AUDIT.md. The combined input should be sent as a single user message to the model.

---

## Prompt text

You are going to read a field audit of 61 memory systems for AI agents and companions. Before you do, here is what you need to know about the mission and the problem.

**The mission:** Build the memory technology that makes the most human-like companion we can, then show it with a number someone else can rerun. We do not know yet what we are shipping, and we do not know yet what that number measures. The audit exists so we do not copy everyone else's extract-and-search pipeline. The missing piece is a number we would bet the company on — one that comes from running the same situation on our companion and on other products, then reading a result someone else can run again.

**What a companion is:** A companion is not a coding agent. It is not a RAG system over documents. It is a persistent relationship between the system and one specific person. It has its own identity, character, and voice. It maintains emotional and factual continuity across sessions. The relationship is supposed to deepen over time. Its failure modes are: forgetting what matters while remembering trivia; fabricating things the user never said; behaving differently after an update without explanation; or conflating what Alice said with what Bob said. The benchmark that matters is not "did the right passage come back" — it is "does the companion behave as if the past actually happened and mattered."

**What you are reading:** AUDIT.md is a field audit of 61 memory products, written by a human who read every audit JSON produced by a prior research pipeline. The top section is a synthesis — the auditor's own conclusions. The rest is one entry per product. The synthesis represents one analyst's read. It may be wrong. It may have blind spots. It may have overweighted the systems that are technically interesting and underweighted the ones that are practically important.

**Your job:** Evaluate the audit and its synthesis. Do not just summarize it back. Push back where you disagree. Find what was missed. Be specific.

Produce the following, in order:

1. **What the synthesis got right.** The two or three claims you most agree with, and why.

2. **What the synthesis missed or underweighted.** Specific products, patterns, or failure modes that deserved more attention than they got.

3. **What the synthesis overweighted.** Things that were given prominence but are less relevant to building a companion than the auditor assumed.

4. **Top 5 design decisions worth stealing.** Concrete, specific mechanisms from the audited products — not philosophies, not vibes. Things you would actually implement. Ranked by companion relevance. Include which product it comes from and what problem it solves.

5. **Top 5 failure modes to build against.** The most dangerous things that can go wrong in a companion memory system, based on what the audit documents. Concrete — "silent cursor advancement on LLM extraction failure" is a failure mode, "reliability" is not. Include which products documented it.

6. **What to build first.** One paragraph. Given the mission, what is the smallest thing that would tell us whether we are on the right track? This is a prioritization judgment, not a product roadmap.

7. **The sharpest open question.** The one thing the audit does not answer that we most need to figure out before writing code.

Be direct. If the synthesis is substantially right, say so. If it has a serious blind spot, name it. The goal is a sharper picture of the problem, not a validation of the prior work.

---

The full AUDIT.md follows below.
