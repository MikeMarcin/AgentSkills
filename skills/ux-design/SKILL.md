---
name: ux-design
description: Design, build and critique UX and UI for websites and web apps, mobile and desktop apps including Qt, game UI in Roblox or custom engines, and editors and developer tools. Use for new screens, redesigns, interaction flows, component styling or UX critique; refinements keep the product's existing conventions. Backend and logic-only work does not need this skill.
---

# UX design

Build interfaces with an identifiable visual character and a clear path through
the user's work. Treat appearance, content and behavior as one design problem.
The result should fit the product, its host platform and the inputs people use.

## Establish the design boundary

Start from the requested change and the interface that already exists. Inspect
nearby screens, components, assets and tokens before choosing what to introduce.
Keep the current framework and product conventions unless changing them is part
of the assignment.

Identify the runtime and UI toolkit, the input devices the product supports and
the range of displays it must serve, from a phone to a television or a
multi-monitor workstation. They constrain layout, text, assets and verification.

Match the work to the deliverable:

- For a **new interface**, identify the audience, main task and content before
  choosing a visual direction.
- For a **redesign**, identify which problems justify changes and which familiar
  behaviors should survive them.
- For a **component or local refinement**, solve the local problem using the
  surrounding system. Keep the scope proportional to the request.
- For a **critique**, connect each finding to a visible defect or an impeded task
  and propose a concrete correction. Edit only when asked to implement.

Resolve context from the conversation and repository. Ask when an unknown would
change the product's purpose or workflow; otherwise state a reasonable assumption
and keep moving. Design decisions do not create an extra approval stage.

Before designing interactions, read only the references in rows that match the
surface, and every such row: a Qt code-review tool matches both the Qt row and
the editors row.

| Surface | Read |
|---|---|
| Browser pages, web apps, hosted dashboards or generated HTML | [Web](references/web.md) |
| Native or cross-platform phone and tablet apps | [Mobile](references/mobile.md) |
| Desktop apps, including AppKit, SwiftUI, Windows toolkits and web-content shells | [Desktop](references/desktop.md) |
| Qt Widgets or Qt Quick | [Qt](references/qt.md) and Desktop |
| In-game UI in any engine: HUDs, menus, inventories, shops, dialogue | [Game UI](references/game-ui.md) |
| UI inside a Roblox experience | [Roblox experiences](references/roblox.md) and Game UI |
| Editors, inspectors, debuggers, review and other developer tools | [Editors and tools](references/editors-and-tools.md) and the row for its UI toolkit |
| Dear ImGui or other immediate-mode tool UI | [Immediate-mode UI](references/immediate-mode.md) and Editors and tools |
| Roblox Studio plugins | [Roblox Studio plugins](references/roblox-studio-plugins.md) and Editors and tools |

A viewport size alone does not determine navigation, input or lifecycle
conventions.

## Turn the task into a composition

Work with realistic content early: the actual objects, names, actions and data
that people will see, including the longest realistic values such as maximum
counts, long translated strings and long user, file or item names. A page of
short placeholders conceals wrapping, density and hierarchy problems. Mark
invented examples as sample data rather than presenting them as customer claims
or live results.

Establish what the user needs to notice first, act on next and consult later.
Arrange the screen around those priorities. Use grouping to express relationships
and whitespace to separate decisions. A dashboard, an editor, a game HUD and a
public-facing page can share branding while needing different structures and
densities.

Keep working surfaces lean. A row carries its label, its control and, when
needed, an info glyph whose tooltip or disclosure holds the explanation; shortcut
hints belong in tooltips. Drop text that repeats what a control already shows, and
move implementation vocabulary, identifiers, digests and raw request data into a
log or collapsed details. Every icon-only control still names its action in a
tooltip and accessible name. Narrow panels scroll only vertically: wrap rows of
controls and elide user-supplied names, with the full text in a tooltip. Hiding a
horizontal scroll bar leaves trackpad panning in place.

For substantial work, briefly describe the layout, visual character and important
interactions before implementation. Compare rough alternatives when a structural
choice is unresolved. Keep this proportional: a component adjustment may need
only a local sketch or a sentence explaining its treatment. When a mockup has been
approved, build to its measured sizes and spacing rather than toolkit defaults or
an approximation.

Give aesthetic choices a reason rooted in the product. Its activity, imagery,
materials and audience can suggest an expressive direction. Explore a strong
choice where the brief leaves room, then judge it by coherence and usability
inside the product: a look chosen in a standalone mockup can feel foreign once
embedded. Build special surfaces from the product's own type, color roles and
components. Honor explicit references and established branding, including
familiar styles.

## Make a coherent visual language

Choose a small set of repeatable relationships and express them in the project's
existing styling or theme system:

- **Typography:** define roles and a readable hierarchy through family, size,
  weight and spacing. Test the hierarchy with actual labels, long titles, body
  text and data. Preserve the platform's text scaling where it provides one.
- **Color:** give each meaning one color role, and keep accents clear of state
  colors such as error red. Check contrast for the pairs that actually meet,
  including text over highlights and fills, on rendered pixels with headroom:
  antialiasing and fractional scaling paint thin text below its nominal ratio.
  When color conveys status or an available action, keep it and add a shape,
  stroke or label that remains legible at the real size.
- **Geometry:** relate spacing, alignment, borders, corners and elevation to
  grouping and interaction. Similar objects should behave like a family;
  different importance should remain visible.
- **Assets:** choose images and icons that reinforce the content. Account for
  crop, resolution, loading and empty space around them. Judge icons at their
  real size, and replace placeholder or lettered icons before review. Use the
  project's asset pipeline and respect its constraints on external resources.
- **Movement:** use transitions to preserve context between states. Match duration
  and emphasis to the interaction, and provide a reduced-motion treatment that
  retains the information needed to understand the change.

Evaluate the composition as a whole. Strong type, imagery, color and motion all
compete for attention; reduce competing emphasis until the important content is
easy to find. Repeated decorative treatments should have a role in the product's
visual language, rather than filling space left by unfinished content.

## Complete the interaction

Design controls together with their consequences. Show which object an action
affects, whether work is in progress and how completion or failure appears. Keep
action names consistent across the flow and write in vocabulary the user already
understands. Direct manipulation should respond at once; long work shows progress
tied to its object, with cancellation where the operation allows it.

Keep layout stable under the pointer: edits, status messages, late data and
restored layout must not move or open what the user is about to use. Reserve room
for changing text, or show a short headline with details on demand, so it never
reflows controls or resizes a render surface.

Implement the interactions the requested deliverable promises. Every enabled
control must reach real behavior in the running product; a mechanism that passes
its tests is not a feature until the real interface dispatches it. Identify
deliberate mocks and external dependencies that remain unavailable. Add a new
capability as an explicit action beside the existing workflow, rather than as a
toggle that silently changes what the next gesture does.

Give each essential action a route for every input the product supports: pointer,
touch, keyboard, gamepad or other controllers. Hover, gestures and shortcuts can
accelerate an action that also has a visible route. Show prompts and glyphs for
the input in use.

Cover the states reachable in the requested flow, including empty content,
loading, errors, selection, focus and disabled actions where applicable. Keep
loading distinct from empty: unloaded data never reads as "none". Answer an open
or navigate gesture at once by moving to the destination with what is already
known, then fill in the rest, naming the current step during a slow wait. A
disabled control says why in its tooltip. Explain how to recover from failure and
preserve entered work when recovery is possible.

Use the platform's semantic structure and accessible names alongside visible
presentation. Keyboard, gamepad and assistive-technology order should follow a
sensible task sequence. Allow room for usable targets, text expansion and
supported scaling. Reusable components should carry these behaviors as well as
their appearance.

## Evaluate the result in use

Run the affected surface in its real runtime, as the matching reference's
verification section describes. Walk through the primary task with representative
content, including a boundary case such as a long label, empty dataset or
recoverable error.

Inspect rendered output at both screen and component scale. Judge the fully
composed surface as the real runtime draws it, at the user's display scale, in
every intermediate state a person can stop at, not only where a scripted flow
ends. Clear focus rings left by scripted input. When the user supplies a
screenshot, reproduce its state and compare. Correct observed problems and
recheck the affected parts.

Automated UI checks should assert a perceptible effect in the expected direction,
such as a drag that visibly moves the view the right way, rather than any change
at all. Confirm that each visual state a check claims actually appears in its
captures. Run the repository's relevant code checks as well. Distinguish a
successful build, visual inspection and an exercised user flow when reporting
evidence. If a target runtime, device or input is unavailable, identify the
resulting verification gap.

Deliver the requested artifact or implementation with a concise account of the
important design decisions, working behavior and checks performed. Show visual
changes as screenshots of the rendered states rather than describing them.
