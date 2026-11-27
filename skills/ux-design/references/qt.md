# Qt applications

Read for Qt Widgets or Qt Quick interfaces; also read the desktop reference, and
the editors and tools reference for developer tools. Keep the module the project
uses, and check its Qt version before relying on newer APIs.

## Layout, style and commands

Lay out with layouts, stretch factors and size policies rather than fixed
geometry, so fonts, translations and display scaling reflow. Set minimum sizes
from content and allow the window to grow. A scroll area or text view can keep a
few pixels of horizontal range while its content wraps, as `QPlainTextEdit` does;
confirm the range is zero, not just that the bar is hidden.

Style through `QPalette` roles and the platform style, and paint custom controls
from palette roles. Style sheets replace native drawing piecemeal: once a widget
is styled, related subcontrol, palette, focus and dark-mode behavior may need
explicit rules. Follow the project's rule when it restricts style sheets. On
Qt 6.5 and later, follow `QStyleHints::colorScheme` for light and dark appearance.

Menus, dialogs and other popups are separate windows, so a palette applied to a
widget subtree does not reach them. Apply the theme application-wide or through
one central hook for every popup, and test with the app theme opposite the
desktop theme. Palette roles also meet in pairs a theme may not have tuned, such
as `Mid` under `Base` text, and some styles draw fixed-color indicators that
vanish on dark backgrounds; check those pairs in both schemes.

Platform styles change control geometry. On macOS, a flat `QPushButton` or an
auto-raise `QToolButton` outside a toolbar still draws a native bezel, and push
buttons lay out by their bezel unless `Qt::WA_LayoutUsesWidgetRect` is set. The
Windows 11 style adds label padding. Where secondary buttons must match across
platforms, paint them from palette roles and measure each painted face.

Define each command once as a `QAction` with its text, icon, shortcut, enabled
state and checked state, then reuse it in menus, toolbars and context menus. Use
`QKeySequence::StandardKey` where a platform-standard shortcut exists. On macOS,
Qt gives a parentless `QMenuBar` to whichever window has focus; manage it so the
menu bar still works after the last window closes. Wrap user-visible strings in
`tr()` or `qsTr()`.

## Data, threads and state

Use model/view classes for large or changing data: a `QAbstractItemModel`
subclass with `QTableView`, `QTreeView` or `QListView` rather than item widgets.
Emit fine-grained change signals instead of resetting the model, so selection,
expansion and scroll position survive updates. Build hidden alternative views
lazily, since constructing and laying them out stalls the GUI thread.

Run long work outside the GUI thread with `QtConcurrent` or a worker object in a
`QThread`, and deliver results with queued signals. Touch widgets only from the
GUI thread. Restore window geometry and dock or splitter state with `saveGeometry`,
`saveState` and `QSettings`.

Qt sends no font-change event when a widget receives a font equal to its current
one, so metrics derived from settings such as tab width need their own update.
`QPlainTextEdit` ignores line height; leave such a setting visibly unavailable
there rather than faking it.

## Keyboard and accessibility

Set a deliberate tab order, label fields with buddies and mnemonics, and give
icon-only controls an accessible name and a tooltip. Keep focus visible under
custom styles. Give each focusable widget a unique accessible name and enforce it
with a test, since duplicates recur. A hidden widget can remain in the
accessibility tree; remove widgets that assistive technology should no longer
reach. Qt hides tooltips on a focus change, so post a focus-triggered tooltip to
the next event-loop turn, and place tooltips for small marks right beside them.

## Verify the affected flow

Exercise flows with `QTest` where the project has widget tests. Offscreen
captures (`QT_QPA_PLATFORM=offscreen`) use a fallback style, a light palette and
substitute fonts, some about twice as wide as the native UI font, so layouts can
pass offscreen and fail natively or the reverse. Judge visuals from natively
drawn, fully composed windows; on macOS, the native platform with
`Qt::WA_DontShowOnScreen` captures native drawing without showing the window.
`QT_SCALE_FACTOR` multiplies the device pixel ratio rather than replacing it. A
never-activated window paints with the inactive palette, and programmatic clicks
leave focus rings; activate the window and clear stray focus before capture.

Confirm final visuals on each requested operating system with its real UI font,
at 100%, 125% and 200% scaling, at the narrowest supported panel widths, in
light and dark schemes, and with a larger system font.
