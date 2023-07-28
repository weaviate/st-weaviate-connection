from st_weaviate_connection import WeaviateConnection
import streamlit as st
import time
import sys
import os

from dotenv import load_dotenv

# Constants
ENV_VARS = ["WEAVIATE_URL", "WEAVIATE_API_KEY", "OPENAI_API_KEY"]
NUM_IMAGES_PER_ROW = 3


# Functions
def get_env_vars(env_vars: list) -> dict:
    """Retrieve environment variables
    @parameter env_vars : list - List containing keys of environment variables
    @returns dict - A dictionary of environment variables
    """
    load_dotenv()

    env_vars = {}
    for var in ENV_VARS:
        value = os.environ.get(var, "")
        if value == "":
            st.error(f"{var} not set", icon="🚨")
            sys.exit(f"{var} not set")
        env_vars[var] = value

    return env_vars


def display_chat_messages() -> None:
    """Print message history
    @returns None
    """
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# Environment variables
env_vars = get_env_vars(ENV_VARS)
url = env_vars["WEAVIATE_URL"]
api_key = env_vars["WEAVIATE_API_KEY"]
openai_key = env_vars["OPENAI_API_KEY"]

# Check keys
if url == "" or api_key == "" or openai_key == "":
    st.error(f"Environment variables not set", icon="🚨")
    sys.exit("Environment variables not set")

# Title
st.title("🔮 Magic Chat")
st.subheader("The Generative Gathering")
st.write(
    "Chat with Magic Chat that utilizes traditional BM25, Semantic, Hybrid, and Generative Search to build your dream deck for Magic The Gathering."
)

# Connection to Weaviate thorugh Connector
conn = st.experimental_connection(
    "weaviate",
    type=WeaviateConnection,
    url=os.getenv("WEAVIATE_URL"),
    api_key=os.getenv("WEAVIATE_API_KEY"),
    additional_headers={"X-OpenAI-Api-Key": openai_key},
)

st.success("Connected to Weaviate client", icon="💚")

# Search Mode descriptions

bm25_gql = """
        {{
            Get {{
                Card(limit: {limit_card}, bm25: {{ query: "{input}" }}) 
                {{
                    name
                    card_id
                    img
                    mana_cost
                    type
                    mana_produced
                    power
                    toughness
                    color
                    keyword
                    set
                    rarity
                    description
                    _additional {{
                        id
                        distance
                        vector
                    }}
                }}
            }}
        }}"""

vector_gql = """
        {{
            Get {{
                Card(limit: {limit_card}, nearText: {{ concepts: ["{input}"] }}) 
                {{
                    name
                    card_id
                    img
                    mana_cost
                    type
                    mana_produced
                    power
                    toughness
                    color
                    keyword
                    set
                    rarity
                    description
                    _additional {{
                        id
                        distance
                        vector
                    }}
                }}
            }}
        }}"""

hybrid_gql = """
        {{
            Get {{
                Card(limit: {limit_card}, hybrid: {{ query: "{input}" alpha:0.5 }}) 
                {{
                    name
                    card_id
                    img
                    mana_cost
                    type
                    mana_produced
                    power
                    toughness
                    color
                    keyword
                    set
                    rarity
                    description
                    _additional {{
                        id
                        distance
                        vector
                    }}
                }}
            }}
        }}"""

generative_gql = """
        {{
            Get {{
                Card(limit: {limit_card}, hybrid: {{ query: "{input}" alpha:0.5 }}) 
                {{
                    name
                    card_id
                    img
                    mana_cost
                    type
                    mana_produced
                    power
                    toughness
                    color
                    keyword
                    set
                    rarity
                    description
                    _additional {{
                        generate(
                            groupedResult: {{
                                task: "Based on the Magic The Gathering Cards, which one would you recommend and why. Use the context of the user query: {input}"
                            }}
                        ) {{
                        groupedResult
                        error
                        }}
                        id
                        distance
                        vector
                    }}
                }}
            }}
        }}"""

mode_descriptions = {
    "BM25": [
        "BM25 is a method used by search engines to rank documents based on their relevance to a given query, factoring in both the frequency of keywords and the length of the document.",
        bm25_gql,
    ],
    "Vector": [
        "Vector search is a method used by search engines to find and rank results based on their similarity to your search query. Instead of just matching keywords, it understands the context and meaning behind your search, offering more relevant and nuanced results.",
        vector_gql,
    ],
    "Hybrid": [
        "Hybrid search combines vector and BM25 methods to offer better search results. It leverages the precision of BM25's keyword-based ranking with vector search's ability to understand context and semantic meaning. Providing results that are both directly relevant to the query and contextually related.",
        hybrid_gql,
    ],
    "Generative": [
        "Generative search is an advanced method that combines information retrieval with AI language models. After finding relevant documents using search techniques like vector and BM25, the found information is used as an input to a language model, which generates further contextually related information.",
        generative_gql,
    ],
}

# Information
with st.expander("Build with Weaviate for the Streamlit Hackathon 2023"):
    st.write(
        """This demo was built for the Streamlit Hackathon in which it was required to create a database connection integration into Streamlit's ExperimentalBaseConnection. This demo showcases the Weaviate Connector which connects to a Weaviate Cluster to retrieve data about Magic the Gathering cards. You can learn more about weaviate here https://weaviate.io/"""
    )

# User Configuration
desc_col, mode_col = st.columns([0.8, 0.2])
mode = mode_col.radio(
    "Search Mode", options=["BM25", "Vector", "Hybrid", "Generative"], index=3
)
desc_col.info(mode_descriptions[mode][0])
limit = st.slider(label="Number of cards", min_value=1, max_value=12, value=6)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.greetings = False

# Display chat messages from history on app rerun
display_chat_messages()

# Greet user
if not st.session_state.greetings:
    with st.chat_message("assistant"):
        intro = "Hey! I am Magic Chat, your assistant for finding the best Magic The Gathering cards to build your dream deck. Let's get started!"
        st.markdown(intro)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": intro})
        st.session_state.greetings = True

# Wait for prompt
if prompt := st.chat_input("What cards are you looking for?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    if prompt != "":
        query = prompt.strip().lower()
        gql = mode_descriptions[mode][1].format(input=query, limit_card=limit)

        df = conn.query(gql)

        response = ""
        with st.chat_message("assistant"):
            for index, row in df.iterrows():
                if index == 0:
                    if "_additional.generate.groupedResult" in row:
                        first_response = row["_additional.generate.groupedResult"]
                    else:
                        first_response = f"Here are the results from the {mode} search:"

                    message_placeholder = st.empty()
                    full_response = ""
                    for chunk in first_response.split():
                        full_response += chunk + " "
                        time.sleep(0.05)
                        # Add a blinking cursor to simulate typing
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                    response += full_response + " "

                # Create a new row of columns for every NUM_IMAGES_PER_ROW images
                if index % NUM_IMAGES_PER_ROW == 0:
                    cols = st.columns(NUM_IMAGES_PER_ROW)

                if row["img"]:
                    # Display image in the column
                    cols[index % NUM_IMAGES_PER_ROW].image(row["img"], width=200)

            st.session_state.messages.append({"role": "assistant", "content": response})
