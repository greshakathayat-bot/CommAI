"""
LangChain AI agent powered by ChatWxO (watsonx Orchestrate) with the
wxo-docs MCP server for product capability lookups.

The agent:
1. Receives a raw meeting transcript
2. Extracts client updates (requirements, feedback, blockers, action items)
3. Identifies solution opportunities
4. Matches opportunities against watsonx Orchestrate product capabilities
   via the wxo-docs MCP server
"""

import json
import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# ── System prompts ─────────────────────────────────────────────────────────────

EXTRACTION_SYSTEM_PROMPT = """You are a sales intelligence assistant. Your job is to analyze
meeting transcripts between sales representatives and clients.

When given a transcript, you must extract:
1. CLIENT UPDATES — specific requirements, feedback, blockers, and action items communicated
   by the client. Each update should include:
   - category: one of "requirement", "feedback", "blocker", "action_item", "context"
   - summary: a concise 1-2 sentence summary
   - verbatim_quote: the exact words from the transcript that support this update
   - speaker: who said it (if identifiable)
   - priority: "low", "medium", or "high"

2. OPPORTUNITIES — business problems or needs that could be solved with a product/solution.
   Each opportunity should include:
   - title: a short descriptive title
   - description: what the client needs and why
   - matched_product: the watsonx Orchestrate product/capability that addresses this need
   - matched_capability: specific capability or feature
   - confidence_score: 0.0 to 1.0
   - agent_reasoning: why you matched this opportunity to this product

Always respond in valid JSON with this structure:
{
  "updates": [...],
  "opportunities": [...]
}
"""

SOLUTION_MATCHING_SYSTEM_PROMPT = """You are a solution architect familiar with watsonx Orchestrate
capabilities. Given a client requirement or pain point, identify the best matching
watsonx Orchestrate product capability.

Use your knowledge of watsonx Orchestrate to:
- Match automation needs to AI agents and skills
- Match workflow needs to orchestration capabilities
- Match integration needs to connectors and APIs
- Match AI needs to the model serving capabilities

Be specific about which capability addresses the need."""


def _build_llm():
    """Build the ChatWxO LLM instance from instance credentials."""
    try:
        from ibm_watsonx_orchestrate_sdk.langchain import ChatWxO

        return ChatWxO.from_instance_credentials(
            instance_url=settings.wxo_instance_url,
            api_key=settings.wxo_api_key,
            model=settings.wxo_model,
            temperature=0.2,
            max_tokens=4000,
        )
    except Exception as exc:
        logger.error("Failed to initialize ChatWxO: %s", exc)
        raise


async def _get_mcp_tools() -> list[Any]:
    """Load tools from the wxo-docs remote MCP server."""
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        from langchain_mcp_adapters.tools import load_mcp_tools
        import subprocess

        server_params = StdioServerParameters(
            command="uvx",
            args=[
                "mcp-proxy",
                "--transport",
                "streamablehttp",
                settings.wxo_mcp_url,
            ],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await load_mcp_tools(session)
                logger.info("Loaded %d tools from wxo-docs MCP server", len(tools))
                return tools
    except Exception as exc:
        logger.warning("Could not load MCP tools (will proceed without): %s", exc)
        return []


async def analyze_transcript(raw_text: str) -> dict:
    """
    Run the full analysis pipeline on a raw transcript.

    Returns a dict with 'updates' and 'opportunities' lists.
    """
    llm = _build_llm()

    # ── Step 1: Extract updates and identify opportunities ─────────────────
    messages = [
        SystemMessage(content=EXTRACTION_SYSTEM_PROMPT),
        HumanMessage(
            content=f"Please analyze this meeting transcript:\n\n---\n{raw_text}\n---"
        ),
    ]

    response = await llm.ainvoke(messages)
    raw_content = response.content

    # Strip markdown code fences if present
    if "```json" in raw_content:
        raw_content = raw_content.split("```json")[1].split("```")[0].strip()
    elif "```" in raw_content:
        raw_content = raw_content.split("```")[1].split("```")[0].strip()

    try:
        extracted = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse agent JSON response: %s\nRaw: %s", exc, raw_content)
        extracted = {"updates": [], "opportunities": []}

    # ── Step 2: Enrich opportunities via MCP (product capability lookup) ───
    mcp_tools = await _get_mcp_tools()
    if mcp_tools:
        enriched_opportunities = []
        llm_with_tools = llm.bind_tools(mcp_tools)

        for opp in extracted.get("opportunities", []):
            try:
                enrich_messages = [
                    SystemMessage(content=SOLUTION_MATCHING_SYSTEM_PROMPT),
                    HumanMessage(
                        content=(
                            f"Look up watsonx Orchestrate capabilities for this client need:\n"
                            f"Title: {opp.get('title')}\n"
                            f"Description: {opp.get('description')}\n\n"
                            f"Use the available tools to find the best product match and "
                            f"return a JSON object with matched_product, matched_capability, "
                            f"confidence_score (0-1), and agent_reasoning."
                        )
                    ),
                ]
                enrich_response = await llm_with_tools.ainvoke(enrich_messages)
                enrich_text = enrich_response.content

                if "```json" in enrich_text:
                    enrich_text = enrich_text.split("```json")[1].split("```")[0].strip()
                elif "```" in enrich_text:
                    enrich_text = enrich_text.split("```")[1].split("```")[0].strip()

                try:
                    enrich_data = json.loads(enrich_text)
                    opp.update(enrich_data)
                except json.JSONDecodeError:
                    pass  # Keep original opportunity data
            except Exception as exc:
                logger.warning("MCP enrichment failed for opportunity '%s': %s", opp.get("title"), exc)

            enriched_opportunities.append(opp)

        extracted["opportunities"] = enriched_opportunities

    return extracted
