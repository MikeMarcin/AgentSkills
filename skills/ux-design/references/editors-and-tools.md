# Editors and tools

Read for editors, inspectors and developer tools: engine and level editors, asset
and data tools, code and review tools, profilers, debuggers and internal
operations consoles. Also read the reference for the UI toolkit: [Qt](qt.md) or
[Desktop](desktop.md) for native shells, [Web](web.md) for browser tools,
[Immediate-mode UI](immediate-mode.md) for Dear ImGui and similar libraries, and
[Roblox Studio plugins](roblox-studio-plugins.md) for Studio.

## Workspace

People use these tools for long sessions of repeated, expert work. Optimize the
repeated operation and support dense information, while keeping every command
discoverable through menus or a command palette that shows its shortcut. Visual
character comes from precise hierarchy and alignment, with color reserved for
state: selection, the active object, modified, warning, error and running.

Center the layout on the work surface (viewport, canvas, document, graph or
diff) and surround it with panels such as a hierarchy, inspector, asset browser
and log. Panels resize, collapse and dock; the layout persists per user and a
command restores the default. Showing or hiding one panel leaves the others where
they were.

Distinguish modes from documents. Editing in place in the world or scene is a
mode; something with its own canvas is a document. Change modes only through the
mode control, never as a side effect of dock visibility, tab selection or focus.
Make modes visible: play versus edit, the active tool, recording and read-only
state. Edits that will be discarded, such as changes made during play, must look
different.

Selection drives the tool. Show one selection and its active object consistently
in the work surface, hierarchy and inspector. The inspector edits the selection;
with several objects selected it edits shared properties and shows mixed values
explicitly, leaving them untouched until the user changes them.

Route input by what has captured it. While the viewport captures the pointer for
navigation, editor shortcuts stay quiet; pointer events go to what is under the
pointer without waiting for keyboard focus. Scope remaining shortcuts to the
focused panel, avoid shortcuts the host already owns and allow rebinding where the
host does.

Previous and next controls for changes, results or problems stay enabled and stop
at each end, without wrapping or crossing into the next file. A log or transcript
follows new output only while the user is already at its end; items awaiting a
response sit beside the input that answers them.

## Editing and data safety

Give every document change an undo step that matches the user's intent: one drag,
slider scrub or multi-field commit becomes one step, not one per frame. Unsaved
means the content differs from the last save, so undoing back to the saved state
clears the marker. Closing an unsaved document offers save, discard and cancel;
discard restores the saved bytes exactly. Preserve unsaved work across a crash.
Offer snapping with visible state and a modifier to bypass it, numeric entry for
precision and units on values.

Report validation problems at the field and on the affected object in the
hierarchy, with log entries that link back to their source. Warn and proceed for
recoverable content problems rather than blocking the workflow. Run builds,
bakes, imports, searches and other long operations off the interface thread. Show
their stage and progress, allow cancellation and summarize results with links to
each failure.

When an edit-to-run loop exists, run exactly what is on screen, unsaved edits
included, without a manual export or cook step. Surface the runtime's own failure
reason when a run does not start.

When agents edit alongside people, route both through the same edit and undo
service and keep full manual control. Agent proposals preserve locks and newer
human edits, and an agent's confidence does not replace visual acceptance.

Virtualize long lists and trees. Filter incrementally, keep sorting stable and
preserve selection and scroll position across refreshes. Live or polled data
should show when it last updated and whether a refresh is in progress.

## Viewports and code views

Draw manipulation handles at a fixed on-screen size, scaled by device pixel ratio,
above scene geometry and with an outline that holds over any background. Let
shape signal the affordance and show labels on hover or drag. Move handles with
the live preview and commit on the pointer event rather than a timer. Hit-test
against the frame that was drawn; while a new view is pending, keep the last image
and pause picking with a visible reason.

Match the editor preview to the shipped look, including tone mapping and lighting.
Design the empty and opening states: frame the content on open, and show an
intentional empty view rather than a renderer placeholder.

In code and diff views, draw selection solidly above change fills while each
glyph keeps its syntax color, adjusted to meet the contrast floor.

## Verify the affected flow

Run the tool build against representative data large enough to expose scale
problems: thousands of objects, long names and paths, deep hierarchies and large
files. Exercise the primary edit loop from the keyboard and pointer: select, edit,
undo back to saved, redo, save, close and reopen. Check multi-selection with mixed
values, mode transitions, the edit-to-run loop, a cancelled long operation, an
error with recovery, panel docking and reset, and display scaling. Report the
builds and data sets used.
