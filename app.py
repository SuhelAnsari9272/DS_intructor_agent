import json
from typing import Any

import streamlit as st

from src.graph import create_workflow_graph
from utils.utils import save_graph


# -----------------------------------------------------------------------------
# Page Configuration
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="DS Instructor Agent",
    page_icon="🧠",
    layout="wide",
)


# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------

def init_session_state():
    st.session_state.setdefault("chat_history", [])
    st.session_state.setdefault("router_info", None)


# -----------------------------------------------------------------------------
# Load LangGraph (Only Once)
# -----------------------------------------------------------------------------

@st.cache_resource
def get_instructor():
    """
    Compile the LangGraph once per Streamlit server.
    """
    graph = create_workflow_graph()
    instructor = graph.compile()

    # Optional
    try:
        save_graph(instructor)
    except Exception:
        pass

    return instructor


# -----------------------------------------------------------------------------
# Utility Functions
# -----------------------------------------------------------------------------

def extract_text(value: Any) -> str:
    """
    Extract the assistant response from different possible return types.
    """

    if value is None:
        return ""

    if isinstance(value, str):
        return value

    if hasattr(value, "answer"):
        return str(value.answer)

    if hasattr(value, "content"):
        return str(value.content)

    if isinstance(value, dict):

        if "final_response" in value:
            return extract_text(value["final_response"])

        if "answer" in value:
            return str(value["answer"])

        if "content" in value:
            return str(value["content"])

        return json.dumps(value, indent=2)

    if hasattr(value, "dict"):
        data = value.dict()
        return extract_text(data)

    return str(value)


def extract_router_info(state: Any):
    """
    Extract router information for displaying in sidebar.
    """

    if not isinstance(state, dict):
        return None

    routes = state.get("routes")

    if routes is None:
        return None

    if hasattr(routes, "dict"):
        return routes.dict()

    if isinstance(routes, dict):
        return routes

    return {"routes": str(routes)}


def extract_final_response(result: Any):
    """
    Extract the complete SynthesizedOutput.
    """

    if not isinstance(result, dict):
        return None

    response = result.get("final_response")

    if response is None:
        return None

    if hasattr(response, "model_dump"):      # Pydantic v2
        print(response.model_dump())
        print(type(response.model_dump()))
        return response.model_dump()

    if hasattr(response, "dict"):
        print(response.dict())           # Pydantic v1
        print(type(response.dict()))
        return response.dict()

    if isinstance(response, dict):
        print(response)
        return response

    return None


def render_response(response):

    st.markdown(response["answer"])

    with st.expander("📚 Topics Covered"):
        for topic in response["topics_covered"]:
            st.write("•", topic)

    with st.expander("✅ Key Takeaways"):
        for takeaway in response["key_takeaways"]:
            st.write("•", takeaway)

    with st.expander("🚀 Recommended Next Topics"):
        for topic in response["recommended_next_topics"]:
            st.write("•", topic)


# -----------------------------------------------------------------------------
# Initialize
# -----------------------------------------------------------------------------

init_session_state()

instructor = get_instructor()

# -----------------------------------------------------------------------------
# Title
# -----------------------------------------------------------------------------

st.title("🧠 DS Instructor Agent")

st.markdown(
    """
A graph-based multi-agent Data Science Instructor built using **LangGraph**.
"""
)

# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------

with st.sidebar:

    st.header("Session Information")

    st.write(f"Messages : {len(st.session_state['chat_history'])}")

    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.session_state.router_info = None
        st.rerun()

    if st.session_state["router_info"] is not None:

        with st.expander("Router Decision", expanded=False):
            st.json(st.session_state["router_info"])


# -----------------------------------------------------------------------------
# Display Chat History
# -----------------------------------------------------------------------------

for message in st.session_state["chat_history"]:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# -----------------------------------------------------------------------------
# Chat Input
# -----------------------------------------------------------------------------

prompt = st.chat_input("Ask a Data Science question...")

if prompt:

    # Display user message immediately
    st.session_state["chat_history"].append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                result = instructor.invoke({ "query": prompt })

                final_response = extract_final_response(result)
                # final_response =  result['final_response']

                # answer = extract_text(result)

                router_info = extract_router_info(result)

                answer = final_response['answer']

                render_response(final_response)

                # answer = final_response["answer"]

                # st.markdown(answer)

                # with st.expander("📚 Topics Covered"):

                #     for topic in final_response["topics_covered"]:
                #         st.write("•", topic)

                # with st.expander("✅ Key Takeaways"):

                #     for takeaway in final_response["key_takeaways"]:
                #         st.write("•", takeaway)

                # with st.expander("🚀 Recommended Next Topics"):

                #     for topic in final_response["recommended_next_topics"]:
                #         st.write("•", topic)

                # st.markdown(answer)

                st.session_state["chat_history"].append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

                st.session_state["router_info"] = router_info

            except Exception as e:

                error_msg = f"❌ Error while generating response:\n\n{str(e)}"

                st.error(error_msg)

                st.session_state["chat_history"].append(
                    {
                        "role": "assistant",
                        "content": error_msg,
                    }
                )

    # st.rerun()