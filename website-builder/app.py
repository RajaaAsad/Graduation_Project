"""Streamlit entry point: python -m streamlit run app.py."""

import streamlit as st

from website_builder.classifiers import AnswerError
from website_builder.config import ASSETS_DIR, Settings, load_settings
from website_builder.generation import generate_html
from website_builder.interview import PAGE_TYPES, Interview


def generate_design(interview: Interview, settings: Settings, edit: str = "") -> bool:
    """Keep the previous artifact if validation or the API request fails."""
    try:
        with st.spinner("Creating your design…"):
            code = generate_html(
                interview.design_brief(),
                settings,
                existing_html=st.session_state.get("generated_html", ""),
                edit=edit,
            )
        st.session_state.generated_html = code
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": "Your design is ready. Download the HTML or request a change below.",
            }
        )
        return True
    except (ValueError, RuntimeError) as exc:
        st.error(str(exc))
    except Exception:
        # API error messages can contain request information. Never render or log them.
        st.error(
            "Generation failed. Check your API credentials, model access, and connection, then retry."
        )
    return False


def show_page_picker() -> None:
    """Display the original eight page buttons in two rows."""
    page_order = ["signin", "event", "contact", "landing", "soon", "blog", "restaurant", "signup"]
    with st.container(key="page-picker"):
        for row_start in (0, 4):
            columns = st.columns(4)
            for column, page_type in zip(
                columns, page_order[row_start : row_start + 4], strict=True
            ):
                with column:
                    if st.button(PAGE_TYPES[page_type], use_container_width=True):
                        interview = Interview(page_type)
                        article = "an" if page_type == "event" else "a"
                        st.session_state.interview = interview
                        st.session_state.generated_html = ""
                        st.session_state.messages = [
                            {
                                "role": "user",
                                "content": f"I’d like to design {article} {PAGE_TYPES[page_type].lower()}.",
                            },
                            {"role": "assistant", "content": interview.current.question},
                        ]
                        st.rerun()


def show_design(interview: Interview, settings: Settings) -> None:
    """Show generation controls and the successful design's download."""
    if not settings.api_key:
        st.info("Add your OpenAI API key to the local .env file to enable generation.")

    code = st.session_state.generated_html
    button_label = "Regenerate design" if code else "Generate design"
    if st.button(button_label, disabled=not settings.api_key):
        if generate_design(interview, settings):
            st.rerun()

    if code:
        st.download_button(
            "Download index.html", data=code, file_name="index.html", mime="text/html"
        )
        with st.expander("Inspect HTML and CSS"):
            st.code(code, language="html")
        st.caption("Review the downloaded design before publishing. Forms are visual prototypes.")


def save_answer(interview: Interview, prompt: str, settings: Settings) -> bool:
    """Save a valid answer and add the next question to the conversation."""
    try:
        interview.answer(prompt, settings)
    except (AnswerError, RuntimeError) as exc:
        st.error(str(exc))
        return False
    except Exception:
        st.error("The research classifier could not load. Check docs/models.md or disable ML mode.")
        return False

    st.session_state.messages.append({"role": "user", "content": prompt})
    if not interview.complete:
        st.session_state.messages.append(
            {"role": "assistant", "content": interview.current.question}
        )
    return True


def main() -> None:
    """Draw the page, then handle one answer or edit request."""
    st.set_page_config(page_title="AI-Powered Website Builder", page_icon="🤖", layout="centered")
    # Only this trusted local stylesheet is inserted as HTML; chat messages stay plain text.
    stylesheet = (ASSETS_DIR / "styles.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{stylesheet}</style>", unsafe_allow_html=True)
    settings = load_settings()
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("generated_html", "")
    interview = st.session_state.get("interview")
    st.title("AI-Powered Website Builder 🤖")
    if interview is None:
        show_page_picker()
        st.chat_input("Choose a page above to begin", disabled=True)
        return

    if st.button("Start a new design"):
        st.session_state.pop("interview", None)
        st.session_state.messages = []
        st.session_state.generated_html = ""
        st.rerun()

    if interview.complete:
        st.success("Your design brief is complete.")
    else:
        st.caption(f"{PAGE_TYPES[interview.page_type]} · Question {interview.index + 1}")
        if interview.current.candidate_labels:
            st.caption("Choices: " + " · ".join(interview.current.candidate_labels))

    for index, message in enumerate(st.session_state.messages):
        avatar = ASSETS_DIR / ("user_icon.svg" if message["role"] == "user" else "ai_icon.svg")
        # The key supplies a CSS class for left/right alignment without inserting user HTML.
        with st.container(key=f"chat-{message['role']}-{index}"):
            with st.chat_message(message["role"], avatar=str(avatar)):
                st.text(message["content"])

    if interview.complete:
        show_design(interview, settings)

    prompt = st.chat_input(
        "Request a design change" if interview.complete else "Write your answer here…",
        disabled=interview.complete and not bool(st.session_state.generated_html),
    )
    if not prompt:
        return

    if interview.complete:
        st.session_state.messages.append({"role": "user", "content": prompt})
        successful = generate_design(interview, settings, edit=prompt)
    else:
        successful = save_answer(interview, prompt, settings)
    if successful:
        st.rerun()


if __name__ == "__main__":
    main()
