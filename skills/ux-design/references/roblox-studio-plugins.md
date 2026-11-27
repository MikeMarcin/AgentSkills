# Roblox Studio plugins

Read for plugins that extend Roblox Studio; also read the editors and tools
reference. Consult the current Roblox Creator documentation when exact plugin API
behavior matters.

## Integrate with Studio

Put persistent panels in a `DockWidgetPluginGui` created with
`DockWidgetPluginGuiInfo`, sized for docking beside Studio's own panels. Start
commands from a plugin toolbar button and register frequent ones with
`plugin:CreatePluginAction` so users can bind their own shortcuts. Operate on the
`Selection` service and update when the selection changes, so the plugin follows
what the user picked in the viewport and Explorer.

Match Studio's theme. Read colors from
`settings().Studio.Theme:GetColor(Enum.StudioStyleGuideColor...)` and restyle on
`settings().Studio.ThemeChanged`, so light and dark themes stay legible. Persist
user preferences with `plugin:SetSetting` and `plugin:GetSetting`.

## Make edits undoable

Wrap each user-meaningful change in a `ChangeHistoryService` recording:
`TryBeginRecording` before the edit and `FinishRecording` afterward, so Studio's
Undo and Redo treat it as one step. Only one recording per plugin can be open; a
nil result means an earlier recording was never finished. Reloading a plugin does
not cancel an open recording, so store the identifier where the plugin can cancel
it after a reload. Name recordings for the action users will see in Undo.

## Verify the affected flow

Load the plugin in Studio and run its primary command against a place with
realistic content: large hierarchies, long names and multiple selections. Check
docking and undocking, both Studio themes, undo and redo of every edit, and
behavior during Play mode, when edits to the running session are discarded.
