# Immediate-mode UI

Read for tool or debug UI built with Dear ImGui or a similar immediate-mode
library; also read the editors and tools reference. Check the library version the
project pins before relying on an API, since immediate-mode libraries change
their font, docking and input APIs between releases.

## State and identity

Immediate-mode widgets keep their state by ID. Give each repeated item a unique
ID derived from stable data, such as an object identifier rather than a list
index or label. Use the library's ID stack (for example `PushID` or a `##` label
suffix) so duplicate labels keep independent state.

Keep document state in the application model, and treat the UI pass as a view of
it that emits edits. Commit undoable changes when the user finishes an edit (for
example on `IsItemDeactivatedAfterEdit`), so a drag or text entry becomes one
undo step. Apply live preview separately from the committed edit where the tool
needs both.

## Layout and appearance

Use tables, child regions and docking rather than absolute positions, and keep
window and dock state in the library's settings file or the project's own layout
storage. Define the style once in a theme function: spacing, rounding and color
roles for selection, hover, active, disabled, warning and error. Scattered
per-widget style pushes drift and leak when a pop is missed.

Scale fonts and style metrics with display DPI through the mechanism the pinned
version supports, and test at 100% and 200%. Rendering a small font atlas and
scaling it up produces blurry text.

## Input and cost

Enable keyboard navigation, keep focus visible and give icon-only buttons
tooltips that include their shortcut. Read the library's capture flags (for
example `WantCaptureKeyboard` and `WantCaptureMouse`) each frame so the host
withholds game or viewport input while the UI owns it, and so clicks reach the UI
without waiting for keyboard focus.

The whole interface is rebuilt every frame. Clip long lists with the library's
clipper, avoid formatting and allocation in hot loops, and profile tool panels
when they affect the frame time of the application they run inside.

## Verify the affected flow

Run the tool in its host application at the supported DPI settings. Check ID
collisions with duplicated objects, undo granularity for drags and text entry,
keyboard navigation, input capture between UI and viewport, and frame-time cost
with large data.
