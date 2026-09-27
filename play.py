"""Cold-test harness for the UFA JEV Bake-Off (pilot track).

No JEV API key yet, so the decider here is a RANDOM POLICY, not JEV.
Every number below comes from the environment or this code.
After each game it appends the run to results.json, then commits and pushes.
"""
import json, subprocess, sys, time, statistics
import gymnasium as gym, ale_py

ENV_ID = "ALE/SpaceInvaders-v5"
SEEDS = [int(s) for s in sys.argv[1:]] or [1, 2]
MAX_STEPS = 500  # short episodes for the cold test

def load():
    try:
        return json.load(open("results.json"))
    except FileNotFoundError:
        return {
            "schema_version": 2,
            "models": [{"role": "decider", "provider": "none", "requested_model": "random-policy",
                        "served_model": "random-policy",
                        "notes": "Placeholder until a JEV key is issued. Not JEV."}],
            "config": {"env_id": ENV_ID, "frameskip": 4, "repeat_action_probability": 0.25,
                       "full_action_space": False, "obs_type": "ram", "wrappers": [],
                       "decision_interval_steps": 1, "max_steps_per_run": MAX_STEPS,
                       "state_encoding": "none (random policy ignores state)",
                       "ale_py_version": ale_py.__version__, "gymnasium_version": gym.__version__},
            "runs": [],
        }

def push(n, score):
    subprocess.run(["git", "add", "results.json"], check=True)
    subprocess.run(["git", "commit", "-m", f"results: run {n}, score {score}"], check=True)
    subprocess.run(["git", "push"], check=True)

def play(seed):
    gym.register_envs(ale_py)
    env = gym.make(ENV_ID, obs_type="ram")
    env.action_space.seed(seed)
    obs, info = env.reset(seed=seed)
    lives0, score, steps, lat = info["lives"], 0.0, 0, []
    t0 = time.perf_counter()
    term = trunc = False
    while not (term or trunc) and steps < MAX_STEPS:
        d0 = time.perf_counter()
        a = env.action_space.sample()
        lat.append((time.perf_counter() - d0) * 1000)
        obs, r, term, trunc, info = env.step(a)
        score += r; steps += 1
    env.close()
    q = statistics.quantiles(lat, n=20)
    return {"seed": seed, "score": int(score), "steps": steps,
            "frames": int(info["episode_frame_number"]), "lives_lost": lives0 - info["lives"],
            "terminated": bool(term), "truncated": bool(trunc or steps >= MAX_STEPS),
            "model_calls": 0, "decision_latency_ms_p50": round(statistics.median(lat), 4),
            "decision_latency_ms_p95": round(q[18], 4),
            "wall_clock_s": round(time.perf_counter() - t0, 3),
            "served_model": "random-policy",
            "notes": f"Cold test: random policy, capped at {MAX_STEPS} steps. No JEV key yet."}

if __name__ == "__main__":
    for seed in SEEDS:
        data = load()
        run = play(seed)
        data["runs"].append(run)
        json.dump(data, open("results.json", "w"), indent=2)
        print(json.dumps(run))
        push(len(data["runs"]), run["score"])
