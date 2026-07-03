# graph/manual_context.py

MANUAL_PR_CONTEXT = {
    9816: """
Additional context (from linked discussion #9709 and FastAPI migration docs):
FastAPI migrated from Pydantic v1 to Pydantic v2 to take advantage of major 
performance improvements (Pydantic v2's core was rewritten in Rust) and to 
align with the Pydantic ecosystem's direction, since Pydantic v1 was being 
deprecated. The migration was done incrementally: FastAPI 0.100.0 added 
initial support for either v1 or v2. Later versions (0.119.0+) added a 
compatibility layer (pydantic.v1) to help users migrate gradually before 
v1 support was fully dropped in 0.126.0+. Community members reported 
switching entire codebases (60+ files) with minimal breakage, validating 
the migration path. The maintainer (tiangolo) explicitly prioritized 
backward compatibility during the transition to avoid breaking the 
ecosystem of dependent packages.
"""
}