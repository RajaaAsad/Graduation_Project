# Publishing to GitHub

Use `website-builder` as the repository root. Include application source, tests,
public documentation, configuration examples, and the CI workflow.

## Check the files

Install the development dependencies and run:

```sh
python -m ruff check .
python -m ruff format --check .
python -m unittest discover -s tests -v
python scripts/check_release.py
```

The release checker looks for common credential formats and private artifacts.
When a Git repository exists, it also checks staged content and reachable history.
Review the files yourself as well: pattern checks cannot detect every private detail.

## Uploading through the GitHub website

Before uploading files manually, run the stricter folder check:

```sh
python scripts/check_release.py --all-files
```

Resolve every reported issue before uploading. Remove local caches and keep `.env`,
credentials, generated designs, datasets, and model weights outside the uploaded
files. GitHub's file uploader does not apply your local `.gitignore` rules.

Files beginning with a dot are not automatically private. Include `.gitignore`,
`.gitattributes`, `.env.example`, `.github/`, and `.streamlit/config.toml`.
Only placeholder values belong in `.env.example`.

## Publishing with Git

For a new repository, run:

```sh
git init
git add .
python scripts/check_release.py
git diff --cached --stat
git diff --cached
```

After reviewing the staged files, create an empty repository on GitHub and run:

```sh
git commit -m "Add Sitecraft website builder"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/website-builder.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username. If the folder already has a
repository or an `origin`, inspect its status and remotes before changing them.
`.gitignore` prevents new local files from being added; it does not remove files
that are already tracked or staged.

## Ownership

Confirm ownership of the code and assets before choosing a redistribution
license. Review the terms for any separately obtained models, datasets, or media.
