# Contributing

Start with the setup instructions in `README.md` and install the development
extras using `python -m pip install -e ".[dev]"`.

Keep interface code in `app.py` and domain logic in `website_builder/`. Add new
page questions to `data/question_flows.json`; use explicit answer types and
dependencies. Keep the trained label map aligned with the original classifier.

For behavior changes, add tests covering the user-visible outcome and failure
path. Mock paid APIs. Do not download research models during the normal test run.
Run lint, formatting, tests, and the release checker before proposing a change.

Describe the problem, resulting behavior, and validation in pull requests.
Do not include credentials, user conversations, generated private sites,
research datasets, or model binaries in commits or issue reports.

The project currently has no redistribution license. Confirm terms with the
owner before redistributing modified versions.
