#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Role: Verifies structure block inspector panel API behavior for the merge block.
# File Name: F8.13_structure_block_inspector_panel_api.py
# Author: Alexandre EL
# Email: alex@hackinvent.com
# Created Date: 2024-07-24
# -----------------------------------------------------------------------------

"""F8.13 - UI modulaire des panneaux inspecteur Merge et Event OR.

Le test démarre un serveur isolé, demande le rendu des panneaux inspecteur
`merge` et `event_or` depuis leurs `block.py`, puis vérifie que leur CSS est
exposé. Aucune donnée utilisateur n'est modifiée hors du serveur de test.
"""

# Test cases:
# - Merge UI - Render structural block inspector panels for Merge and EventOr through the block API.
# - Merge UI - Verify the panels expose input/output summaries without mutating node configuration.
# - Merge UI - Verify their modals are autonomous and declare block-owned JS.

from __future__ import annotations

from urllib.request import urlopen

from ui_smoke_common import expect, http_json, isolated_server


def assert_structure_panel(server, kind: str, expected_text: str) -> None:
    node = {
        "id": f"{kind}-1",
        "kind": kind,
        "type": kind,
        "title": kind,
        "inputs": [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}],
    }
    rendered = http_json(server.base_url, f"/api/blocks/{kind}/inspector-panel", method="POST", payload={"node": node})
    html = str(rendered.get("html") or "")
    expect("data-structure-inspector-root" in html, f"Le HTML inspecteur {kind} doit venir du bloc.")
    expect("2 input(s)" in html, f"Le panneau {kind} doit afficher le nombre d'inputs.")
    expect(expected_text in html, f"Le panneau {kind} doit afficher le comportement attendu.")
    assets = rendered.get("assets") or []
    expect({"kind": "css", "path": "assets/css/inspector_panel.css"} in assets, f"CSS {kind} manquant.")
    with urlopen(f"{server.base_url}/api/blocks/{kind}/assets/assets/css/inspector_panel.css", timeout=5) as response:
        body = response.read().decode("utf-8")
    expect("structure" in body.lower(), f"Asset CSS inspecteur {kind} non servi.")

    modal = http_json(server.base_url, f"/api/blocks/{kind}/modal", method="POST", payload={"node": node})
    modal_html = str(modal.get("html") or "")
    modal_assets = modal.get("assets") or []
    expect('data-block-runtime-refresh="autonomous"' in modal_html, f"Le modal {kind} doit gerer son refresh runtime.")
    expect({"kind": "js", "path": "assets/js/block_modal.js"} in modal_assets, f"JS modal {kind} manquant.")
    with urlopen(f"{server.base_url}/api/blocks/{kind}/assets/assets/js/block_modal.js", timeout=5) as response:
        modal_js = response.read().decode("utf-8")
    expect(f"registry.{kind}" in modal_js, f"Asset JS modal {kind} non servi.")


def main() -> None:
    with isolated_server() as server:
        assert_structure_panel(server, "merge", "Agrège les inputs")
        assert_structure_panel(server, "event_or", "Relaie uniquement")
    print("[ok] F8.13_structure_block_inspector_panel_api")


if __name__ == "__main__":
    main()
