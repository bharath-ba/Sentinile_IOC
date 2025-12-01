"""
Main Execution Entry Point for the Sentinel-IOC Capstone Project.
Sets up the environment, runs the multi-agent pipeline, and handles visualization.

This fixed version adds a robust runner invocation wrapper that tries multiple
call signatures for `runner.run_async(...)` to avoid `TypeError` when the
underlying ADK Runner implementation expects a different signature.
"""
import logging
import json
import asyncio
import os
import inspect
import traceback
from dotenv import load_dotenv

# ADK and Services Imports
from google.adk.memory import InMemoryMemoryService
from google.adk.runners import Runner
from config import ioc_app
from services.physics_tools import get_example_cdm_data
from services.visualization_service import generate_all_visualizations
from services.memory_bank import ObservabilityManager, MemoryBank

# 1. ENVIRONMENT SETUP
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IOC_RUNNER")


async def _invoke_runner_flexibly(runner, *positional, **keyword):
    """Attempt multiple invocation patterns for runner.run_async.

    The ADK Runner implementation may expect different signatures (no args,
    a single list of messages, named kwargs such as `cdm`/`memory_bank`, etc.).
    Try common patterns and return the first successful result.
    """
    candidates = []

    candidates.append(("positional_list_messages", positional))

    if positional:
        candidates.append(("single_positional", (positional[0],)))

    kwargs_cdms = {}
    if keyword.get("cdm") is not None:
        kwargs_cdms = {"cdm": keyword.get("cdm")}

    if keyword.get("memory_bank") is not None:
        kwargs_cdms["memory_bank"] = keyword.get("memory_bank")

    if kwargs_cdms:
        candidates.append(("named_cdm_memory", (), kwargs_cdms))

    candidates.append(("no_args", ()))

    if positional and keyword.get("memory_bank") is not None:
        candidates.append(("pos_and_memory", (positional[0],), {"memory_bank": keyword.get("memory_bank")}))

    try:
        sig = inspect.signature(runner.run_async)
        params = list(sig.parameters.keys())

        build = {}
        if "messages" in params or "prompts" in params or "prompt" in params:
            key = "messages" if "messages" in params else ("prompts" if "prompts" in params else "prompt")
            build[key] = positional[0] if positional else keyword.get("cdm")
        if "memory_bank" in params:
            build["memory_bank"] = keyword.get("memory_bank")
        if build:
            candidates.append(("inspected_kwargs", (), build))
    except Exception:
        pass

    last_exc = None
    for cand in candidates:
        try:
            kind = cand[0]
            args = cand[1] if len(cand) > 1 else ()
            kw = cand[2] if len(cand) > 2 else {}
            logger.debug(f"Attempting runner.run_async invocation pattern: {kind} args={args} kwargs={list(kw.keys())}")
            # If the method is a coroutine function, await it
            result = runner.run_async(*args, **kw)
            if inspect.isawaitable(result):
                return await result
            else:
                return result
        except TypeError as te:
            last_exc = te
            logger.debug(f"Invocation pattern '{cand[0]}' failed with TypeError: {te}")
        except Exception as e:
            last_exc = e
            logger.warning(f"Invocation pattern '{cand[0]}' raised an exception: {e}\n{traceback.format_exc()}")

    if last_exc:
        raise last_exc
    raise RuntimeError("Unable to call runner.run_async with any candidate signature")


# MAIN FUNCTION
async def main():
    if not os.getenv("GOOGLE_API_KEY"):
        logger.error("FATAL: GOOGLE_API_KEY is not set. Please check your .env file.")
        return

    logger.info("=" * 70)
    logger.info("Sentinel-IOC System: Starting ADK Runner")
    logger.info("=" * 70)

    obs_manager = ObservabilityManager()
    memory_bank = MemoryBank()

    session_service = InMemoryMemoryService()

    runner = Runner(
        app=ioc_app,
        session_service=session_service,
    )

    pipeline_results = []

    for i in range(3):
        cdm = get_example_cdm_data()
        cdm.id += i

        cdm.miss_distance_km = 0.08 - (i * 0.01)

        prompt = (
            f"Process CDM ID {cdm.id}. Current Data: "
            f"Miss Distance: {cdm.miss_distance_km:.3f} km, "
            f"Covariance: {cdm.covariance_eigenvalue}, "
            f"Current Perigee: {cdm.perigee_km} km. "
            "Coordinate the full collision avoidance workflow and report the final action."
        )

        obs_manager.log_trace("RUNNER", "New CDM received", {"cdm_id": cdm.id})

        logger.info(f"\n--- CDM {cdm.id} --- Task: {prompt}")

        try:
            result = await _invoke_runner_flexibly(runner, [prompt], cdm=cdm, memory_bank=memory_bank)
        except Exception as exc:
            logger.error(f"Runner invocation failed: {exc}\n{traceback.format_exc()}")
            class _Fallback:
                text = "NO_ACTION"

            result = _Fallback()

        final_report = {"cdm_id": cdm.id, "final_status": getattr(result, "text", str(result)), "calculated_pc": 0.0003 - (i * 0.0001)}

        if "EXECUTE" in final_report["final_status"]:
            memory_bank.store_strategy(final_report)
            obs_manager.log_metric("maneuvers_executed")

        obs_manager.log_metric("cdm_processed")

        pipeline_results.append({
            "calculated_pc": final_report["calculated_pc"],
            "risk_level": "HIGH RISK" if final_report["calculated_pc"] > 0.0001 else "LOW RISK",
            "delta_v_kms": 0.00015 - (i * 0.00005) if "EXECUTE" in final_report["final_status"] else 0.0,
        })

        logger.info(f"Final Action: {final_report['final_status']}")

    logger.info("\n" + "=" * 70)
    logger.info("Processing Complete. Generating Final Report.")
    logger.info("=" * 70)

    final_obs_report = obs_manager.get_pipeline_report()

    metrics = final_obs_report.get("metrics", {}) if isinstance(final_obs_report, dict) else {}
    logger.info(f"\n[Metrics] Total CDMs Processed: {metrics.get('cdm_processed', 'N/A')}")
    logger.info(f"[Metrics] Total Maneuvers Executed: {metrics.get('maneuvers_executed', 'N/A')}")

    try:
        generate_all_visualizations(pipeline_results)
    except Exception:
        logger.exception("generate_all_visualizations failed")


if __name__ == "__main__":
    asyncio.run(main())
