import os
import logging
import asyncio
from typing import Optional
from litellm import acompletion
from litellm.exceptions import RateLimitError
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

# Map generic LLM keys from .env to provider-specific keys for LiteLLM
if os.getenv("LLM_API_KEY"):
    os.environ["GROQ_API_KEY"] = os.getenv("LLM_API_KEY") or ""

DEFAULT_MODEL = os.getenv("LLM_MODEL", "groq/llama-3.3-70b-versatile")

SYSTEM_PROMPT = """You are the AI Institutional Memory Engine for a software repository.
Your task is to answer user queries using ONLY the retrieved context (graph facts, repository structures, issues, pull requests, files).

Rules:
1. Provide a direct, detailed answer, referencing files, classes, methods, pull request numbers, and issues where possible.
2. Rely strictly on the provided context evidence. If the context does not contain enough information to confidently answer the query, respond exactly with:
   "I do not have enough evidence to answer confidently."
3. Do not assume or extrapolate beyond the provided text.
4. Support your answer with a list of citations of files, PRs, and issues.
"""

async def query_llm(query: str, context: str, model: Optional[str] = None) -> str:
    """
    Sends a query and context payload to Groq via LiteLLM with rate-limit retries.
    """
    model_name = model or DEFAULT_MODEL
    
    user_content = f"""USER QUERY: {query}

RETRIEVED CONTEXT EVIDENCE:
---
{context}
---

Provide your evidence-backed answer below:"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content}
    ]

    max_retries = 5
    base_delay = 5.0

    for attempt in range(1, max_retries + 1):
        try:
            logger.info("Calling LLM (model=%s) for reasoning (attempt %d/%d)...", model_name, attempt, max_retries)
            response = await acompletion(
                model=model_name,
                messages=messages,
                temperature=0.0, # Deterministic answers
            )
            answer = response.choices[0].message.content
            logger.info("LLM responded successfully.")
            return answer
        except Exception as e:
            err_str = str(e).lower()
            is_rate_limit = (
                isinstance(e, RateLimitError) or
                "rate limit" in err_str or
                "429" in err_str or
                "limit reached" in err_str
            )
            if is_rate_limit and "llama-3.3-70b-versatile" in model_name:
                logger.warning("LLM model llama-3.3-70b-versatile rate-limited. Falling back to groq/llama-3.1-8b-instant...")
                model_name = "groq/llama-3.1-8b-instant"
                continue
            elif is_rate_limit and attempt < max_retries:
                sleep_time = base_delay * attempt
                logger.warning("LLM API call rate-limited. Retrying in %.1fs... Error: %s", sleep_time, e)
                await asyncio.sleep(sleep_time)
            else:
                logger.error("LLM API call failed on attempt %d: %s", attempt, e)
                raise RuntimeError(f"LLM reasoning failed: {e}")

    raise RuntimeError("LLM reasoning failed: Max retries exceeded due to rate limits.")
