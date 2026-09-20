#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Role: Verifies merge concat inputs behavior for the merge block.
# File Name: F5.03_merge_concat_inputs.py
# Author: Alexandre EL
# Email: alex@hackinvent.com
# Created Date: 2024-06-17
# -----------------------------------------------------------------------------

"""F5.03 - Merge of two inputs.

The test sends two text sources into a `merge` block, then checks that the
output joins both inputs with the configured separator.
"""

# Test cases:
# - FB1/FB2 - Run two text sources into Merge and verify non-empty inputs are concatenated in port order with the configured separator.
# - FB3 - Verify the merged output is delivered to a downstream display.
# - FB4 - Execute Merge directly with empty inputs and verify it returns skipped with an empty output.
# - Runtime modes - Verify the same ordered merge in centralized and zeromq_active.

from pathlib import Path
from types import SimpleNamespace

from ui_smoke_common import (
    create_run_api,
    data_edge,
    display_node,
    expect,
    graph_payload,
    isolated_server,
    text_node,
    wait_for_run_terminal,
)

from blocs.merge.block import MergeBlock
from bloxsmith_app.block_runtime import BlockRuntimeContext


def merge_node() -> dict:
    return {
        "id": "merge-1",
        "kind": "merge",
        "title": "Merge test",
        "position": {"x": 360, "y": 160},
        "inputs": [
            {"id": 1, "name": "input_1", "title": "In 1", "accepts": ["message/*"], "multiplicity": "many"},
            {"id": 2, "name": "input_2", "title": "In 2", "accepts": ["message/*"], "multiplicity": "many"},
        ],
        "outputs": [
            {"id": 1, "name": "out", "title": "Out", "emits": ["message/*"], "multiplicity": "many"}
        ],
        "config": {"separator": "\n\n"},
    }


def _verify_empty_merge_skips() -> None:
    result = MergeBlock().execute_runtime(
        BlockRuntimeContext(
            run_id="unit-run",
            node_id="merge-empty",
            kind="merge",
            title="Merge empty",
            config={"separator": "\n\n"},
            inputs={},
            input_content_types={},
            input_message="",
            input_ports=(SimpleNamespace(id=1, name="input_1"), SimpleNamespace(id=2, name="input_2")),
            output_ports=(SimpleNamespace(id=1, name="out"),),
            root_dir=Path.cwd(),
        )
    )
    expect(result.status == "skipped", "Merge with no non-empty input must return skipped.")
    expect(result.outputs and result.outputs[0].value == "", "A skipped merge must keep a compatible empty output.")


def _verify_runtime_mode(runtime_mode: str) -> None:
    """Run an ordered two-input merge through one selected execution engine."""

    with isolated_server() as server:
        document = graph_payload(
            f"F5 Merge {runtime_mode}",
            [
                text_node("text-a", "Texte A", "alpha", 80, 100),
                text_node("text-b", "Texte B", "beta", 80, 260),
                merge_node(),
                display_node("display-1", "Affichage", 680, 160),
            ],
            [
                data_edge("edge-a-merge", "text-a", 1, "merge-1", 1),
                data_edge("edge-b-merge", "text-b", 1, "merge-1", 2),
                data_edge("edge-merge-display", "merge-1", 1, "display-1", 1),
            ],
        )
        created = create_run_api(server, document, runtime_mode=runtime_mode)
        run = wait_for_run_terminal(server, str(created.get("run_id") or ""), timeout_sec=20)
        expect(run.get("status") == "success", f"The merge {runtime_mode} run must succeed.")
        expect(run.get("runtime_mode") == runtime_mode, f"The merge run must stay in {runtime_mode}.")
        expected = "alpha\n\nbeta"
        expect(
            run.get("output_values", {}).get("merge-1:1", {}).get("value") == expected,
            f"La concaténation merge est incorrecte en {runtime_mode}.",
        )
        expect(
            run.get("results", {}).get("merge-1", {}).get("aggregated_inputs") == 2,
            f"Merge doit agréger deux inputs en {runtime_mode}.",
        )
        if runtime_mode == "zeromq_active":
            expect(
                run.get("results", {}).get("merge-1", {}).get("transport") == "zeromq_active",
                "Merge actif ne doit pas utiliser le moteur centralisé.",
            )


def main() -> None:
    _verify_empty_merge_skips()
    for runtime_mode in ("centralized", "zeromq_active"):
        _verify_runtime_mode(runtime_mode)
    print("[ok] F5.03_merge_concat_inputs")


if __name__ == "__main__":
    main()
