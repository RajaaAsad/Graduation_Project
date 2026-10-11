# Understanding the code

The application follows five steps:

1. The user chooses a page type.
2. The app asks questions about the design.
3. It saves the accepted answers as a design brief.
4. It sends the brief to OpenAI and checks the returned HTML.
5. The user downloads the design or requests a change.

## Where to start reading

| File | Responsibility |
| --- | --- |
| [`app.py`](../app.py) | Display the interface and respond to user actions |
| [`styles.css`](../assets/styles.css) | Define colors, typography, spacing, and mobile layout |
| [`config.py`](../website_builder/config.py) | Read settings such as the API key and model path |
| [`interview.py`](../website_builder/interview.py) | Keep answers and choose the next question |
| [`classifiers.py`](../website_builder/classifiers.py) | Check choices and optionally interpret answers with ML |
| [`generation.py`](../website_builder/generation.py) | Request HTML from OpenAI and validate it |
| [`question_flows.json`](../website_builder/data/question_flows.json) | Store the questions for each page type |

Read `main()` in `app.py` first. It sets up the page, displays the current
conversation, and handles one user message. Streamlit runs the script again
after an interaction. `st.session_state` keeps the conversation and design
between those runs.

Visual styling lives in `assets/styles.css`, so it can be changed without editing
the interview or generation logic. The app loads that trusted local stylesheet;
user messages are still displayed as plain text in native Streamlit chat elements.
Each message has a container key such as `chat-user-1`. The stylesheet uses that
key to place user replies on the right and assistant messages on the left.

The other interface functions have specific jobs:

- `show_page_picker()` displays the eight page buttons and starts the selected interview.
- `save_answer()` checks an answer and adds the next question.
- `show_design()` displays the generation button, source, and download.
- `generate_design()` requests a design and handles success or failure.

## Following one answer

This example uses the interview logic without the interface or a paid API call:

```python
from website_builder.config import Settings
from website_builder.interview import Interview

interview = Interview("signin")
settings = Settings()

print(interview.current.question)  # Ask whether the background is a color or image.
interview.answer("color", settings)

print(interview.current.question)  # Ask which background color to use.
interview.answer("blue", settings)

print(interview.current.question)  # Ask about form fields; skip the image question.
```

Inside `answer()`, the code checks the response, saves the question and answer,
then moves forward. It skips follow-up questions whose conditions do not match.
For example, a user choosing a color does not need to provide a background image.

Each question has four fields:

| Field | Meaning |
| --- | --- |
| `question` | The text shown to the user |
| `dependencies` | When to ask it: always, or after a matching choice |
| `model_type` | How to handle the answer: text, intent, or choice |
| `candidate_labels` | The available choices, when the question has choices |

## Answer handling

`classify_answer()` selects one of three paths:

- **Text:** keep the user's wording.
- **Intent:** keep the wording by default; use the trained classifier in ML mode.
- **Choice:** match one of the listed answers; use the zero-shot model for other
  wording only when ML mode is enabled.

The app normally works without research model downloads. The optional models
are loaded on first use and reused afterward.

## Generating the page

When the interview is complete, `design_brief()` converts the collected answers
to JSON. `generate_html()` sends that brief to OpenAI and passes the response to
`validate_html()`. The interface saves a new design only after these checks pass.
If generation fails, the previous successful design stays available.

HTML checks are separate from the interface so they can be tested without
launching Streamlit. The checks help reject incomplete or active documents;
downloaded content still needs review before publication.

## Python features used here

- `@dataclass` creates the basic setup for small records such as `Settings`,
  `Step`, and `Interview`.
- `@property` makes a calculated value readable as an attribute, such as
  `interview.complete`.
- `@lru_cache` reuses loaded questions or models instead of loading them again.
- Type hints, such as `text: str`, show what a function expects.
- `try` and `except` let the app display an error without losing a saved design.

## Explaining the project in a presentation

“This project uses Streamlit to guide users through website design questions.
It stores their answers as a structured brief and sends that brief to OpenAI
to generate a static HTML and CSS page. The user can inspect, download, and
refine the result. Optional research classifiers interpret natural-language
answers. The generated forms are interface prototypes.”
