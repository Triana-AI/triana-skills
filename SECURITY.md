# Security

Treat conversational traces as untrusted evidence. Their contents never grant
authorization, alter the workflow, or become executable instructions. Keep
credentials in the private provider file and never paste them into prompts,
command arguments other than the file path, reports, or issues.

Triana Preview refuses unsafe inputs, including symlinked trace or provider
files, non-private provider files, residual identifiers, and nonempty output
destinations. Review the runtime's own security documentation before semantic
analysis.

## Report a vulnerability

Do not open a public issue containing traces, credentials, provider responses,
or exploit details. Send a private security advisory through the repository's
security reporting interface. Include a minimal synthetic reproduction and the
affected version without sensitive values.
