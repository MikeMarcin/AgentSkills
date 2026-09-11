# Writing for agents

Notes for people maintaining this package. Agents use [SKILL.md](SKILL.md) and,
for skill packages, [skill mechanics](references/skill-mechanics.md); nothing
points them here.

## Provenance

Adapted on 2026-09-11 under ASK-0071 from Matt Pocock's MIT-licensed
`writing-for-agents` skill (`https://github.com/mattpocock/skills`,
`skills/productivity/writing-for-agents`), read from a local checkout at commit
`3cca18b368ae95cdbdebbff572ccafa662551015`. That directory's tree is
`ad2925850efb8973a72d2e666f7a975f9a2d4a9b`; it last changed in `3216582`.

The concepts and their names are kept: context pointers, the two loads, the
information hierarchy, completion criteria, splitting, leading words and
pruning. The text is rewritten for AgentSkills rather than copied, as the wizard
companion was. Changes from the source:

- Skill mechanics target plain MASK packages shared by Claude and Codex. With no
  portable user-invoked mode, the invocation guidance becomes selection scope,
  reaching other skills by name, and the catalog in place of router skills.
- The applications recorded in RFC-ASK-0008 and RFC-ASK-0010 are folded in:
  operation-specific pointers, per-path load counting, obligations kept out of
  leading words, prohibitions reserved for authority and side-effect
  boundaries, and verification by tabletop and reachability rather than word
  quotas.
- Examples use AgentSkills vocabulary. The Codex `agents/openai.yaml` interface
  file is not carried over.

This package substantially adapts that material, so the upstream notice is
retained:

```text
MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
