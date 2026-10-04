# Mobile applications

Read for native or cross-platform phone and tablet applications. A site viewed
on a phone uses the web reference; mobile-app guidance applies when the product
also has native navigation, controls or lifecycle behavior.

## Platform and layout

Use the target platform's conventions for navigation, back behavior, sheets,
menus and system controls. A shared visual identity can use different navigation
and control treatments on iOS and Android. Follow the project's framework and
native component library; consult current official platform guidance when exact
metrics or API behavior matter.

Prioritize the task within reachable touch areas. Account for safe areas, system
bars, display cutouts and the keyboard. Respect platform minimum touch targets in
logical units, including hit areas larger than the visible icon when appropriate.
Primary actions should remain discoverable without knowing a hidden gesture.

Adapt phone, tablet, supported orientations and resizable windows deliberately.
A wider surface can expose related content or a second pane when useful. Preserve
selection and navigation context when the layout changes.

## Interaction and states

Use platform text styles and accessibility semantics so Dynamic Type or font
scaling and screen readers work with custom visuals. Support localized text,
including changed length and direction when applicable; avoid fixed-height text
containers that clip enlarged content.

Match keyboard type, input assistance and focus movement to the field. Keep the
focused field, validation feedback and required action visible above the keyboard.
Use haptics as supplemental feedback when appropriate to the app and platform.

For affected flows, consider interrupted requests, connectivity loss, permission
denial and returning from the background. Preserve drafts and navigation context
through recoverable interruptions, and provide retry or recovery at the failure.

## Verify the affected flow

Exercise the requested platform in an available simulator or device. Check a compact
screen and any supported tablet or larger layout, enlarged text, keyboard overlap,
back navigation, touch targets and screen-reader order. Verify reduced motion
where animation is present and lifecycle recovery where the change affects it.

Report which platforms and devices were exercised. A browser approximation or a
shared-framework build alone does not verify native interaction or accessibility.
