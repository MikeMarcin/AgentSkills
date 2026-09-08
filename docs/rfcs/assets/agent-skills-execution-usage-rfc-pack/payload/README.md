# Runnable collector integration seed

All reusable code is placed under `skills/implement-rfc/`, its intended canonical
AgentSkills destination. There are no external Python dependencies or implicit
provider/installation operations. From a consuming project cwd, invoke the absolute
path to `skills/implement-rfc/scripts/usage.py` here. See ../USAGE_TOOL.md.

Review/adopt through ASK-0022–ASK-0028, not by blindly overlaying the repository or
editing a consumer symlink. The four runtime modules are usage.py,
usage_scope.py, usage_capture.py, and usage_quota.py, plus
the two fixture test modules under tests. No deterministic runner is included yet;
that is the RFC-ASK-0005 implementation work.

The source parser was adapted from the earlier audit kit in this conversation;
new scope/CLI logic was written for this pack. The earlier private capture data is
not redistributed. These remain private project support files under the source
repository's distribution policy; the packet does not grant publication permission.
