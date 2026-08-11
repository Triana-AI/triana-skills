# Privacy

Triana Preview runs locally. Raw traces and generated reports remain on the
operator's device, and the public alpha sends nothing to Triana. There is no
hosted Triana ingestion path and no telemetry.

Every trace-reading operation requires explicit authorization. Provider mode
also requires explicit authorization for provider egress, a private provider
file, and a positive call ceiling. After local validation and redaction,
semantic evidence goes directly from the operator's machine to the configured
provider under the operator's credentials. Nothing is routed through Triana.

Provider retention and processing policies still apply. Redaction is not anonymity:
meaning and contextual information may remain in the evidence sent to the
configured provider. Use only data and provider access you are authorized to use.
