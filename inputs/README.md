# inputs/

Drop-in folder for everything a run consumes. Git ignores every file here except this
README, so inputs stay on the machine that supplies them. The skills and gates in this
repo are input-agnostic: they read from here at runtime and never carry input data.

| Path | What goes there |
|---|---|
| `client-terms.txt` | Terms the client-term gate blocks, one per line (`#` comments; a leading `=` matches case exactly) |
| `fixture/inputs.json` | Inputs for an end-to-end fixture run (schema `h0-inputs`) |

Anything else a run needs (reference material, earlier runs) can live here too.
