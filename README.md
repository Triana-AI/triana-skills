# Triana Skills

Triana Skills contains one thin onboarding skill for Codex and Claude. It
guides an authorized local trace through the exact `triana-preview==0.1.0a1`
command line and contains no analysis engine or provider implementation.

Triana Preview turns conversational-agent traces into a proposed,
evidence-grounded map of user demands and repeated agent behavior. It runs
locally, sends nothing to Triana, and makes no correctness, evaluation, or
pass/fail claim.

## Install

Add this repository as the `triana-skills` marketplace, install the `triana`
plugin, then start a fresh agent session and ask it to use the `onboard` skill.

For Codex:

```sh
codex plugin marketplace add Triana-AI/triana-skills
codex plugin add triana@triana-skills
```

For Claude Code:

```sh
claude plugin marketplace add Triana-AI/triana-skills
claude plugin install triana@triana-skills
```

Restart the agent after installation so it discovers the new skill. The agent
will not read trace data until you explicitly authorize the trace path.

The agent requests only the trace path, short agent description, trace
authorization, and either no-provider mode or a private provider file with
provider-egress authorization and a maximum call ceiling.

The skill is Apache-2.0. The separately distributed Triana Preview runtime is
source-available under its own terms; Triana Preview is not open source.

Copyright 2026 Akarsh Gajbhiye
