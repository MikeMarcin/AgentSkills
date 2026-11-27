# Desktop applications

Read for native or cross-platform desktop applications. Qt applications also read
[Qt](qt.md); editors and developer tools also read
[Editors and tools](editors-and-tools.md). For web content inside a desktop shell
such as Electron or Tauri, also read [Web](web.md); the shell still owns
windowing, menus, shortcuts and operating-system integration.

## Workspace and information density

Design around sustained work: reading, editing, comparison and repeated actions.
Use panes, toolbars, inspectors, tables or canvases when the task warrants them.
Support useful density through alignment and hierarchy while keeping controls
legible and their hit areas usable.

Make resizing intentional. Establish a usable minimum window size, reflow or
collapse secondary panes when space tightens, and use larger windows to expose
useful context. Preserve focus, selection and scroll position across layout
changes. Test scaling and available display space rather than assuming one large
monitor or fixed pixel density. Decide compaction, such as folding labels to
icons, from the measured width at layout time with one rule for every platform,
rather than from guessed widths or per-platform thresholds.

Route scrolling to what the user means. A wheel over an empty or non-scrolling
overlay scrolls the content beneath it, and a trackpad gesture stays with the
nested scroller where it began. A scroller whose bar the system hides still
consumes gestures while it has range. A jump to a target shows all of it, clear
of sticky headers.

## Input and operating-system behavior

Follow the target operating system for menus, window chrome, dialogs, standard
shortcuts and file interactions. Keep Command and Control conventions appropriate
to the platform and avoid taking over familiar editing commands. On macOS,
Option+letter types characters, and menus can intercept it before a text field
does; avoid such shortcuts or let them yield to text input. Use the toolkit's
own command, settings, appearance and accessibility mechanisms rather than
drawing look-alikes, and follow the system's light or dark appearance unless the
product deliberately sets its own.

Support keyboard traversal, visible focus and discoverable accelerators for
frequent work. Context menus, drag and drop, double-click and hover can improve
efficiency; provide a visible or keyboard-accessible route to essential actions.
Distinguish hover, keyboard focus, selection and the active pane.

Use native file dialogs and system behavior when the flow calls for them. For
editing flows, make save state, unsaved changes, undo/redo and close behavior
understandable. Cross-window actions and background work need feedback tied to
the affected document or task rather than an unexplained global status.

## Verify the affected flow

Run the actual shell or native application where available, using each
platform's real UI font. Check minimum and expanded windows, display scaling,
keyboard-only operation, menu/shortcut parity and focus across panes and dialogs.
When the app can set its own theme, test it opposite the system theme and open
menus and dialogs in that state. Exercise accessibility labels and order, plus
file/save/close and multiple-window behavior when the change touches them.

Verify each requested operating system that is available. A browser preview of
embedded content cannot establish desktop window, menu or lifecycle behavior;
state those limits when reporting results.
