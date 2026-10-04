# Web interfaces

Read for browser-based pages and applications, including mobile web. Combine
with the desktop reference for a desktop shell with embedded web content.

## Layout and navigation

Let the page's job determine its opening. A public-facing page can lead with the
subject's most characteristic image, statement, demonstration or interaction.
An application should expose its primary task and useful state immediately.

Make responsive changes where content or controls stop fitting. Reflow navigation,
columns and density with intentional reading order; narrowing the viewport should
preserve the information needed to complete the task. Give wide tables and canvases
an explicit small-screen treatment rather than accidental page overflow.

Use semantic HTML and native controls as the foundation. Links navigate; buttons
act. Preserve deep links, browser Back/Forward and meaningful document structure.
On touch devices, every essential action needs a discoverable path without hover.
Account for safe areas and the on-screen keyboard when positioning fixed controls.

## Implementation

Keep CSS specificity predictable. Use the repository's styling conventions and
one clear owner for each component's spacing and layout; inspect competing rules
when a utility or component style silently cancels another.

Use available fonts deliberately, with fallback metrics that keep content usable
during loading. Reserve media dimensions to limit layout shifts. Match image
resolution to display size and defer nonessential media or motion when it would
delay the main content. External assets or font services should fit the project's
network, privacy and offline constraints.

## Verify the affected flow

Check representative narrow and wide viewports and the point where the layout
changes. Test long content and zoom for clipping, overlap and lost actions.
Exercise keyboard navigation, visible focus, form labels and error recovery;
dialogs should manage focus and return it to a useful place when dismissed.
Check touch paths and reduced motion where used. Inspect console/runtime errors
and verify that links, forms and primary controls do what their labels promise.

Screenshots assess composition. Interaction and accessibility checks assess whether
the same screen can be used. Report browser and viewport coverage actually exercised.
