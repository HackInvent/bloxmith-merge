#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Role: Verifies structure block inspector panel API behavior for the merge block.
# File Name: F8.13_structure_block_inspector_panel_api.py
# Author: Alexandre EL
# Email: alex@hackinvent.com
# Created Date: 2024-07-24
# -----------------------------------------------------------------------------

"""F8.13 - Modular UI of the Merge and Event OR inspector panels.

The test starts an isolated server, renders the `merge` and `event_or` inspector
panels from their own `block.py`, then checks that their CSS is exposed. No user
data is modified outside the test server.
"""

# Test cases:
# - Merge UI - Render structural block inspector panels for Merge and EventOr through the block API.
# - Merge UI - Verify the panels expose input/output summaries without mutating node configuration.
# - Merge UI - Verify their modals are autonomous and declare block-owned JS.

from __future__ import annotations

from urllib.parse import quote
from urllib.request import urlopen

from ui_smoke_common import expect, http_json, isolated_server
from block_test_packages import install_test_package, release_key, surface_payload


def assert_structure_panel(server, kind: str, expected_text: str) -> None:
    """Check one structure block's own surfaces through the installed release contract."""
    # Surfaces are release assets: the host serves what model.json declares, and the
    # editor imports them as ES modules. A bundled kind would serve nothing.
    model = install_test_package(server, kind)
    key = quote(release_key(model), safe="")
    node = {
        "id": f"{kind}-1",
        "kind": kind,
        "type": kind,
        "title": kind,
        "block_version": model["version"],
        "inputs": [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}],
    }
    rendered = surface_payload(server, model, node, "inspector_panel")
    html = str(rendered.get("html") or "")
    expect("data-structure-inspector-root" in html, f"The {kind} inspector HTML must come from the block.")
    expect("2 input(s)" in html, f"The {kind} panel must show the input count.")
    expect(expected_text in html, f"The {kind} panel must show the expected behavior.")
    css_path = next(asset["path"] for asset in rendered["assets"] if asset["kind"] == "css")
    with urlopen(f"{server.base_url}/api/blocks/{key}/assets/{css_path}", timeout=5) as response:
        body = response.read().decode("utf-8")
    expect("structure" in body.lower(), f"{kind} inspector CSS asset not served.")
    expect(f'[data-block-release="{release_key(model)}"]' in body,
           f"The {kind} CSS must be scoped to its release.")

    modal = surface_payload(server, model, node, "modal")
    modal_html = str(modal.get("html") or "")
    expect('data-block-runtime-refresh="autonomous"' in modal_html, f"The {kind} modal must own its runtime refresh.")
    js_path = next(asset["path"] for asset in modal["assets"] if asset["kind"] == "js")
    with urlopen(f"{server.base_url}/api/blocks/{key}/assets/{js_path}", timeout=5) as response:
        modal_js = response.read().decode("utf-8")
    expect("export function mount" in modal_js, f"The {kind} modal module must export mount.")
    expect("CWBlockUiBlocks" not in modal_js, f"The {kind} modal module must no longer use the global registry.")


def main() -> None:
    with isolated_server() as server:
        assert_structure_panel(server, "merge", "Joins the non-empty inputs")
        assert_structure_panel(server, "event_or", "Relays only")
    print("[ok] F8.13_structure_block_inspector_panel_api")


if __name__ == "__main__":
    main()
