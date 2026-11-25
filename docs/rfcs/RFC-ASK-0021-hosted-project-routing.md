---
id: "RFC-ASK-0021"
title: "Route attended reviews by project"
status: "Implementing"
metadata: {"milestone_plan":{"id":"hosted-project-routing","path":"docs/rfcs/plans/hosted-project-routing/milestone-plan.json"}}
---

# Route attended reviews by project

The owner requested a project-local follow-up to
[RFC-ASK-0020](RFC-ASK-0020-hosted-review-producer.md) on 2026-11-24. A consumer
can opt new sessions into hosted review with a checked routing file for its
enrolled producer origin, project and owner. An operator supplies the installation
locally or uses a configured installation for a checkout that has one. The
producer credential retains its process-only input. The change covers the
shared AgentSkills skill and disposable local verification. Consumer installation,
Athens changes and live enrollment are outside the assignment.

- **AC01** Two consumers of the same skill can select their own project mode and
  route. Missing configuration keeps the legacy default. Malformed or out-of-scope
  configuration fails when consulted. Explicit mode flags and existing sessions
  preserve the stored mode.
- **AC02** First hosted publication requires explicit title and candidate selection.
  Explicit routing flags override project defaults. Once staged locally, retries
  and Hand Back use the saved package and binding, including when project settings
  change. Credentials, HTTPS validation and redirect refusal retain the native
  producer's boundaries.

[Work and closeout](../issues/30-in-progress/ASK-0143-hosted-project-routing.md).
