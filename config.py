"""
Application Configuration File.
Defines the ADK App and registers the root agent.
"""
from google.adk.apps import App
from agents.supervisor import supervisor_agent
from agents.triage_safety import triage_agent, safety_agent
from agents.planner import planner_agent

# Gather all agents from the modules
ALL_AGENTS = [
    supervisor_agent,
    triage_agent,
    planner_agent,
    safety_agent,
]

ioc_app = App(
    name="sentinel_ioc_system", 
    root_agent=supervisor_agent,
)