# Desktop applications

Read for native or cross-platform desktop applications. For web content inside
a desktop shell, also read the web reference; the shell still owns windowing,
menus, shortcuts and operating-system integration.

## Workspace and information density

Design around sustained work: reading, editing, comparison and repeated actions.
Use panes, toolbars, inspectors, tables or canvases when the task warrants them.
Support useful density through alignment and hierarchy while keeping controls
legible and their hit areas usable.

Make resizing intentional. Establish a usable minimum window size, reflow or
collapse secondary panes when space tightens, and use larger windows to expose
useful context. Preserve focus, selection and scroll position across layout
changes. Test scaling and available display space rather than assuming one large
monitor or fixed pixel density.

## Input and operating-system behavior

Follow the target operating system for menus, window chrome, dialogs, standard
shortcuts and file interactions. Keep Command and Control conventions appropriate
to the platform and avoid taking over familiar editing commands.

Support keyboard traversal, visible focus and discoverable accelerators for
frequent work. Context menus, drag and drop, double-click and hover can improve
efficiency; provide a visible or keyboard-accessible route to essential actions.
Distinguish hover, keyboard focus, selection and the active pane.

Use native file dialogs and system behavior when the flow calls for them. For
editing flows, make save state, unsaved changes, undo/redo and close behavior
understandable. Cross-window actions and background work need feedback tied to
the affected document or task rather than an unexplained global status.

## Verify the affected flow

Run the actual shell or native application where available. Check minimum and
expanded windows, display scaling, keyboard-only operation, menu/shortcut parity
and focus across panes and dialogs. Exercise accessibility labels and order, plus
file/save/close and multiple-window behavior when the change touches them.

Verify each requested operating system that is available. A browser preview of
embedded content cannot establish desktop window, menu or lifecycle behavior;
state those limits when reporting results.
