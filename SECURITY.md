# Security

AgentSkills is a source preview of skill instructions, local Python helpers and
examples. Security fixes target current main. There are no supported release
branches or hosted service. Hosted model providers and application integrations
have their own security policies.

Review a skill and any declared setup script before approving installation.
Helpers may inspect local files, invoke Git, run bounded commands or start a
loopback review server within the selected workflow. Repository and task scope
remain the authority for mutations. Generated role settings, advisory candidate
protection and successful tests do not sandbox an agent or prove loaded policy.

Keep credentials, private prompts, consumer metadata and usage archives out of
commits and public reports. Use disposable fixtures for vulnerability reproduction.
MASK's package validation and ownership checks belong to
[ManageAgentSkills](https://github.com/MikeMarcin/ManageAgentSkills).

Private vulnerability reporting is not currently enabled. Before posting sensitive
details, check the repository's
[Security page](https://github.com/MikeMarcin/AgentSkills/security) for a private
reporting option. If it is unavailable, open an issue containing only a request for
a private contact channel. Include affected paths, candidate revision and a
sanitized description. Share sanitized reproduction details only after a private
channel is established. Never send live credentials through any channel.
Enabling GitHub's private reporting remains a maintainer step when the repository
becomes public.
