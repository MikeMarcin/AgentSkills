# Game UI

Read for interfaces inside a game or real-time 3D experience in any engine:
HUDs, menus, inventories, shops, dialogue, onboarding, notifications and world
markers. Roblox experiences also read [Roblox experiences](roblox.md); debug
overlays and in-game developer tools also read
[Editors and tools](editors-and-tools.md).

## Play context and hierarchy

Interface competes with the scene for attention. Decide for each element whether
it is persistent HUD, contextual (shown when relevant, then gone), placed in the
world (nameplates, markers, signs) or a menu that pauses or overlays play. Keep
the center of the screen and the direction of action clear. Put status at the
edges and alerts where the player is already looking.

Make critical state glanceable: position, shape and color should change together,
with numbers where precision matters. Readability cannot depend on the scene
behind the element. Use backing plates, outlines or shadows that hold over bright
sky, dark interiors and busy effects. Scale feedback to significance so routine
events stay quiet and important ones remain unmistakable. Pair visual feedback
with audio and haptics where the platform supports them.

Inventories, shops, upgrades and other decision screens should keep the player
oriented. Show what an item does, what it costs, what is already owned and how a
choice compares with the current one before commitment. Confirm irreversible
spending; where the platform supplies a purchase dialog, that dialog is the
confirmation. Teach controls in context with prompts for the active input device, and
let players dismiss a tutorial and find it again.

## Displays and input

Anchor elements to edges, corners or the center, and size them from a reference
resolution or UI scale rather than fixed pixels. Constrain art to its aspect ratio.
Cover the supported range of aspect ratios, including ultrawide, 4:3 and portrait
phones if those are supported. Respect safe areas for cutouts, rounded corners and
television overscan. Text read from across a room needs larger minimum sizes than
desktop text; provide a UI or text scale setting where the target displays vary.

Support each device the game ships on, and follow the most recent input as players
switch devices: update glyphs, prompts and hit areas immediately. For gamepads, make
every interactive element reachable by directional navigation with a visible
selection highlight. Set initial focus when a menu opens and restore it when the
menu closes. Keep confirm and back consistent with the platform's convention. For
touch, place controls within thumb reach and clear of movement and camera zones.
Offer remapping where the game has bindings. While a menu or text field is open,
decide which gameplay inputs it captures and apply that rule consistently.

## Engine implementation

Use the engine's UI system and the project's framework. Drive interface updates
from game-state changes rather than rebuilding everything each frame. UI shares
the frame budget: limit per-frame layout, text shaping and allocation, atlas icons
and batch draws, then measure the cost on the lowest supported hardware.

Route all player-facing text through the localization system and leave room for
substantially longer translations. Ensure font coverage for every shipped
language, with fallback fonts and right-to-left layout where shipped. Keep text out
of baked images. Format numbers, currency and time for the locale.

Engines often lack an operating-system accessibility tree. Provide subtitles with
speaker names and size options, cues that do not rely on color alone, hold-versus-
toggle choices, remappable controls and an adjustable UI scale. Offer settings to
reduce camera shake, flashing and screen motion, and avoid rapid flashing by
default. Consult current platform accessibility guidelines when a console or store
imposes requirements.

Account for lifecycle: in multiplayer, opening a menu does not pause the world, so
the player should still see threats or time-critical state. Handle controller
disconnection, suspend and resume, and reconnection without losing menu context or
unsaved choices.

## Verify the affected flow

Play the flow in the running game rather than judging a static mockup. Exercise
each supported input device, switching devices mid-flow, and complete every menu
path with a gamepad alone where gamepads are supported. Check the minimum and
maximum supported resolutions and aspect ratios, a safe-area or cutout profile,
and television-distance readability for console targets. View the UI over bright,
dark and busy scenes, with the longest translated strings and maximum values.
Check its frame-time cost on low-end target hardware.

Report which devices, inputs and resolutions were exercised. A capture from one
editor viewport does not verify other displays, input switching or performance.
