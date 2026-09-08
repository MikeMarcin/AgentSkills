# Remote stations

No remote stations are configured for this project. Local implementation only. Existing portable workflow remote helpers are optional, not a MASK feature or prerequisite.


## Native qualification host

Owner confirmed ExampleWinHost availability on 2026-09-08. Trusted SSH alias
`example-win-host` reaches `example-win-host.local` with native Windows; the bare `example-win-host`
alias did not match an existing trusted host-key entry and was not bypassed.
The existing `mask-win-example-win-host` station belongs to ManageAgentSkills, at
`C:\code\git\ManageAgentSkills-win-example-win-host`, with `read-only-proof` authority.
It is not an AgentSkills writing station. AgentSkills native qualification may
use task-owned disposable Windows fixtures over that existing SSH connection,
without modifying the station checkout, changing credentials/permissions or
launching additional model tasks beyond an explicit budget. Absence of an
AgentSkills station row does not mean Windows tooling is unavailable.
