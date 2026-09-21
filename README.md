# release-agent-test

A small payments app used to exercise the Heimdall Release Agent against a real
repository: real pull requests, real changed-file sets, and governance read from
each pull request's base ref.

    web/        front end (React)
    services/   back end (Python)
    docs/       documentation

The release agent's inputs live in `.pipeline/`:

    tools.json                    the release capabilities available
    deployment.json               the release path and how each environment deploys
    policies/baseline.rego        governance, evaluated against the release plan
    policies/baseline.intent.json the same governance, structured, read by the resolver


