import sys
import asyncio
from dotenv import load_dotenv

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

load_dotenv()

import cognee
from cognee.api.v1.search import SearchType


TEST_DATA = """
Repository: Demo Repo

Issue #23:
Authentication failed when requests were routed through a load balancer.

Pull Request #47:
Changed authentication from session-based authentication to JWT.

Reason:
Sessions require shared state across servers.
JWT is stateless and scales horizontally.

Developer:
Vaibhav Singh

Decision:
Use JWT instead of sessions.
"""


async def diagnostic():
    print("=" * 60)
    print("COGNEE DIAGNOSTIC")
    print("=" * 60)

    try:
        print("Pruning old data...")
        await cognee.prune.prune_data()
        await cognee.prune.prune_system(metadata=True)
        print("✓ Prune complete")
    except Exception as e:
        print("Prune failed:", e)

    try:
        print("\nAdding data...")
        await cognee.add(
            [TEST_DATA],
            dataset_name="diagnostic_dataset"
        )
        print("✓ Add complete")
    except Exception as e:
        print("Add failed:")
        print(e)
        return

    try:
        print("\nRunning cognify...")
        await cognee.cognify()
        print("✓ Cognify complete")
    except Exception as e:
        print("Cognify failed:")
        print(e)
        return

    for search_type in SearchType:
        print(f"\nTesting SearchType.{search_type.name}")

        try:
            result = await cognee.search(
                query_text="Why was JWT chosen over sessions?",
                query_type=search_type,
            )

            print(result)

        except Exception as e:
            print(e)

    print("\nDone.")


if __name__ == "__main__":
    asyncio.run(diagnostic())