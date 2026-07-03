import asyncio
import sys
import os
import json
from dotenv import load_dotenv

# Ensure root of project is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()
os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"

from reasoning.query_engine import QueryEngine

DEMO_QUESTIONS = [
    "Why did FastAPI migrate to Pydantic v2?",
    "What broke when FastAPI refactored Depends to use dataclasses?",
    "What are the supported dependency scopes in FastAPI?"
]

async def build_cache():
    print("=" * 60)
    print("BUILDING DEMO RESPONSES CACHE")
    print("=" * 60)
    
    engine = QueryEngine()
    cache = {}
    
    # We temporarily delete the cache to force live execution
    cache_path = "cache/demo_responses.json"
    if os.path.exists(cache_path):
        try:
            os.remove(cache_path)
        except Exception:
            pass

    for q in DEMO_QUESTIONS:
        print(f"\nQuerying: '{q}'...")
        try:
            res = await engine.execute_query(q)
            print("Answer:", res["answer"])
            print("Citations:", res["citations"])
            cache[q] = res
        except Exception as e:
            print(f"Error querying '{q}': {e}")
            
    # Write back to cache
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)
        
    print("\n✓ Cache built successfully and saved to cache/demo_responses.json!")

if __name__ == "__main__":
    asyncio.run(build_cache())
