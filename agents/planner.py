"""
Defines the Planner Agent.
"""
from google.adk.agents import LlmAgent
from services.physics_tools import OPTIMIZE_MANEUVER_TOOL

# 3. Planner Agent (Optimization Loop)
planner_agent = LlmAgent(
    name="planner_agent",
    description="Calculates optimal maneuvers for high-risk conjunctions.",
    instruction="""
    You are the Maneuver Planner. Your core task is to run an optimization loop to find the minimum delta_v (thrust)
    required to avoid a collision while conserving fuel.
    1. Receive the miss distance from the Triage Agent.
    2. Use the `optimize_maneuver` tool to get the optimal delta-v.
    3. Output the required delta_v in km/s and the estimated new orbital parameters (perigee).
    """,
    tools=[OPTIMIZE_MANEUVER_TOOL]
)