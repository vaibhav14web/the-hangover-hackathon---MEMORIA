import json
import os
import requests
from typing import Any, Dict

API_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
DEMO_CACHE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cache", "demo_responses.json"))


def load_demo_cache() -> Dict[str, Any]:
    try:
        with open(DEMO_CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        print(f"Failed to load demo cache: {exc}")
        return {}


def query_api(query: str) -> Dict[str, Any]:
    response = requests.post(
        f"{API_URL}/query",
        json={"query": query},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def print_answer(label: str, data: Dict[str, Any]) -> None:
    print(f"\n=== {label} ===")
    print("Answer:")
    print(data.get("answer", "<no answer>"))
    print("Retrieval method:", data.get("retrieval_method", "UNKNOWN"))
    citations = data.get("citations", [])
    if citations:
        print("Citations:")
        for cit in citations:
            print(f" - {cit.get('label', cit)}")
    else:
        print("Citations: none")


def main() -> None:
    demo_cache = load_demo_cache()
    if not demo_cache:
        print("No demo cache available. Please ensure cache/demo_responses.json exists.")
        return

    questions = list(demo_cache.keys())
    print(f"Using API URL: {API_URL}")
    print(f"Found {len(questions)} demo questions in cache.")

    for question in questions:
        print(f"\n---\nQuery: {question}")
        try:
            result = query_api(question)
            print("Live query succeeded.")
            print_answer("Live Result", result)
        except Exception as exc:
            print(f"Live query failed: {exc}")
            fallback = demo_cache.get(question)
            if fallback:
                print("Using cached fallback answer.")
                print_answer("Cached Result", fallback)
            else:
                print("No cached fallback available for this query.")


if __name__ == "__main__":
    main()
