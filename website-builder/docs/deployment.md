# Running and deploying

## Local application

Install the project and start it from the repository root:

```sh
python -m pip install -e .
python -m streamlit run app.py
```

The guided interview works without credentials. Generation requires a valid
server-side `OPENAI_API_KEY`, billing, connectivity, and access to `OPENAI_MODEL`.
If generation fails, check these settings and retry. Do not place keys in HTML,
JavaScript, GitHub issues, or screenshots.

If PowerShell activation is restricted, use the environment's Python directly:

```powershell
.venv\Scripts\python.exe -m pip install -e .
.venv\Scripts\python.exe -m streamlit run app.py
```

## Hosting the builder

The builder needs a Python host that supports Streamlit. Configure the application
entry point as `app.py` and set secrets as environment variables on that host.
`requirements.txt` installs the local package and its runtime dependencies.

The current app is designed for local or trusted use. It does not provide user
authentication, account quotas, billing controls, or durable storage. Add access
control and request limits before exposing an instance backed by your paid key.
Saving an open-source repository on GitHub does not itself host the application.

## Publishing a generated static page

1. Download `index.html` from the application.
2. Inspect its content, external resources, accessibility, and mobile layout.
3. Save it in a separate directory containing only public site files.
4. Deploy that directory through your chosen static host.

If you already use the Vercel CLI, sign in with `vercel login`, change into the
directory containing the reviewed HTML, and run `vercel` for a preview. Publish
to production with `vercel --prod` after reviewing the preview.

Deploy only the downloaded site's directory. The builder source, `.env`, model
files, and research data are not part of that static site. Vercel deployment has
not been executed or verified during this review.
