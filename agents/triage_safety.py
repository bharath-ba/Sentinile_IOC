"""
Defines the Triage and Safety Agents.
"""
from google.adk.agents import LlmAgent
from services.physics_tools import PC_CALCULATION_TOOL, VALIDATE_SAFETY_TOOL

# 1. Triage Agent (Risk Assessment)
triage_agent = LlmAgent(
    name="triage_agent",
    description="Analyzes collision risk and assigns a consensus probability (Pc).",
    instruction="""
    You are the Triage Agent. Your goal is to assess the risk of a Conjunction Data Message (CDM).
    1. Use the `calculate_collision_probability` tool with the provided miss distance and covariance eigenvalue.
    2. If the calculated Pc is greater than 1e-4, report the 'HIGH RISK' level.
    3. If the Pc is 1e-4 or less, report 'LOW RISK'.
    4. Always output the calculated Pc.
    """,
    tools=[PC_CALCULATION_TOOL]
)

# 2. Safety Agent (Plan Validation)
safety_agent = LlmAgent(
    name="safety_agent",
    description="Validates maneuver plans against fuel and orbital safety constraints.",
    instruction="""
    You are the Safety Validator. You ensure any planned maneuver does not compromise the satellite's health.
    1. Receive the planned delta_v and estimated post-maneuver perigee (km).
    2. Use `validate_safety_constraints` to check against limits.
    3. If the tool reports 'approved_for_execution', output EXECUTE. If not, output REJECT.
    """,
    tools=[VALIDATE_SAFETY_TOOL]
)