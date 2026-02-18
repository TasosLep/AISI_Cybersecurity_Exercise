from __future__ import annotations

from pathlib import Path

from inspect_ai import Task, eval, task
from inspect_ai.scorer import includes
from inspect_ai.tool import bash_session, bash

from inspect_cyber import create_agentic_eval_dataset
from inspect_cyber.solvers import play_message_history
from inspect_cyber.model._sources import PythonFunctionSource


def _hydrate_message_history(sample):
    """
    Convert eval.yaml metadata.message_history (a dict) into PythonFunctionSource,
    which play_message_history expects.
    """
    mh = sample.metadata.get("message_history")
    if isinstance(mh, dict) and mh.get("type") == "python":
        sample.metadata["message_history"] = PythonFunctionSource(
            module=mh["module"], # python module path to import
            function=mh["function"], # function name inside that module
            args=mh.get("args") or {}, # optional keyword arguments for that function
        )
    return sample


@task
def message_history_solution():
    """
    This defines an Inspect task factory.

    When Inspect runs this, it will:
      - build the dataset
      - create tools
      - return a Task(dataset=..., solver=..., scorer=...)
    """

    # Load the agentic eval dataset (Doomla), rooted at evals/doomla
    dataset = create_agentic_eval_dataset(root_dir=Path("evals/doomla").resolve())

    # Restrict to only the "message_history" variant of the dataset
    dataset = dataset.filter_by_metadata({"variant_name": "message_history"})

    # Convert YAML/dict message_history entries into PythonFunctionSource callables
    dataset = [_hydrate_message_history(s) for s in dataset]

    # IMPORTANT: bash_session is the ONLY tool our message history calls.
    # bash_session: stateful shell (persists across calls)
    # wait_for_output: how long bash_session will wait for output before returning.
    # timeout: maximum runtime for a single tool invocation.
    # bash: one-shot/stateless shell tool (each call independent)
    tools = [
        bash_session(
            instance="BashSession",
            wait_for_output=900, # keep session from returning "" too early on long/quiet cmds
            timeout=930 # hard cap per tool call
        ),
        bash(
            timeout=930 # hard cap per tool call
        )
    ]

    # Build and return the task:
    # - solver: replays the provided message history + executes tool calls
    # - scorer: includes() checks the final answer contains the expected substring(s)
    return Task(
        dataset=dataset,
        solver=play_message_history(tools=tools),
        scorer=includes(),
    )


# model=None means "don't call an LLM"; you’re just replaying messages/tools.
# sandbox_cleanup=False keeps the sandbox around after for debugging.
if __name__ == "__main__":
    eval(
        message_history_solution,
        model=None, 
        sandbox_cleanup=False,
    )
