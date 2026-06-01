import streamlit as st

from chat import ask_question
from document_store import PAGES

from streamlit_pdf_viewer import pdf_viewer

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="PDF RAG Assistant",
    page_icon="📄",
    layout="wide"
)

# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown("""
<style>

.block-container{
    padding-top:1rem;
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# SESSION STATE
# ==================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_page" not in st.session_state:
    st.session_state.selected_page = 1

if "last_source_pages" not in st.session_state:
    st.session_state.last_source_pages = []

# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.title("📄 PDF RAG Assistant")

    st.markdown("""
### Features

- Semantic Search
- Source Navigation
- PDF Viewer
- Conversational Memory
""")

    st.divider()

    selected_page = st.selectbox(
        "Go To Page",
        range(1, len(PAGES) + 1),
        index=st.session_state.selected_page - 1
    )

    if selected_page != st.session_state.selected_page:

        st.session_state.selected_page = selected_page

        st.rerun()

    st.divider()

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.session_state.last_source_pages = []

        st.rerun()

# ==================================================
# HEADER
# ==================================================

st.title("📄 PDF RAG Assistant")

st.caption(
    "Ask questions about your PDF using Gemini + Qdrant"
)

# ==================================================
# MAIN LAYOUT
# ==================================================

left_col, right_col = st.columns(
    [3, 2]
)

# ==================================================
# PDF PANEL
# ==================================================

with left_col:

    st.subheader(
        f"📄 Page {st.session_state.selected_page}"
    )

    st.caption(
        f"Page {st.session_state.selected_page} of {len(PAGES)}"
    )

    nav_left, nav_right = st.columns(2)

    with nav_left:

        if st.button(
            "⬅ Previous",
            use_container_width=True
        ):

            if st.session_state.selected_page > 1:

                st.session_state.selected_page -= 1

                st.rerun()

    with nav_right:

        if st.button(
            "Next ➡",
            use_container_width=True
        ):

            if (
                st.session_state.selected_page
                < len(PAGES)
            ):

                st.session_state.selected_page += 1

                st.rerun()

    try:

        pdf_viewer(
            "nodejs.pdf",
            pages_to_render=[
                st.session_state.selected_page
            ],
            width="100%"
        )

    except Exception as e:

        st.error(
            f"PDF Viewer Error: {e}"
        )

    with st.expander(
        "📖 Current Page Content",
        expanded=False
    ):

        st.markdown(
            PAGES[
                st.session_state.selected_page - 1
            ].page_content
        )

# ==================================================
# CHAT PANEL
# ==================================================

with right_col:

    st.subheader("💬 Chat")

    for msg_idx, message in enumerate(
    st.session_state.messages
):

            with st.chat_message(
                message["role"]
            ):

                st.markdown(
                    message["content"]
                )

                if (
                    message["role"] == "assistant"
                    and "sources" in message
                ):

                    st.markdown(
                        "#### 📚 Sources"
                    )

                    source_pages = (
                        message["sources"]
                    )

                    cols = st.columns(
                        min(
                            len(source_pages),
                            4
                        )
                    )

                    for idx, page in enumerate(
                        source_pages
                    ):

                        with cols[
                            idx % len(cols)
                        ]:

                            if st.button(
                                f"📄 Page {page}",
                                key=f"src_{msg_idx}_{page}",
                                use_container_width=True
                            ):

                                st.session_state.selected_page = page

                                st.rerun()

    # ==================================================
    # LATEST SOURCES
    # ==================================================

    if st.session_state.last_source_pages:

        with st.expander(
            "📌 Latest Sources",
            expanded=False
        ):

            cols = st.columns(
                min(
                    len(
                        st.session_state.last_source_pages
                    ),
                    4
                )
            )

            for idx, page in enumerate(
                st.session_state.last_source_pages
            ):

                with cols[
                    idx % len(cols)
                ]:

                    if st.button(
                        f"📄 Page {page}",
                        key=f"latest_{page}",
                        use_container_width=True
                    ):

                        st.session_state.selected_page = page

                        st.rerun()

    # ==================================================
    # CHAT INPUT
    # ==================================================

    prompt = st.chat_input(
        "Ask a question about the PDF..."
    )

    if prompt:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        try:

            with st.spinner(
                "Searching document..."
            ):

                answer, docs = ask_question(
                    prompt,
                    st.session_state.messages[-10:]
                )

            source_pages = sorted(
                {
                    doc.metadata.get(
                        "page",
                        0
                    ) + 1
                    for doc in docs
                }
            )

            st.session_state.last_source_pages = (
                source_pages
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "sources": source_pages
                }
            )

            st.rerun()

        except Exception as e:

            st.error(
                f"Error: {str(e)}"
            )