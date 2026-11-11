# Skills list

Goal: Each team lead uses Claude to draft the weekly team report from the team's task tracker and checks every line against it before sending.

Leaves of the capability tree, in an order where nothing a leaf needs comes after it.

1. Open a conversation with Claude and send it a written request (N6)
   - Floor (inputs_stop): Profile says participants are new to Claude; the inputs do not say which Claude product they use or how they get access, so nothing earlier can be derived.
2. Give Claude the tracker export as the source to draft from, by attaching or pasting it into the conversation (N4)
   - Needs first: N6
   - Floor (inputs_stop): Remaining prerequisites are already nodes: N6. The inputs do not say who produces the tracker export or in what form, and exporting happens outside Claude, so it is a gap, not a node.
   - Data: Tracker export used for the lead's real weekly report [read-only]
   - Data: Tracker file used for practice reports [sample]
   - Claim (verify): Claude can read a tracker export that is attached to or pasted into a conversation.
3. Tell Claude what the weekly report must contain and how it should read (N5)
   - Needs first: N6
   - Floor (profile): Profile: team leads already write the weekly report by hand, so they know what it must contain; remaining prerequisites are already nodes: N6.
4. Ask Claude for a first draft, then tell it what to change and judge whether each revision is better (N7)
   - Needs first: N4, N5
   - Floor (profile): Profile: team leads already write the weekly report by hand, so they can judge a draft and say what to change; remaining prerequisites are already nodes: N4, N5.
   - Claim (verify): Claude revises its own draft in response to follow-up requests in the same conversation.
5. Ask Claude to list, for each line of its draft, the tracker export row the line is based on (N8)
   - Needs first: N4
   - Floor (profile): Remaining prerequisites are already nodes: N4 (and the draft, N2). Leads write the report by hand, so naming what a line claims is familiar.
   - Claim (verify): Claude can point to the row of a supplied file that a line of its draft is based on.
6. Compare each draft line with the tracker row Claude pointed to and decide whether the row supports the line (N9)
   - Needs first: N8
   - Floor (domain_knowledge): Glossary: the task tracker is the tool the team logs its work in, so leads can read their own team's rows. Reading status values depends on 'status code', which is UNRESOLVED (see gaps).
   - Data: Tracker export the draft is checked against [read-only]
7. Flag each line the tracker does not support and record the tracker row it was checked against (N10)
   - Needs first: N9
   - Floor (profile): Profile: team leads already write the weekly report by hand, so marking one of its lines as unsupported needs nothing new; remaining prerequisites are already nodes: N9.

## Gaps

- undefined_term — status code: Glossary marks it UNRESOLVED: the tracker's status values are not yet listed. Checking a line that reports a task's status (N9) depends on it.
- undefined_term — line: The goal, W3 and C2 require checking 'every line' and flagging a line, but the glossary does not say what counts as a line of the report (a sentence, a bullet, an item).
- undefined_term — tracker export: C1 and the constraints use 'tracker export', but the glossary does not define its form or contents (which fields, which period).
- other: The inputs do not say who produces the tracker export or how. Exporting is done outside Claude, so it is not a node; N4 stops here.
- other: The inputs do not say which Claude product or surface participants use, or how they get access. N6 stops here.

## Set aside

- "Two 90-minute sessions." — Delivery constraint (time and session count); the tree is about capability only, so it does not size, split or merge any node.
