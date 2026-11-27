# Roblox experiences

Read for UI inside a Roblox experience; also read the game UI reference. Studio
plugins use the Roblox Studio plugins reference instead. Engine APIs change between
releases, so consult the current Roblox Creator documentation when exact behavior
matters.

## Structure and layout

Follow the project's UI approach: Instances authored in Studio or Luau, or a
declarative library such as React for Luau or Fusion. Keep UI source where the
project's sync tool expects it. Use ScreenGui for screen UI, SurfaceGui for UI on
parts and BillboardGui for world-anchored labels and markers. Set
`ResetOnSpawn` deliberately: the default rebuilds the UI on each respawn and
discards its state.

Lay out with UDim2 and layout objects instead of hand-placed coordinates. Scale
gives proportion and Offset gives fixed detail. Pure Scale makes elements huge on
tablets and cramped on phones, so bound it with `UISizeConstraint`,
`UIAspectRatioConstraint` or a `UIScale` driven by the viewport. Position from
edges and centers with `AnchorPoint`. Arrange groups with `UIListLayout`,
`UIGridLayout`, `UIFlexItem` and `UIPadding`; use `AutomaticSize` where content
determines size. Order overlapping UI with `ZIndex` and between ScreenGuis with
`DisplayOrder`.

Leave room for Roblox's own interface. `ScreenGui.ScreenInsets` defaults to
`CoreUISafeInsets`, which keeps interactive UI clear of the top bar and screen
cutouts. Reserve `DeviceSafeInsets` or `None` for backgrounds and full-bleed art.
Use `TopbarSafeInsets` or `GuiService.TopbarInset` for UI placed in the top bar.
Replace core UI such as chat, the backpack or the player list only when the
experience provides that function itself.

For text, prefer an explicit `TextSize` with `AutomaticSize` or wrapping to
`TextScaled`, which produces inconsistent sizes across devices. When `TextScaled`
is used, bound it with `UITextSizeConstraint`. `GuiService.PreferredTextSize`
reflects the player's text-size setting; let containers grow with it, and measure
with `TextService:GetTextBoundsAsync`, which honors that setting. Escape any
user-provided text placed in `RichText`.

Upload images through the project's asset workflow and allow for moderation.
Build scalable panels with nine-slice images (`ScaleType.Slice` and
`SliceCenter`) or with `UICorner`, `UIStroke` and `UIGradient`. Use sprite sheets
through `ImageRectOffset` and `ImageRectSize`. `CanvasGroup` costs texture memory
and resolution; reserve it for effects that need group transparency.

## Input and devices

Players arrive on phones, tablets, computers, consoles with gamepads and VR.
Adapt prompts and layout to `UserInputService.PreferredInput` and listen for its
changes. It follows the most recent input, so a newly connected gamepad may not
register until it is used. Avoid inferring the device from screen size or
`TouchEnabled` alone.

Handle buttons with `GuiButton.Activated`, which works for mouse, touch and
gamepad. For gamepad navigation, set `GuiService.SelectedObject` when a menu
opens and restore it when the menu closes. Use `Selectable`, the
`NextSelection*` properties for non-geometric order and `SelectionGroup` with
`SelectionBehavior*` set to `Stop` to keep selection inside a dialog. Style
`SelectionImageObject` to match the UI, and make the back button close the menu.
Keep touch controls clear of the thumbstick and jump button. Use
`ContextActionService` or `ProximityPrompt` where their built-in, device-aware
prompts fit.

## Platform rules and services

Filter user-generated text before showing it to other players with
`TextService:FilterStringAsync` and the result method for its audience. Show
display names, allowing for long and non-Latin names.

Start purchases through `MarketplaceService` prompts; leave the purchase
confirmation to Roblox's own dialog. Show prices in Robux and mark what the
player already owns. Disclose odds before any paid random item, and check
`PolicyService:GetPolicyInfoForPlayerAsync` for features restricted in the
player's region.

Use `LocalizationService` and localization tables for player-facing strings,
with `AutoLocalize` behavior chosen deliberately for dynamic text. When
`GuiService.ReducedMotionEnabled` is true, replace movement tweens with fades or
immediate changes.

## Verify the affected flow

Playtest in Studio and use the Device Emulator for phone, tablet, desktop and
console profiles, including orientation, safe insets and the top bar. Complete
menus with a gamepad, and test with larger text and reduced motion. Use a
multi-client test when UI depends on replicated state. Check the Output window
for errors, and use the MicroProfiler when UI updates appear in heavy frames.

Use whatever Studio automation the session provides to playtest, capture
screenshots and send input; otherwise give the user exact playtest steps. Report
emulated profiles separately from real devices, since emulation does not establish
touch feel, device performance or console readability.
