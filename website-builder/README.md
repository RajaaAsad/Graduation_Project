# Sitecraft — AI Website Builder

Turn a guided design conversation into a responsive HTML and CSS page. Sitecraft
asks about content, colors, typography, and layout, then uses the OpenAI API to
produce a static design that you can download and refine.

Originally developed as a graduation project, this edition separates the
interface, interview logic, classifiers, and code generation into testable modules.

## What you can build

- Landing pages, blogs, and restaurant pages.
- Event, coming soon, and contact pages.
- Sign-in and sign-up interface prototypes.

Each format has a dedicated interview with conditional follow-up questions.
The app supports regeneration and edit requests, keeps designs separate across
browser sessions, and provides an HTML download and source inspection.

**Scope:** Sitecraft creates static design prototypes. Authentication, payments,
form submission, live countdowns, and other backend features are not implemented.
Generated pages require review before publication. Generation uses a paid API;
the guided interview works without a key or machine-learning model downloads.

## Quick start

Use Python 3.11 or 3.12. Run these commands from this folder.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

For macOS or Linux, activate with `source .venv/bin/activate` and copy the
configuration with `cp .env.example .env`.

Edit `.env` and set `OPENAI_API_KEY` to your own key. Then start the app:

```sh
python -m streamlit run app.py
```

Open the local URL printed by Streamlit and select one of the eight page buttons.
Answer the questions, select **Generate design**, and download the
result. With an existing design, use the chat input to request changes.
Select **Start a new design** to return to the page selection screen.

No website is published automatically. The app does not write generated designs
to a shared server file or copy credentials into the downloaded HTML.

## Configuration

Environment variables override the local `.env` file.

| Variable | Default | Purpose |
| --- | --- | --- |
| `OPENAI_API_KEY` | Empty | Required for code generation; kept on the server |
| `OPENAI_MODEL` | `gpt-4.1-mini` | Model used for generation; account access may vary |
| `USE_ML_CLASSIFIERS` | `false` | Enable the original research classifiers |
| `INTENT_MODEL_PATH` | `models/intent-classifier` | Local trained classifier directory |

By default, the app accepts exact choices and preserves free-text design details.
For the optional BERT and multilingual zero-shot models, see
[Model setup](docs/models.md). Model weights and research datasets are excluded
from this release.

## Project structure

```text
website-builder/
├── app.py                     # Streamlit entry point
├── website_builder/
│   ├── config.py              # Environment settings and project paths
│   ├── interview.py           # Validated flows and interview state
│   ├── classifiers.py         # Choice validation and optional ML inference
│   ├── generation.py          # OpenAI integration and HTML checks
│   └── data/                  # Eight flows and the trained label mapping
├── assets/                    # Interface stylesheet and SVG chat avatars
├── models/README.md           # Local model placement guide
├── scripts/check_release.py   # Files, staged content, and history checks
├── tests/                     # Unit tests and Streamlit session tests
├── docs/                      # Code walkthrough, architecture, and setup guides
├── .github/workflows/ci.yml    # Automated quality and release checks
├── .streamlit/config.toml     # Interface theme
└── pyproject.toml             # Package metadata and dependency bounds
```

## Development checks

```sh
python -m ruff check .
python -m ruff format --check .
python -m unittest discover -s tests -v
python scripts/check_release.py
```

Tests exercise interview branching, session isolation, HTML validation, failed
generation, environment precedence, and credentials hidden in staged files or
Git history. API responses are mocked; the test suite makes no paid requests.

Dependencies have explicit version bounds in `pyproject.toml`. Tests use mocked
API responses; live generation and optional model inference need separate checks.
CI runs on Python 3.11 and 3.12 after the project is pushed.

## Documentation

- [Understanding the code](docs/code_walkthrough.md)
- [Architecture and behavior](docs/architecture.md)
- [Optional model setup](docs/models.md)
- [Running and deploying](docs/deployment.md)
- [Preparing a public GitHub repository](docs/publication.md)
- [Contribution guide](CONTRIBUTING.md)
- [Security and privacy](SECURITY.md)

The API integration uses the [OpenAI Responses API](https://developers.openai.com/api/docs/guides/text).
Do not expose an unauthenticated, publicly reachable instance using your paid API
key; see the deployment guide before hosting the application.

## License and attribution

No open-source license has been assigned. Confirm ownership and choose a license
before inviting redistribution. The original trained models and datasets have
separate provenance and licensing considerations described in the model guide.
