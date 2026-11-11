# Skills list

Goal: Each team lead uses Claude to draft the weekly team report from the team's task tracker and checks every line against it before sending.

1. Ask Claude for a first draft by stating what the document is, who reads it and what it must contain. (N4)
2. Give Claude a tracker export as the source it must draft the report from. (N5) - needs: N4
3. Revise Claude's draft by telling it what to change and reading the revised version. (N6) - needs: N4
4. Check each line of Claude's draft against the tracker export and flag every line the export does not support, naming the tracker row it was checked against. (N3) - needs: N2

## Open gaps

- undefined_term - line: The goal says "checks every line" but the glossary does not define what counts as a line of the weekly report (sentence, bullet, figure). N3 depends on it; not defined here.
- undefined_term - tracker export: Used in criterion C1 and the constraints; the glossary defines "task tracker" but not the export (its format or contents). N3 and N5 depend on it.
- undefined_term - status code: The glossary marks it UNRESOLVED ("the tracker's status values are not yet listed"). Not used in the goal, weekly goals or constraints, so no node depends on it.
- other - other: The inputs do not name which Claude product or surface participants use. N4 and N5 stop splitting here, and their product claims carry verify: true.
