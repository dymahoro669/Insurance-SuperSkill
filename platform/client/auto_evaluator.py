"""
Auto Evaluator – Data Linkage Engine

Listens to telemetry events and automatically escalates evaluations:
  L1 score < 60                → trigger L2
  L2 overall < 60              → trigger L3
  |L2 overall – L1 score| > 20 → trigger L3

The evaluator can run as a one-shot processor or a background polling loop.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_PLATFORM_URL = "http://127.0.0.1:8080"
L1_L2_THRESHOLD = 60
L2_L3_THRESHOLD = 60
L2_L3_GAP_THRESHOLD = 20

# LLM endpoint used to generate evaluation content (OpenAI-compatible)
LLM_API_URL = os.getenv("LLM_API_URL", "http://127.0.0.1:8000/v1/chat/completions")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")

POLL_INTERVAL = int(os.getenv("AUTO_EVAL_POLL_INTERVAL", "30"))  # seconds


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _post(url: str, payload: Dict[str, Any], timeout: int = 60) -> Dict[str, Any]:
    headers = {"Content-Type": "application/json"}
    if LLM_API_KEY and "chat/completions" in url:
        headers["Authorization"] = f"Bearer {LLM_API_KEY}"
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        return {"status": "error", "message": str(exc)}


def _get(url: str, timeout: int = 30) -> Dict[str, Any]:
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        return {"status": "error", "message": str(exc)}


# ---------------------------------------------------------------------------
# LLM generation
# ---------------------------------------------------------------------------

def _call_llm(system_prompt: str, user_prompt: str) -> str:
    """Call the configured LLM and return the text content."""
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 2048,
    }
    data = _post(LLM_API_URL, payload)
    if data.get("status") == "error":
        return f"[LLM Error] {data.get('message', 'unknown')}"
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        return "[LLM Error] Unexpected response format"


def _generate_l2_evaluation(skill_id: str, event: Dict[str, Any]) -> Dict[str, Any]:
    system = (
        "You are an expert insurance AI evaluator. "
        "Assess the skill response across five dimensions and return ONLY a JSON object with keys: "
        "professional_score, practical_accuracy, scenario_coverage, executability, risk_awareness, overall, "
        "evaluation (string), improvements (list of strings), benchmark (string). "
        "Scores are integers 0-100."
    )
    user = (
        f"Skill: {skill_id}\n"
        f"User input: {event.get('user_input', '')}\n"
        f"L1 score: {event.get('l1_score', 'N/A')}\n"
        f"L1 verdict: {event.get('l1_verdict', 'N/A')}\n"
        f"Duration: {event.get('duration_ms', 'N/A')} ms\n"
        f"Tokens: {event.get('tokens_used', 'N/A')}\n"
        f"Model: {event.get('model', 'N/A')}\n"
        "Please provide the evaluation JSON."
    )
    raw = _call_llm(system, user)
    # Extract JSON from possible markdown fences
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        # Fallback placeholder
        result = {
            "professional_score": 70,
            "practical_accuracy": 70,
            "scenario_coverage": 70,
            "executability": 70,
            "risk_awareness": 70,
            "overall": 70,
            "evaluation": raw or "Auto-generated fallback evaluation.",
            "improvements": ["Review required after LLM parse failure"],
            "benchmark": "Industry standard",
        }
    return result


def _generate_l3_evaluation(skill_id: str, event: Dict[str, Any], l2_eval: Dict[str, Any]) -> Dict[str, Any]:
    system = (
        "You are a senior insurance domain expert conducting L3 expert arbitration. "
        "Assess the skill response and the L2 evaluation across four dimensions and return ONLY a JSON object with keys: "
        "professional_score, practical_score, compliance_score, overall, "
        "feedback (string), reviewer (string), expertise_level (string). "
        "Scores are integers 0-100."
    )
    user = (
        f"Skill: {skill_id}\n"
        f"Event ID: {event.get('event_id', '')}\n"
        f"User input: {event.get('user_input', '')}\n"
        f"L1 score: {event.get('l1_score', 'N/A')}\n"
        f"L2 overall: {l2_eval.get('overall', 'N/A')}\n"
        f"L2 evaluation: {l2_eval.get('evaluation', 'N/A')}\n"
        "Please provide the expert arbitration JSON."
    )
    raw = _call_llm(system, user)
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        result = {
            "professional_score": 70,
            "practical_score": 70,
            "compliance_score": 70,
            "overall": 70,
            "feedback": raw or "Auto-generated fallback L3 feedback.",
            "reviewer": "Auto-Arbiter",
            "expertise_level": "Senior",
        }
    return result


# ---------------------------------------------------------------------------
# Platform interaction
# ---------------------------------------------------------------------------

class AutoEvaluator:
    def __init__(self, platform_url: str = DEFAULT_PLATFORM_URL):
        self.platform_url = platform_url.rstrip("/")

    # -- event helpers ------------------------------------------------

    def fetch_recent_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        url = f"{self.platform_url}/api/v1/telemetry/events?limit={limit}"
        data = _get(url)
        return data.get("events", [])

    def fetch_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        # The platform does not expose a single-event GET; fetch recent and filter
        events = self.fetch_recent_events(limit=500)
        for ev in events:
            if ev.get("event_id") == event_id:
                return ev
        return None

    def fetch_l2(self, event_id: str) -> Optional[Dict[str, Any]]:
        url = f"{self.platform_url}/api/v1/evaluator/l2"
        data = _get(url)
        for ev in data.get("evaluations", []):
            if ev.get("event_id") == event_id:
                return ev
        return None

    # -- submission ---------------------------------------------------

    def submit_l2(self, event_id: str, skill_id: str, eval_data: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            "eval_id": f"L2-{event_id}",
            "skill_id": skill_id,
            "event_id": event_id,
            "professional_score": eval_data.get("professional_score", 70),
            "practical_accuracy": eval_data.get("practical_accuracy", 70),
            "scenario_coverage": eval_data.get("scenario_coverage", 70),
            "executability": eval_data.get("executability", 70),
            "risk_awareness": eval_data.get("risk_awareness", 70),
            "overall": eval_data.get("overall", 70),
            "evaluation": eval_data.get("evaluation", ""),
            "improvements": eval_data.get("improvements", []),
            "benchmark": eval_data.get("benchmark", ""),
        }
        url = f"{self.platform_url}/api/v1/evaluator/l2"
        return _post(url, payload)

    def submit_l3(self, event_id: str, skill_id: str, eval_data: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            "eval_id": f"L3-{event_id}",
            "skill_id": skill_id,
            "event_id": event_id,
            "reviewer": eval_data.get("reviewer", "Auto-Arbiter"),
            "expertise_level": eval_data.get("expertise_level", "Senior"),
            "professional_score": eval_data.get("professional_score", 70),
            "practical_score": eval_data.get("practical_score", 70),
            "compliance_score": eval_data.get("compliance_score", 70),
            "overall": eval_data.get("overall", 70),
            "feedback": eval_data.get("feedback", ""),
        }
        url = f"{self.platform_url}/api/v1/evaluator/l3"
        return _post(url, payload)

    # -- evaluation logic ---------------------------------------------

    def evaluate_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Run the full evaluation pipeline for a single event.

        Returns a summary dict indicating which evaluations were triggered.
        """
        event_id = event.get("event_id", "")
        skill_id = event.get("skill", "unknown")
        l1_score = event.get("l1_score", 100)

        result = {"event_id": event_id, "l1_score": l1_score, "l2_triggered": False, "l3_triggered": False}

        # L1 → L2
        if l1_score < L1_L2_THRESHOLD:
            l2_data = _generate_l2_evaluation(skill_id, event)
            l2_resp = self.submit_l2(event_id, skill_id, l2_data)
            result["l2_triggered"] = True
            result["l2_response"] = l2_resp
            l2_overall = l2_data.get("overall", 100)

            # L2 → L3
            gap = abs(l2_overall - l1_score)
            if l2_overall < L2_L3_THRESHOLD or gap > L2_L3_GAP_THRESHOLD:
                l3_data = _generate_l3_evaluation(skill_id, event, l2_data)
                l3_resp = self.submit_l3(event_id, skill_id, l3_data)
                result["l3_triggered"] = True
                result["l3_response"] = l3_resp

        return result

    def run_once(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch recent events and evaluate any that meet the criteria."""
        events = self.fetch_recent_events(limit=limit)
        results: List[Dict[str, Any]] = []
        for ev in events:
            # Skip already processed (naïve check via existing L2)
            if self.fetch_l2(ev.get("event_id", "")):
                continue
            results.append(self.evaluate_event(ev))
        return results

    def run_loop(self) -> None:
        """Run as a background daemon, polling continuously."""
        print(f"[AutoEvaluator] Starting background loop (poll interval={POLL_INTERVAL}s)")
        while True:
            try:
                results = self.run_once()
                triggered = [r for r in results if r.get("l2_triggered") or r.get("l3_triggered")]
                if triggered:
                    print(f"[AutoEvaluator] Processed {len(triggered)} events this cycle.")
                    for r in triggered:
                        print(f"  - {r['event_id']}: L2={r['l2_triggered']}, L3={r['l3_triggered']}")
            except Exception as exc:
                print(f"[AutoEvaluator] Error in loop: {exc}")
            time.sleep(POLL_INTERVAL)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Insurance-SuperSkill Auto Evaluator")
    parser.add_argument("--platform-url", default=DEFAULT_PLATFORM_URL, help="Platform base URL")
    parser.add_argument("--event-id", help="Evaluate a specific event ID")
    parser.add_argument("--daemon", action="store_true", help="Run as background polling daemon")
    parser.add_argument("--l2", action="store_true", help="Force L2 evaluation for event-id")
    parser.add_argument("--l3", action="store_true", help="Force L3 evaluation for event-id")
    args = parser.parse_args()

    evaluator = AutoEvaluator(platform_url=args.platform_url)

    if args.daemon:
        evaluator.run_loop()
        return

    if args.event_id:
        event = evaluator.fetch_event(args.event_id)
        if not event:
            print(f"Event not found: {args.event_id}")
            sys.exit(1)

        if args.l2:
            l2_data = _generate_l2_evaluation(event.get("skill", "unknown"), event)
            resp = evaluator.submit_l2(args.event_id, event.get("skill", "unknown"), l2_data)
            print(json.dumps(resp, indent=2, ensure_ascii=False))
            if args.l3:
                l3_data = _generate_l3_evaluation(event.get("skill", "unknown"), event, l2_data)
                resp3 = evaluator.submit_l3(args.event_id, event.get("skill", "unknown"), l3_data)
                print(json.dumps(resp3, indent=2, ensure_ascii=False))
            return

        if args.l3:
            # L3 requires an existing L2; try to fetch or generate one
            l2 = evaluator.fetch_l2(args.event_id)
            if not l2:
                l2_data = _generate_l2_evaluation(event.get("skill", "unknown"), event)
                evaluator.submit_l2(args.event_id, event.get("skill", "unknown"), l2_data)
            else:
                l2_data = l2
            l3_data = _generate_l3_evaluation(event.get("skill", "unknown"), event, l2_data)
            resp = evaluator.submit_l3(args.event_id, event.get("skill", "unknown"), l3_data)
            print(json.dumps(resp, indent=2, ensure_ascii=False))
            return

        # Default: auto pipeline
        result = evaluator.evaluate_event(event)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    # One-shot scan
    results = evaluator.run_once()
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
