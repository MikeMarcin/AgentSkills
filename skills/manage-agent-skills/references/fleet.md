# Operate an enrolled MASK fleet

Use the selected MASK program's `capabilities --json`. Check the exact
`fleet.*` commands and flags in `data.commands` before running them. Central
taps also require version 1 of `data.fleet.tap_management` and compatible
device capabilities. Report a missing capability before attempting the operation.

## Inspect or enroll

Use `mask fleet device list --json` and
`mask fleet capability --device NAME --json` to inspect the binding and signed
device capabilities. Use repeated `--device NAME` on tap and maintenance
commands when the user names a subset. Check the preview's actual targets.

Enrollment requires an existing SSH alias, independently verified host key,
the device's signed identity and an explicit local grant. When enrollment
or authority changes are authorized, follow MASK's `docs/guides/fleet-enrollment.md`
for the local `fleet device authorize --policy FILE` and controller
`fleet device enroll NAME --ssh-config-alias ALIAS --binding FILE` previews
and approvals. Keep Git and SSH credentials with their existing machine.
Tap delegation names exact repositories or trusted forge namespaces and
eligible scope aliases. Rollout, upgrade, project Git commits and program
updates have their own grants.

## Choose the operation

| Intent | Command after `mask` |
|---|---|
| List centrally owned taps | `fleet tap` |
| Add an approved catalog binding | `fleet tap NAME URL` |
| Remove an unused fleet-owned catalog binding | `fleet untap NAME` |
| Fetch a catalog on the controller | `tap fetch NAME` |
| Roll out one skill to authorized personal scopes | `fleet install SOURCE/ID` |
| Review skill upgrades across granted scopes | `fleet upgrade --all` |
| Review an exact MASK program update on enrolled devices | `fleet update` |

Fleet install requires a configured desired-state repository and a fetched
controller tap. Use `--project-alias ALIAS` for an explicitly requested project
rollout. Use the controller's configured import mode or the user's selected mode.
Delegated tap sources use the device's own Git access. Forwarding requires a
separate static source grant. Fleet upgrade can also propagate a reviewed
canonical Git commit of project controls to eligible checkouts.

For a mutation, run the exact command with `--dry-run --json`. Review its
targets, authority and effects, including the controller's own catalog entry
for tap changes. Additions to at least one device can approve the controller
tap. Subset removals retain it. Apply the same command and target flags with
`--approve-plan HASH --json`, where HASH is `data.plan_hash`. Catalog changes
leave fetch and deployment to their own tasks.

Inspect exit status, `error.code`, `data.complete`, and each device result.
Check `data.controller_result` for tap changes. Exit 9 means some effects
remain unverified. Report those devices and the verified effects separately.
Retry a lost tap or maintenance acknowledgement using the same command and
hash. Preview again for changed plans or devices offline during preview.
Use `fleet tap` for current catalog state and `fleet operation show ID` for
a rollout's recorded outcome. A receipt reports its observed operation.
