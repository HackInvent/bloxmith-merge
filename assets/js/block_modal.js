import { withProperties } from "./properties.js";

/**
 * Role: Mounts the Merge block modal frontend.
 * File Name: block_modal.js
 * Author: Alexandre EL
 * Email: alex@hackinvent.com
 * Created Date: 2026-06-10
 */

/**
 * Mark the Merge modal as block-owned while generic fields, ports,
 * runtime state, and Apply stay handled by the framework modal API.
 *
 * @param {HTMLElement} root - Mounted Merge modal root.
 */
function mountOwned(root) {
  if (root instanceof HTMLElement) {
    root.dataset.mergeModalMounted = "true";
  }
}

/** Keep the block behavior and add properties-only accessibility. */
export function mount(root, ...args) {
  return withProperties(mountOwned).call(this, root, ...args);
}
