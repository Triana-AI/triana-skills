# Contributing

Keep this repository thin. Contributions may improve the onboarding
instructions, plugin metadata, public documentation, or synthetic contract
tests. Do not add runtime validation, provider clients, executable helpers,
background services, or duplicate Triana Preview behavior.

Never contribute customer traces, credentials, provider responses, generated
private reports, checkpoints, or local machine paths. Use small synthetic
fixtures only.

Run the repository contract before opening a change:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p 'test_*.py' -v
```

By contributing, you agree that your contribution is licensed under
Apache-2.0 and that you have the right to submit it.
