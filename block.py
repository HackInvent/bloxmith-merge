# -----------------------------------------------------------------------------
# Role: Implements the merge block runtime and UI contract.
# File Name: block.py
# Author: Alexandre EL
# Email: alex@hackinvent.com
# Created Date: 2024-05-11
# -----------------------------------------------------------------------------

from __future__ import annotations

from html import escape
from typing import Any

from bloxsmith_app.block_api import (
    BlockDefinition,
    BlockRuntimeContext,
    BlockRuntimeOutput,
    BlockRuntimeResult,
    render_inspector_template,
    render_node_card_template,
    TEXT_PLAIN,
)


# Functional behavior:
# FB1 - Aggregate non-empty incoming values in input-port order.
# FB2 - Use the configured separator when joining values.
# FB3 - Emit the same merged text on every output port.
# FB4 - Return skipped status and an empty output when all inputs are empty.
class MergeBlock(BlockDefinition):
    """Autonomous block implementation for `MergeBlock`."""
    kind = "merge"

    def render_node_card(self, *, node: dict[str, Any], payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Render the Merge canvas card body from the block-owned template."""

        input_count = len(node.get("inputs") or [])
        return render_node_card_template(
            block=self,
            node=node,
            node_classes=["merge-node"],
            replacements={
                "title": node.get("title") or self.default_title(),
                "preview": f"{input_count} input{'s' if input_count > 1 else ''} -> 1 output",
                # The card text is countable: the count travels next to the marker so the
                # browser picks the plural form of the active language on its own.
                "preview_count": input_count,
                "mode": "aggregate",
            },
        )

    def render_inspector_panel(self, *, node: dict[str, Any], payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Render the block-owned inspector panel HTML for the selected node.

        Args:
            node: Serialized graph node handled by the block.
            payload: Optional UI or runtime payload provided by the framework.
        """
        inputs = node.get("inputs") if isinstance(node.get("inputs"), list) else []
        template = (self.directory / "inspector_panel.html").read_text(encoding="utf-8")
        html = render_inspector_template(
            template=(
                template
                .replace("{{ source }}", escape(f"{len(inputs)} input(s)"))
                .replace("{{ description }}", escape("Joins the non-empty inputs, in port order, with two line breaks."))
            ),
            node={**node, "type": self.kind, "kind": self.kind},
            payload=payload,
        )
        return {"html": html, "context": {"node_id": str(node.get("id") or ""), "input_count": len(inputs), "full_panel": True}}

    def aggregate(self, inputs: list[Any], *, separator: str = "\n\n") -> str:
        """Aggregate input values according to this block configuration.

        Args:
            inputs: Input values received by the block.
            separator: Separator value used by this block helper.
        """
        parts = []
        for value in inputs:
            text = "" if value is None else str(value).strip()
            if text:
                parts.append(text)
        return separator.join(parts)

    def execute_runtime(self, context: BlockRuntimeContext) -> BlockRuntimeResult:
        """Execute the block through the generic runtime context and return runtime outputs.

        Args:
            context: Generic runtime context injected by the execution engine.
        """
        ordered_inputs = sorted(context.input_ports, key=lambda port: int(getattr(port, "id", 0) or 0))
        input_parts = [
            str(context.input_value(str(getattr(port, "id", ""))) or "").strip()
            for port in ordered_inputs
        ]
        input_parts = [value for value in input_parts if value]
        separator = str(context.config.get("separator") or "\n\n")
        merged_value = self.aggregate(input_parts, separator=separator)
        outputs = [
            BlockRuntimeOutput(
                port_id=int(getattr(port, "id", 0) or 0),
                port_name=str(getattr(port, "name", "") or ""),
                value=merged_value,
                content_type=TEXT_PLAIN,
            )
            for port in context.output_ports
        ]
        return BlockRuntimeResult(
            status="success" if merged_value else "skipped",
            outputs=outputs,
            logs=[f"[merge] {context.node_id}: {len(input_parts)} non-empty input(s) merged."],
            last_message=merged_value,
            content_type=TEXT_PLAIN,
            worker_received=merged_value or "-",
            metadata={"aggregated_inputs": len(input_parts)},
        )
