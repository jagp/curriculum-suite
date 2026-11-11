# Competing-versions protocol

Every run of the skill ends the same way. It produces its **deliverable** three times, and the presenter picks one.

| Version | Persona | Brief |
|---|---|---|
| **A** | Primary | The skill's own method, done well. |
| **B** | Alternate seed | Same goal and inputs, but a genuinely different design choice. Not a copy with reworded text. Name the choice that differs. |
| **C** | Contrarian / resistance enforcer | Attacks A's premises. It fact-checks every claim about Claude's products against current docs, refuses anything that can't be verified or measured, and proposes the leaner or safer alternative. Default stance: "prove it." |

## Rules
1. **One sentence each.** Every version ends with a single sentence arguing for itself. No longer.
2. **The presenter decides.** No version is marked recommended. Claude may point out factual errors in any version, but it doesn't vote.
3. **Same deliverable format.** All three use the same output schema, so they can be compared side by side and only the content differs.
4. **Picks get logged.** Record which version was chosen and the reason the presenter gave (if any). Later runs read this log, so a run doesn't re-propose something already rejected.
5. **Independence is labeled honestly.** When all three come from one model in one conversation, the output says so: *"B and C are role-played by the same model, not independent runs."* True independence needs separate calls: subagents (Claude Code / Cowork) or separate sample calls with distinct system prompts.

## Measurable deliverable test
A deliverable passes only if someone other than its author could check it. That means it names counts, criteria, or yes/no conditions, not intentions.
