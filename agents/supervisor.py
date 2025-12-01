"""
Defines the Supervisor Agent, which orchestrates the sequential workflow.
"""
from google.adk.agents import LlmAgent

# 4. Supervisor Agent (Sequential Orchestration)
supervisor_agent = LlmAgent(
    name="supervisor_agent",
    description="Root agent that manages the sequential collision avoidance workflow.",
    instruction="""
    You are the IOC Supervisor. Your role is sequential orchestration and overall decision-making.
    
    Workflow:
    1. Receive the initial Conjunction Data Message (CDM).
    2. Start by asking @triage_agent to assess the risk using the CDM parameters.
    3. IF @triage_agent reports 'HIGH RISK':
        a. IMMEDIATELY ask @planner_agent to calculate an optimal avoidance maneuver.
        b. Pass the resulting maneuver plan (delta-v and perigee) to @safety_agent for final validation.
    4. IF @triage_agent reports 'LOW RISK':
        a. Output the decision: 'MONITOR - LOW RISK'. No further action is needed.
    5. Report the final action based on the Safety Agent's output (EXECUTE, REJECT, or MONITOR).
    """
    # Note: No tools are defined here. The Supervisor's "tool" is routing requests to other agents (@mentions).
)