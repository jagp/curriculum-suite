# Skills list

Goal: Each team lead uses Claude to draft the weekly team report from the team's task tracker and checks every line against it before sending.

1. Start a conversation with Claude and send it a written request. (N5, parent N2)
2. Write a request that tells Claude what to draft, who it is for and what it must contain. (N6, parent N2) [after N5; data: Material Claude drafts the first practice draft from (weekly goal W1) (UNRESOLVED)]
3. Ask Claude to revise a draft by naming the specific changes you want. (N7, parent N2) [after N6]
4. Give Claude the tracker export to work from in the conversation. (N8, parent N3) [after N5; data: The team's tracker export for the real report (read-only); data: The sample tracker file for practice reports (sample); has product claims to verify]
5. Ask Claude to draft the weekly report using only what the tracker export shows. (N9, parent N3) [after N6, N8; has product claims to verify]
6. Ask Claude to name, for each line of the draft, the tracker export row it comes from. (N10, parent N4) [after N8, N9; has product claims to verify]
7. Open the tracker export and confirm each line against the row Claude named, finding the row yourself where Claude named none. (N11, parent N4) [after N10; data: The team's tracker export the draft was made from (read-only); data: The sample tracker file when checking a practice report (sample)]
8. Flag each line the export does not support, note the row it was checked against, and ask Claude to correct or remove it. (N12, parent N4) [after N11, N7]

## Open gaps

- data_provenance N6: Weekly goal W1 asks for a first draft, but the inputs do not say what Claude drafts it from (sample tracker file, the participant's own material, or something else).
- undefined_term status code: The glossary marks it UNRESOLVED ('the tracker's status values are not yet listed'); reading export rows to draft (N9) and check lines (N11) depends on it.
- undefined_term tracker export: Used in the constraints ('Tracker exports') and criteria, but not in the glossary: what an export contains and its form are not defined. 'sample tracker file' is likewise undefined.
- other N8: The inputs do not say who produces the tracker export for a real report or how; producing it is outside Claude, so N8 stops at inputs_stop.
- other N5: The inputs do not say which Claude product, plan or surface participants use, so the claims on N8, N9 and N10 are marked verify.
