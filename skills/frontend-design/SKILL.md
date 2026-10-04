---
name: frontend-design
description: Design and implement distinctive, usable interfaces for web, mobile and desktop. Use for new UI, visual redesigns, component styling or design critique; preserve existing product conventions when refining a surface. Pure backend work and logic-only fixes do not need this skill.
---

# Frontend design

Build interfaces with an identifiable visual character and a clear path through
the user's work. Treat appearance, content and behavior as one design problem.
The result should fit both the product and the conventions of its host platform.

## Establish the design boundary

Start from the requested change and the interface that already exists. Inspect
nearby screens, components, assets and tokens before choosing what to introduce.
Keep the current framework and product conventions unless changing them is part
of the assignment.

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

Read the applicable platform guidance before designing interactions:

| Target | Reference |
|---|---|
| Browser, including a mobile browser | [Web](references/web.md) |
| Native or cross-platform phone/tablet app | [Mobile](references/mobile.md) |
| Native or cross-platform desktop app | [Desktop](references/desktop.md) |

A hybrid application may need more than one reference. A viewport size alone
does not determine its navigation, input or lifecycle conventions.

## Turn the task into a composition

Work with realistic content early: the actual objects, names, actions and data
that people will see. A page of short placeholders conceals wrapping, density and
hierarchy problems. Mark invented examples as sample data rather than presenting
them as customer claims or live results.

Establish what the user needs to notice first, act on next and consult later.
Arrange the screen around those priorities. Use grouping to express relationships
and whitespace to separate decisions. A dashboard, an editor and a public-facing
page can share branding while needing different structures and densities.

For substantial work, briefly describe the layout, visual character and important
interactions before implementation. Compare rough alternatives when a structural
choice is unresolved. Keep this proportional: a component adjustment may need
only a local sketch or a sentence explaining its treatment.

Give aesthetic choices a reason rooted in the product. Its activity, imagery,
materials and audience can suggest an expressive direction. Explore a strong
choice where the brief leaves room, then judge it by coherence and usability.
Honor explicit references and established branding, including familiar styles.

## Make a coherent visual language

Choose a small set of repeatable relationships and express them in the project's
existing styling or theme system:

- **Typography:** define roles and a readable hierarchy through family, size,
  weight and spacing. Test the hierarchy with actual labels, long titles, body
  text and data. Preserve native text scaling where the platform provides it.
- **Color:** assign meaning to surfaces, emphasis, controls and feedback. Check
  contrast in the combinations the interface actually uses. Pair color with
  another cue when it conveys status or an available action.
- **Geometry:** relate spacing, alignment, borders, corners and elevation to
  grouping and interaction. Similar objects should behave like a family;
  different importance should remain visible.
- **Assets:** choose images and icons that reinforce the content. Account for
  crop, resolution, loading and empty space around them. Use the project's asset
  pipeline and respect its constraints on external resources.
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
understands.

Cover the states reachable in the requested flow, including empty content,
loading, errors, selection, focus and disabled actions where applicable. Explain
how to recover from failure and preserve entered work when recovery is possible.
Implement the interactions the requested deliverable promises; identify deliberate
mocks and external dependencies that remain unavailable.

Use semantic structure and accessible names alongside visible presentation.
Keyboard and assistive-technology order should follow a sensible task sequence.
Allow enough room for usable targets, text expansion and supported scaling.
Reusable components should carry these behaviors as well as their appearance.

## Evaluate the result in use

Run the affected surface in an available browser, simulator or native runtime.
Walk through the primary task with representative content, including a boundary
case such as a long label, empty dataset or recoverable error. Use the platform
reference to select relevant sizes, inputs and system interactions.

Inspect rendered output at both screen and component scale. Screenshots help
reveal weak hierarchy, uneven spacing and awkward wrapping; interaction checks
reveal unreachable actions, lost focus and unclear feedback. Correct observed
problems and recheck the affected parts.

Run the repository's relevant code checks as well. Distinguish a successful build,
visual inspection and an exercised user flow when reporting evidence. If a target
runtime is unavailable, identify the resulting verification gap.

Deliver the requested artifact or implementation with a concise account of the
important design decisions, working behavior and checks performed.
