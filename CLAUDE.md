# Project rules for Claude Code

This file loads into every session in this folder, including worker agents. It deliberately says nothing about any client, about the project's purpose, or about its history.

## First: which role are you?
- **Worker** (you were handed a task spec, or a prompt that names a sandbox/folder and files): follow the **Worker rules** below. Do not read `HANDOFF-v3.md`.
- **Coordinator** (the project owner opened this session to run the project): read `HANDOFF-v3.md`, and nothing else, before acting. Its "Hard rules" section binds you. You are the only session that sees the full scope.
- Unsure? Ask the project owner before reading anything.

## Worker rules (strict)
1. **Stay on your exact task.** Your spec defines your inputs and outputs. Do nothing outside it.
2. **Read only the files your task names.** Do not list, glob, grep or browse outside your task folder "to get oriented". Do not open `HANDOFF*`, `decisions.md` or any other file your task does not name, even if something you read suggests it.
3. **Write only the files your task names**, in the location it names.
4. **Don't fill gaps from elsewhere.** If an input is missing or ambiguous, say so in your report (or mark it as the schema allows). Don't look for it in the repo, in memory or on the web, unless your task names the source.
5. **No client knowledge.** Use only the data your inputs contain. Don't add examples, names or domain facts from anywhere else.
6. **Report only what your task asks for.**
7. **Use the reference files your task names** to inform your method as a whole.

