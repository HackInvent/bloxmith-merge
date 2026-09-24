# Merge Block

<!-- block-metadata:start -->
[![Block version: 0.1.0](https://img.shields.io/badge/block-0.1.0-blue)](model.json)
[![BloxSmith compatibility: 1.0.9](https://img.shields.io/badge/BloxSmith-1.0.9-brightgreen)](compatibility.json)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)

Verified BloxSmith versions: **1.0.9** (bundled-block tests; see [test evidence](compatibility.json)).
<!-- block-metadata:end -->


## Role

`merge` concatenates multiple input values into one text output.

## Files

- `block.py`: input aggregation and inspector rendering.
- `model.json`: two default inputs, one output, and separator config.
- `inspector_panel.html`, `assets/`: inspector UI.
- `assets/js/block_modal.js`: modal-owned mount hook used by the framework to keep the modal stable during polling.
- `node_card.html`: block-owned canvas card body.

## Ports

- Inputs:
  - `input_1` (`id: 1`): optional `message/*`.
  - `input_2` (`id: 2`): optional `message/*`.
- Outputs:
  - `out` (`id: 1`): emits `message/*`.

## Configuration

- `separator`: string inserted between non-empty input values. Default is a blank line.

## Runtime Behavior

`execute_runtime()` collects current input values, removes empty values, joins them with the configured separator, and emits the merged text on every output.

## UI Behavior

The inspector summarizes merge behavior and uses block-owned CSS.

## Editor Display

The canvas card is rendered by this block through `node_card.html`. It exposes the merge input/output summary while the shared editor shell keeps ports, dragging, status, and graph links generic.

## Modal

`block_modal.html` is owned by this block and rendered by the generic modal contract. It shows block state and lets users edit supported title/config fields through generic bindings.
The modal declares `data-block-runtime-refresh="autonomous"`; it is a lightweight block-owned surface so runtime polling does not replace the open modal or overwrite draft generic fields before **Apply**.

## Maintenance Notes

If dynamic port counts are added later, keep aggregation generic over `context.inputs` rather than hard-coding two input names.

## Compatibility policy

[compatibility.json](compatibility.json) records HackInvent's verified BloxSmith versions and test evidence. Only the versions listed above have been verified, using the block-owned suites in a **bundled-block test installation**. This is not a certification of managed-package installation, every browser/OS, or live provider availability. Other framework versions are unverified, not necessarily incompatible.

The block-version badge follows `model.json`, not a published Git tag. `unversioned` means that no block release version is declared; no number is inferred from the framework version. The framework still uses `model.json` for its runtime/install contract; the tester-owned JSON does not replace it. Official integration tests run in the private `bloxmith-blocs` workspace. Test helpers and the proprietary framework are not bundled in this public block repository.

## Properties ergonomics

Modal and inspector styles are owned by this package and scoped to its exact
release. Forms adapt to narrow panels, checkboxes stay beside their labels, and
long values do not widen the inspector. Existing labels are associated with
controls; keyboard navigation complements the block’s own tab handlers.
These presentation helpers do not change port bindings, authored settings,
runtime behavior or the block’s original surface cleanup.
