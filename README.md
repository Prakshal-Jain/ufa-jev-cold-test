# ufa-jev-cold-test

End-to-end test entry for the UFA JEV Bake-Off (Space Invaders, pilot track).

Status: no JEV API key yet, so `play.py` runs a **random policy**, not JEV. No LLM baseline yet.
Runs in `results.json` are labeled `served_model: "random-policy"`.

## Run

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python play.py 1 2   # one game per seed; appends to results.json, commits, pushes after each
```
