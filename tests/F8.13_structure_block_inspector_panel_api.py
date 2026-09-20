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
    expect("data-structure-inspector-root" in html, f"Le HTML inspecteur {kind} doit venir du bloc.")
    expect("2 input(s)" in html, f"Le panneau {kind} doit afficher le nombre d'inputs.")
    expect(expected_text in html, f"Le panneau {kind} doit afficher le comportement attendu.")
    css_path = next(asset["path"] for asset in rendered["assets"] if asset["kind"] == "css")
    with urlopen(f"{server.base_url}/api/blocks/{key}/assets/{css_path}", timeout=5) as response:
        body = response.read().decode("utf-8")
    expect("structure" in body.lower(), f"Asset CSS inspecteur {kind} non servi.")
    expect(f'[data-block-release="{release_key(model)}"]' in body,
           f"Le CSS {kind} doit être scopé à sa release.")

    modal = surface_payload(server, model, node, "modal")
    modal_html = str(modal.get("html") or "")
    expect('data-block-runtime-refresh="autonomous"' in modal_html, f"Le modal {kind} doit gerer son refresh runtime.")
    js_path = next(asset["path"] for asset in modal["assets"] if asset["kind"] == "js")
    with urlopen(f"{server.base_url}/api/blocks/{key}/assets/{js_path}", timeout=5) as response:
        modal_js = response.read().decode("utf-8")
    expect("export function mount" in modal_js, f"Le module modal {kind} doit exporter mount.")
    expect("CWBlockUiBlocks" not in modal_js, f"Le module modal {kind} ne doit plus utiliser le registre global.")


def main() -> None:
    with isolated_server() as server:
        assert_structure_panel(server, "merge", "Agrège les inputs")
        assert_structure_panel(server, "event_or", "Relaie uniquement")
    print("[ok] F8.13_structure_block_inspector_panel_api")


if __name__ == "__main__":
    main()
