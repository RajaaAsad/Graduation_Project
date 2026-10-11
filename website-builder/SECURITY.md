# Security and privacy

## Credentials and publication

Keep OpenAI keys on the server in environment variables or the ignored `.env`
file. Never add real values to `.env.example`. The release checker examines both
staged files and reachable Git history; `.gitignore` alone does not protect a
secret that has already been tracked.

If a key is exposed, revoke it, replace it, and inspect repository history before
publishing. Removing a key from the latest source file does not invalidate it or
erase earlier snapshots.

## Design data

The app sends the completed brief to OpenAI when you select Generate design.
Edit requests also send the current HTML. Requests use `store=False`, which is
not a guarantee of zero retention under every service policy. Avoid supplying
passwords, financial details, personal records, or other confidential data.

Conversation state and successful designs live in the Streamlit session. The app
does not intentionally log briefs, generated HTML, keys, or raw API exceptions.
External image URLs in a downloaded page may contact their hosts when opened.

## Generated HTML

Treat generated files as untrusted content. The app checks for a complete
document and blocks common active HTML constructs, but this is not a complete
sanitizer or a guarantee of safe content. CSS, links, and HTTPS image resources
still require review. The app presents source and a download without executing
the generated page inside the builder interface.

Forms and sign-in pages are visual prototypes. They do not authenticate users or
process submissions. Review content, resource licenses, and accessibility before
hosting a generated design.

## Hosted instances

Use the app locally or with trusted users. Add authentication and request limits
before operating an internet-facing instance with your API key. Optional model
downloads must come from trusted sources; do not load unknown pickled artifacts.

## Reporting an issue

Contact the repository owner privately using the contact method on their GitHub
profile. Do not paste keys or exploit details into a public issue. A dedicated
security contact has not yet been configured.
