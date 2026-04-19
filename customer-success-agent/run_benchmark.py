"""Benchmark runner: asks the agent Q&A pairs, evaluates with LLM-as-judge."""
import json
import os
import time
from datetime import datetime
from agent import agent_loop, model_call, read_file
from config import CONFIG

RATE_LIMIT_DELAY = 30  # seconds — free tier rate limit protection
MAX_RETRIES = 3


def api_call_with_retry(fn):
    """Rate limit retry wrapper."""
    for attempt in range(MAX_RETRIES):
        try:
            return fn()
        except Exception as e:
            if "429" in str(e) and attempt < MAX_RETRIES - 1:
                wait = RATE_LIMIT_DELAY * (attempt + 1)
                print(f"    Rate limit, waiting {wait}s...")
                time.sleep(wait)
            else:
                raise


def compute_score(results: list) -> float:
    """Composite benchmark score (0.0–1.0).

    Components:
      - Reliability (50%): [KAYNAK:] source attribution rate
      - Accuracy    (30%): LLM-as-judge correct rate
      - Format      (20%): routing correctness + constraint refusal compliance
    """
    if not results:
        return 0.0

    total = len(results)

    # --- Reliability (50%) ---
    reliability = sum(
        1 for r in results if r.get("deterministic", {}).get("has_source", False)
    ) / total

    # --- Accuracy (30%) ---
    accuracy = sum(1 for r in results if r.get("correct", False)) / total

    # --- Format (20%) ---
    format_checks = []
    for r in results:
        det = r.get("deterministic", {})
        if "correct_routing" in det:
            format_checks.append(det["correct_routing"])
        if "has_refusal" in det:
            format_checks.append(det["has_refusal"])

    format_score = sum(format_checks) / len(format_checks) if format_checks else 1.0

    return reliability * 0.5 + accuracy * 0.3 + format_score * 0.2


def run():
    with open("benchmarks/qa_pairs.json", encoding="utf-8") as f:
        pairs = json.load(f)

    results = []
    for i, pair in enumerate(pairs):
        if i > 0:
            time.sleep(RATE_LIMIT_DELAY)

        print(f"  [{i+1}/{len(pairs)}] {pair['id']}...", end=" ", flush=True)

        session = {"messages": []}
        try:
            response = api_call_with_retry(
                lambda: agent_loop(pair["question"], session)
            )
        except Exception as e:
            print(f"✗ (API error)")
            results.append({
                "id": pair["id"],
                "type": pair["type"],
                "correct": False,
                "reasoning": f"API error: {str(e)[:100]}",
            })
            continue

        time.sleep(RATE_LIMIT_DELAY)

        try:
            judgment = api_call_with_retry(
                lambda: judge(pair["question"], pair["expected_answer"], response)
            )
        except Exception:
            judgment = {"correct": False, "reasoning": "Judge API error"}

        det = deterministic_checks(pair, response, session)
        # Attach per-query trace metadata for latency + cost analysis
        trace = session.get("_last_trace", {}) if session else {}
        results.append({
            "id": pair["id"],
            "type": pair["type"],
            "correct": judgment["correct"],
            "grounded": judgment.get("grounded", True),
            "extra_claims": judgment.get("extra_claims", []),
            "reasoning": judgment["reasoning"],
            "deterministic": det,
            "duration_ms": trace.get("duration_ms"),
            "prompt_tokens": trace.get("prompt_tokens"),
            "completion_tokens": trace.get("completion_tokens"),
            "total_tokens": trace.get("total_tokens"),
        })
        det_flags = " ".join(f"[{k}]" for k, v in det.items() if not v)
        print(f"{'✓' if judgment['correct'] else '✗'}{' ' + det_flags if det_flags else ''}")

    correct = sum(1 for r in results if r["correct"])
    total = len(results)
    api_errors = sum(1 for r in results if "API error" in r.get("reasoning", ""))
    actual = total - api_errors

    print(f"\nBaseline: {correct}/{total} ({correct/total:.0%})")
    if api_errors:
        print(f"Excluding API errors: {correct}/{actual} ({correct/actual:.0%})")

    composite = compute_score(results)
    print(f"Composite score: {composite:.3f}")

    # Latency + Escalation metrics (from traces)
    try:
        from agent import load_traces
        traces = load_traces(days=1)
        if traces:
            durations = [t["duration_ms"] for t in traces if t.get("duration_ms")]
            avg_latency = sum(durations) / len(durations) if durations else 0
            tier3_count = sum(1 for t in traces if t.get("tier", 1) == 3)
            escalation_rate = tier3_count / len(traces) if traces else 0
            print(f"\nOperational metrics (last 24 hours):")
            print(f"  Average latency: {avg_latency/1000:.1f}s")
            print(f"  Escalation rate (Tier 3): {tier3_count}/{len(traces)} ({escalation_rate:.0%})")
            if avg_latency / 1000 > 5:
                print(f"  ⚠ Latency above target (>5s)")
            if escalation_rate > 0.15:
                print(f"  ⚠ Escalation rate above target (>15%)")
    except Exception:
        pass  # Skip silently if trace data is unavailable

    # Deterministic metric summary
    all_det = [r.get("deterministic", {}) for r in results if "deterministic" in r]
    if all_det:
        source_count = sum(1 for d in all_det if d.get("has_source", False))
        print(f"\nDeterministic metrics:")
        print(f"  Source attribution: {source_count}/{len(all_det)} ({source_count/len(all_det):.0%})")
        routing_checks = [d for d in all_det if "correct_routing" in d]
        if routing_checks:
            routing_ok = sum(1 for d in routing_checks if d["correct_routing"])
            print(f"  Routing accuracy: {routing_ok}/{len(routing_checks)} ({routing_ok/len(routing_checks):.0%})")
        refusal_checks = [d for d in all_det if "has_refusal" in d]
        if refusal_checks:
            refusal_ok = sum(1 for d in refusal_checks if d["has_refusal"])
            print(f"  Constraint compliance: {refusal_ok}/{len(refusal_checks)} ({refusal_ok/len(refusal_checks):.0%})")
        tool_checks = [d for d in all_det if "tool_call_accuracy" in d]
        if tool_checks:
            tool_ok = sum(1 for d in tool_checks if d["tool_call_accuracy"])
            print(f"  Tool call accuracy: {tool_ok}/{len(tool_checks)} ({tool_ok/len(tool_checks):.0%})")

    # Per-query-type P95 latency (March of Nines metric)
    from collections import defaultdict
    by_type = defaultdict(list)
    for r in results:
        if r.get("duration_ms"):
            by_type[r["type"]].append(r["duration_ms"])
    if by_type:
        print(f"\nPer-query-type latency (P95):")
        for qtype, durs in sorted(by_type.items()):
            durs_sorted = sorted(durs)
            p95 = durs_sorted[min(int(len(durs_sorted) * 0.95), len(durs_sorted) - 1)]
            median = durs_sorted[len(durs_sorted) // 2]
            target = 1000 if qtype in ("routing", "deadline") else 4000
            flag = " ⚠ >target" if p95 > target else ""
            print(f"  {qtype:12} median={median/1000:.1f}s  p95={p95/1000:.1f}s  (target={target/1000:.0f}s){flag}")

    # Token usage aggregate
    total_tokens = sum(r.get("total_tokens") or 0 for r in results)
    if total_tokens:
        print(f"\nToken usage: {total_tokens:,} total across {len(results)} queries  "
              f"(avg {total_tokens // max(len(results),1):,}/query)")

    # Grounding rate (T5.1: context adherence → hallucination proxy)
    judged = [r for r in results if "grounded" in r]
    if judged:
        grounded_count = sum(1 for r in judged if r.get("grounded"))
        print(f"Grounding rate: {grounded_count}/{len(judged)} ({grounded_count/len(judged):.0%})")
        ungrounded_ids = [r["id"] for r in judged if not r.get("grounded")]
        if ungrounded_ids:
            print(f"  Ungrounded: {', '.join(ungrounded_ids[:10])}")

    outfile = f"benchmarks/results_{datetime.now().strftime('%Y%m%d')}.json"
    with open(outfile, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nResults saved: {outfile}")


def deterministic_checks(pair, response, session=None):
    """Deterministic metrics that do not require an LLM."""
    checks = {}

    # 1. Source attribution — accept both [SOURCE:] (English) and [KAYNAK:] (Turkish) formats
    resp_lower = response.lower()
    checks["has_source"] = (
        "[source:" in resp_lower
        or "[kaynak:" in resp_lower
        or "bu konuda kesin bilgi veremiyorum" in resp_lower
    )

    # 2. Routing accuracy — role-based (post-sanitize); also matches compound like "head accountant"
    if pair["type"] == "routing":
        expected_lower = pair["expected_answer"].lower()
        routing_roles = [
            "payroll specialist", "head accountant", "document specialist",
            "general manager", "cs manager", "cs specialist", "lawyer", "accountant",
        ]
        expected_role = next((r for r in routing_roles if r in expected_lower), None)
        if expected_role:
            checks["correct_routing"] = expected_role in resp_lower

    # 3. Constraint enforcement — refusal markers present
    if pair["type"] == "constraint":
        refusal_markers = ["yapamam", "veremem", "verilmez", "paylaşılmaz", "yapılmaz",
                          "yorum yapamam", "yetkisi", "kapsam dışı", "tavsiye veremiyorum"]
        checks["has_refusal"] = any(m in resp_lower for m in refusal_markers)

    # 4. Tool call accuracy — heuristic expected tool from question keywords
    if session and "_last_trace" in session:
        trace = session["_last_trace"]
        tool_names = {tc.get("name") for tc in trace.get("tool_calls", [])}
        q_lower = pair["question"].lower()
        # Only apply heuristic where an expected tool is obvious from the question
        expected_tool = None
        if any(x in q_lower for x in ["nip", "firma", "müşteri"]) and any(
            x in q_lower for x in ["orlen", "kghm", "pzu", "cd projekt", "lpp", "allegro", "inpost", "zabka", "ccc", "dino"]
        ):
            expected_tool = "mastersheet_read"
        elif any(x in q_lower for x in ["vekaletname", "vat tarihi", "beyanname tarih", "zus bildirim", "jpk"]):
            # Either wiki_read or load_skill acceptable — check if any knowledge tool was called
            expected_tool = {"wiki_read", "load_skill"}
        if expected_tool:
            if isinstance(expected_tool, set):
                checks["tool_call_accuracy"] = bool(tool_names & expected_tool)
            else:
                checks["tool_call_accuracy"] = expected_tool in tool_names

    return checks


def _judge_model_call(messages):
    """T8: Use a separate model for the judge — should differ from the agent model (reduces bias)."""
    from openai import OpenAI
    judge_model = CONFIG.get("judge_model", "")
    # If no judge model is set or it matches the agent model, fall back to default model_call
    if not judge_model or judge_model == CONFIG["model"]:
        return model_call(messages, tools=None)
    client = OpenAI(api_key=CONFIG["api_key"], base_url=CONFIG["api_base"])
    try:
        return client.chat.completions.create(
            model=judge_model,
            messages=messages,
            temperature=0.1,
            max_tokens=512,
            timeout=120,
        ).choices[0].message
    except Exception:
        # Fallback: if judge model fails, use the agent model
        return model_call(messages, tools=None)


def judge(question, expected, actual):
    # T5.1: Dual check — factual accuracy + context adherence (hallucination rate)
    prompt = f"""You are conducting a benchmark evaluation. Evaluate the agent's answer on TWO axes:

Question: {question}
Expected answer: {expected}
Agent's answer: {actual}

AXIS 1 — Factual accuracy (tone/style irrelevant):
- Does the answer contain the CORE INFORMATION from the expected answer?
- Is there any INCORRECT or CONTRADICTORY information? (missing info is acceptable)

AXIS 2 — Context adherence (grounding):
- The agent is supposed to answer from a wiki/skill knowledge base or mastersheet (cited via [SOURCE:] or [KAYNAK:]).
- Did the agent STAY GROUNDED in cited sources, or did it volunteer EXTERNAL knowledge (e.g. asserting company NIP numbers, tax rates, names, dates that weren't from its tools)?
- An answer tagged "[SOURCE: general knowledge ...]" that merely cautions the user is still grounded (honest).
- An answer tagged any source but containing uncited specific facts is ungrounded.

Return JSON only:
{{"correct": true/false, "grounded": true/false, "reasoning": "one sentence covering both axes", "extra_claims": []}}

"extra_claims" lists factual statements in the agent's answer that appear to come from outside cited sources (may be empty)."""

    response = _judge_model_call(
        [{"role": "user", "content": prompt}]
    )
    try:
        parsed = json.loads(response.content.strip().replace("```json", "").replace("```", ""))
        # Provide safe defaults for new fields
        parsed.setdefault("grounded", True)
        parsed.setdefault("extra_claims", [])
        return parsed
    except Exception:
        return {"correct": False, "grounded": False, "reasoning": "Parse error", "extra_claims": []}


def run_silent():
    """Run the benchmark silently and return results only."""
    with open("benchmarks/qa_pairs.json", encoding="utf-8") as f:
        pairs = json.load(f)

    results = []
    for i, pair in enumerate(pairs):
        if i > 0:
            time.sleep(RATE_LIMIT_DELAY)

        session = {"messages": []}
        try:
            response = api_call_with_retry(
                lambda p=pair: agent_loop(p["question"], session)
            )
        except Exception:
            results.append({"id": pair["id"], "type": pair["type"], "correct": False,
                          "reasoning": "API error", "deterministic": {"has_source": False}})
            continue

        time.sleep(RATE_LIMIT_DELAY)

        try:
            judgment = api_call_with_retry(
                lambda p=pair, r=response: judge(p["question"], p["expected_answer"], r)
            )
        except Exception:
            judgment = {"correct": False, "reasoning": "Judge error"}

        det = deterministic_checks(pair, response)
        results.append({"id": pair["id"], "type": pair["type"], "correct": judgment["correct"],
                       "reasoning": judgment["reasoning"], "deterministic": det})
    return results


def format_failures(results):
    """Format failed results for display."""
    failures = [r for r in results if not r.get("correct", False)]
    if not failures:
        return "All questions answered correctly."
    lines = []
    for f in failures[:5]:
        lines.append(f"- {f['id']}: {f.get('reasoning', '?')[:100]}")
    return "\n".join(lines)


def extract_system_prompt(source):
    """Extract the SYSTEM_PROMPT string from agent.py."""
    marker_start = 'SYSTEM_PROMPT = """'
    marker_end = '"""'
    start = source.find(marker_start)
    if start == -1:
        return None, -1, -1
    start += len(marker_start)
    end = source.find(marker_end, start)
    if end == -1:
        return None, -1, -1
    return source[start:end], start, end


def hill_climb(iterations=3):
    """Meta-agent hill climbing: improve SYSTEM_PROMPT toward a narrow target.
    T16: isolated benchmark via subprocess instead of importlib.reload.
    Max daily iterations: 3 (safety limit).
    """
    import shutil
    import subprocess
    import hashlib

    MAX_DAILY_ITERATIONS = 3
    iterations = min(iterations, MAX_DAILY_ITERATIONS)

    program = read_file("program.md")

    print("=== Hill Climbing Starting ===\n")
    print("[0] Measuring baseline score...")
    baseline_results = run_silent()
    baseline_score = compute_score(baseline_results)
    print(f"[0] Baseline score: {baseline_score:.3f}\n")

    best_score = baseline_score

    for i in range(1, iterations + 1):
        print(f"[{i}] Meta-agent proposing a change...")

        shutil.copy("agent.py", "agent.py.backup")

        # Only pass the SYSTEM_PROMPT string — not the entire agent.py
        current_source = read_file("agent.py")
        prompt_text, prompt_start, prompt_end = extract_system_prompt(current_source)

        if prompt_text is None:
            print(f"[{i}] Could not extract SYSTEM_PROMPT, skipping.")
            os.remove("agent.py.backup")
            continue

        prompt = f"""You are a meta-agent. Your goal is to increase the benchmark score of the CS Agent.

Directives:
{program}

Current score: {best_score:.3f}
Latest benchmark results (failures):
{format_failures(baseline_results)}

Below is the agent's SYSTEM_PROMPT text. Propose a SINGLE small improvement to this text.
IMPORTANT: Copy the old_text field VERBATIM from the SYSTEM_PROMPT. It must match character for character.

--- SYSTEM_PROMPT START ---
{prompt_text}
--- SYSTEM_PROMPT END ---

Return in JSON format:
{{"old_text": "section to change (COPY VERBATIM FROM PROMPT)", "new_text": "replacement text", "reasoning": "why"}}

Return JSON only."""

        try:
            response = model_call([{"role": "user", "content": prompt}], tools=None)
            content = response.content.strip().replace("```json", "").replace("```", "")
            change = json.loads(content)
        except Exception as e:
            print(f"[{i}] Meta-agent parse error: {e}")
            os.remove("agent.py.backup")
            continue

        print(f"[{i}] Proposal: {change.get('reasoning', '?')[:80]}")

        old_text = change.get("old_text", "")
        new_text = change.get("new_text", "")

        if not old_text or old_text not in prompt_text:
            print(f"[{i}] old_text not found in SYSTEM_PROMPT, skipping.")
            os.remove("agent.py.backup")
            continue

        # Apply change inside SYSTEM_PROMPT, write back to agent.py
        new_prompt = prompt_text.replace(old_text, new_text, 1)
        modified = current_source[:prompt_start] + new_prompt + current_source[prompt_end:]
        with open("agent.py", "w", encoding="utf-8") as f:
            f.write(modified)

        print(f"[{i}] Running benchmark (isolated subprocess)...")
        try:
            # T16: run in isolated subprocess — instead of importlib.reload
            base = os.path.dirname(os.path.abspath(__file__))
            result = subprocess.run(
                ["python", os.path.join(base, "run_benchmark.py")],
                cwd=base, capture_output=True, text=True, timeout=600
            )
            # Parse score from subprocess output
            new_score = best_score  # Default: no change
            for line in result.stdout.split("\n"):
                if "Composite score:" in line:
                    try:
                        new_score = float(line.split(":")[-1].strip())
                    except ValueError:
                        pass
            if result.returncode != 0:
                raise RuntimeError(f"Benchmark subprocess error: {result.stderr[-200:]}")
        except Exception as e:
            print(f"[{i}] Benchmark error: {e}")
            shutil.copy("agent.py.backup", "agent.py")
            os.remove("agent.py.backup")
            continue

        if new_score > best_score:
            print(f"[{i}] Score improved: {best_score:.3f} → {new_score:.3f} Keeping change.")
            best_score = new_score
            os.remove("agent.py.backup")
            # T16: Save change log under traces/optimize/
            opt_dir = os.path.join(CONFIG["trace_dir"], "optimize")
            os.makedirs(opt_dir, exist_ok=True)
            opt_log = os.path.join(opt_dir, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(opt_log, "w") as f:
                json.dump({"score_before": baseline_score, "score_after": new_score,
                          "change": change, "timestamp": datetime.now().isoformat()}, f, indent=2)
        else:
            print(f"[{i}] Score dropped/unchanged: {best_score:.3f} → {new_score:.3f} Reverting.")
            shutil.copy("agent.py.backup", "agent.py")
            os.remove("agent.py.backup")

    print(f"\n=== Hill Climbing Complete ===")
    print(f"Start: {baseline_score:.3f} → Final: {best_score:.3f}")
    return best_score


def generate_qa_from_feedback():
    """Generate new Q&A pairs from negative feedback entries."""
    feedback_path = f"{CONFIG['trace_dir']}/feedback.jsonl"
    if not os.path.exists(feedback_path):
        print("Feedback file not found.")
        return

    negatives = []
    with open(feedback_path, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            if entry.get("rating", 0) < 0:
                negatives.append(entry)

    if not negatives:
        print("No negative feedback found.")
        return

    for neg in negatives[-5:]:
        prompt = f"""This feedback was marked as negative:
Session: {neg.get('session_id')}
Comment: {neg.get('comment', 'No comment')}

Generate a benchmark Q&A pair from this feedback.
Return in JSON format: {{"id": "feedback-NNN", "question": "...", "expected_answer": "...", "type": "procedure|routing|constraint|customer|deadline"}}

Return JSON only."""

        try:
            response = model_call([{"role": "user", "content": prompt}], tools=None)
            qa = json.loads(response.content.strip().replace("```json", "").replace("```", ""))

            with open("benchmarks/qa_pairs.json", "r", encoding="utf-8") as f:
                pairs = json.load(f)

            existing_ids = {p["id"] for p in pairs}
            if qa["id"] in existing_ids:
                qa["id"] = f"feedback-{len(pairs)+1:03d}"

            pairs.append(qa)
            with open("benchmarks/qa_pairs.json", "w", encoding="utf-8") as f:
                json.dump(pairs, f, ensure_ascii=False, indent=2)
            print(f"  New Q&A added: {qa['id']}")

        except Exception as e:
            print(f"  Q&A generation error: {e}")

    print(f"{len(negatives)} negative feedback entries processed.")


def analyze():
    """Load the latest benchmark results, categorize errors, and print an analysis report."""
    import glob as glob_mod

    # Find the latest results file
    files = sorted(glob_mod.glob("benchmarks/results_*.json"))
    if not files:
        print("No benchmark results file found. Run 'python run_benchmark.py' first.")
        return

    latest = files[-1]
    with open(latest, encoding="utf-8") as f:
        results = json.load(f)

    print(f"Analysis: {latest} ({len(results)} questions)\n")

    # Error categories
    categories = {
        "missing_source": [],
        "wrong_routing": [],
        "constraint_violation": [],
        "wrong_answer": [],
        "passed": [],
    }

    for r in results:
        det = r.get("deterministic", {})
        if r.get("correct", False) and det.get("has_source", True):
            categories["passed"].append(r)
        elif not det.get("has_source", True):
            categories["missing_source"].append(r)
        elif det.get("correct_routing") is False:
            categories["wrong_routing"].append(r)
        elif det.get("has_refusal") is False:
            categories["constraint_violation"].append(r)
        else:
            categories["wrong_answer"].append(r)

    total = len(results)
    print("=" * 50)
    print("  Error Analysis Report")
    print("=" * 50)
    print(f"\n  Passed: {len(categories['passed'])}/{total} ({len(categories['passed'])/total:.0%})")

    for cat, items in categories.items():
        if cat == "passed" or not items:
            continue
        print(f"\n  --- {cat.upper()} ({len(items)} errors) ---")
        for item in items[:5]:
            print(f"    {item['id']}: {item.get('reasoning', '?')[:80]}")

    # Priority suggestion
    error_cats = [(cat, items) for cat, items in categories.items() if cat != "passed" and items]
    if error_cats:
        worst = max(error_cats, key=lambda x: len(x[1]))
        print(f"\n  Priority fix: {worst[0]} ({len(worst[1])} errors)")
    else:
        print(f"\n  All questions passed!")
    print("=" * 50)


def regression_diff(strict=False):
    """T7: Compare the last two benchmark results and detect regressions.

    In --strict mode, returns exit code 1 if any regression is found (CI-ready).
    """
    import glob as glob_mod

    files = sorted(glob_mod.glob("benchmarks/results_*.json"))
    if len(files) < 2:
        # If no baseline exists, save the latest result as baseline
        if files:
            import shutil
            shutil.copy(files[-1], "benchmarks/baseline.json")
            print(f"Only one results file found. Saved as baseline: baseline.json")
        else:
            print("No benchmark results file found. Run 'python run_benchmark.py' first.")
        return False

    # Compare against baseline if it exists, otherwise against the previous run
    baseline_path = "benchmarks/baseline.json"
    if os.path.exists(baseline_path):
        old_path = baseline_path
        old_label = "baseline"
    else:
        old_path = files[-2]
        old_label = os.path.basename(old_path)

    new_path = files[-1]
    new_label = os.path.basename(new_path)

    with open(old_path, encoding="utf-8") as f:
        old_results = {r["id"]: r for r in json.load(f)}
    with open(new_path, encoding="utf-8") as f:
        new_results = {r["id"]: r for r in json.load(f)}

    # Compare
    regressions = []   # Previously correct, now wrong
    improvements = []  # Previously wrong, now correct
    new_questions = [] # Not present in previous run
    removed = []       # Not present in new run

    for qid, new_r in new_results.items():
        if qid not in old_results:
            new_questions.append(qid)
            continue
        old_r = old_results[qid]
        was_correct = old_r.get("correct", False)
        now_correct = new_r.get("correct", False)
        if was_correct and not now_correct:
            regressions.append((qid, new_r.get("reasoning", "?")))
        elif not was_correct and now_correct:
            improvements.append(qid)

    for qid in old_results:
        if qid not in new_results:
            removed.append(qid)

    # Score comparison
    old_correct = sum(1 for r in old_results.values() if r.get("correct", False))
    new_correct = sum(1 for r in new_results.values() if r.get("correct", False))
    old_total = len(old_results)
    new_total = len(new_results)

    print(f"{'=' * 55}")
    print(f"  Regression Diff: {old_label} vs {new_label}")
    print(f"{'=' * 55}")
    print(f"\n  Score: {old_correct}/{old_total} ({old_correct/old_total:.0%}) -> {new_correct}/{new_total} ({new_correct/new_total:.0%})")

    has_regression = len(regressions) > 0

    if regressions:
        print(f"\n  REGRESSION ({len(regressions)}):")
        for qid, reason in regressions:
            print(f"    {qid}: {reason[:80]}")

    if improvements:
        print(f"\n  IMPROVEMENT ({len(improvements)}):")
        for qid in improvements:
            print(f"    {qid}")

    if new_questions:
        print(f"\n  NEW QUESTIONS ({len(new_questions)}):")
        for qid in new_questions:
            status = "correct" if new_results[qid].get("correct") else "wrong"
            print(f"    {qid}: {status}")

    if removed:
        print(f"\n  REMOVED ({len(removed)}):")
        for qid in removed:
            print(f"    {qid}")

    if not regressions and not improvements and not new_questions and not removed:
        print(f"\n  No changes.")

    print(f"\n{'=' * 55}")

    if strict and has_regression:
        print(f"\n  STRICT MODE: {len(regressions)} regression(s) detected. Exit code 1.")
        return True  # Regression found

    return False


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--analyze":
        analyze()
    elif len(sys.argv) > 1 and sys.argv[1] == "--hill-climb":
        iterations = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        hill_climb(iterations)
    elif len(sys.argv) > 1 and sys.argv[1] == "--feedback":
        generate_qa_from_feedback()
    elif len(sys.argv) > 1 and sys.argv[1] == "--diff":
        strict = "--strict" in sys.argv
        has_regression = regression_diff(strict=strict)
        if strict and has_regression:
            sys.exit(1)
    elif len(sys.argv) > 1 and sys.argv[1] == "--set-baseline":
        # Save the latest results file as the baseline
        import glob as glob_mod, shutil
        files = sorted(glob_mod.glob("benchmarks/results_*.json"))
        if files:
            shutil.copy(files[-1], "benchmarks/baseline.json")
            print(f"Baseline saved: {files[-1]} -> baseline.json")
        else:
            print("No results file found.")
    else:
        run()
