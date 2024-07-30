from st_weaviate_connection import WeaviateConnection, WeaviateFilter
import streamlit as st
import time
import sys
import os
import base64

# Constants
ENV_VARS = ["WEAVIATE_URL", "WEAVIATE_API_KEY", "COHERE_API_KEY"]
NUM_IMAGES_PER_ROW = 5
SEARCH_LIMIT = 10


# Functions
def get_env_vars(env_vars: list) -> dict:
    """Retrieve environment variables
    @parameter env_vars : list - List containing keys of environment variables
    @returns dict - A dictionary of environment variables
    """

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
            if "images" in message:
                for i in range(0, len(message["images"]), NUM_IMAGES_PER_ROW):
                    cols = st.columns(NUM_IMAGES_PER_ROW)
                    for j in range(NUM_IMAGES_PER_ROW):
                        if i + j < len(message["images"]):
                            cols[j].image(message["images"][i + j], width=200)


def base64_to_image(base64_str: str) -> str:
    """Convert base64 string to image
    @parameter base64_str : str - Base64 string
    @returns str - Image URL
    """
    return f"data:image/png;base64,{base64_str}"


# Environment variables
env_vars = get_env_vars(ENV_VARS)
url = env_vars["WEAVIATE_URL"]
api_key = env_vars["WEAVIATE_API_KEY"]
cohere_key = env_vars["COHERE_API_KEY"]

# Check keys
if url == "" or api_key == "" or cohere_key == "":
    st.error(f"Environment variables not set", icon="🚨")
    sys.exit("Environment variables not set")

# Title
st.title("🎥🍿 Movie Magic")

# Connection to Weaviate thorugh Connector
conn = st.connection(
    "weaviate",
    type=WeaviateConnection,
    url=url,
    api_key=api_key,
    additional_headers={"X-Cohere-Api-Key": cohere_key},
)

with st.sidebar:
    st.title("🎥🍿 Movie Magic")
    st.subheader("The RAG Recommender")
    st.markdown(
        """<DESCRIPTION GOES HERE>"""
    )
    st.header("Settings")

# Search Mode descriptions
mode_descriptions = {
    "Keyword": [
        "Keyword search (BM25, in case of Weaviate) ranks documents based on their relevance to a given query, factoring in both the frequency of keywords and the length of the document.",
        0, # alpha value
    ],
    "Semantic": [
        "Semantic (vector) search ranks results based on their similarity to your search query. Instead of just matching keywords, it understands the context and meaning behind your search, offering more relevant and nuanced results.",
        1, # alpha value
    ],
    "Hybrid": [
        "Hybrid search combines vector and BM25 searches to offer best-of-both-worlds search results. It leverages the precision of BM25's keyword-based ranking with vector search's ability to understand context and semantic meaning. Providing results that are both directly relevant to the query and contextually related.",
        0.7, # alpha value
    ],
}

# Information
with st.expander("Built with Weaviate"):
    st.subheader("<TODO>")
    st.markdown(
        """

        """
    )
    st.subheader("Data")
    st.markdown(
        """The database contains over 4000+ movies from TMDB:
        - Name, Type, Keywords
        - Mana cost, Mana produced, Color
        - Power, Toughness, Rarity
        - Set name and Card description """
    )
    st.subheader("How the demo works")


col1, col2, col3 = st.columns([0.2, 0.5, 0.2])

# col2.image("./img/anim.gif")

# User Configuration Sidebar
with st.sidebar:
    mode = st.radio(
        "Search Mode", options=["Keyword", "Semantic", "Hybrid"], index=2
    )
    year_range = st.slider(
        label="Year range",
        min_value=1950,
        max_value=2024,
        value=(1990, 2024),
    )
    st.info(mode_descriptions[mode][0])

    st.success("Connected to Weaviate", icon="💚")

st.divider()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.greetings = False

# Display chat messages from history on app rerun
display_chat_messages()

# Greet user
if not st.session_state.greetings:
    with st.chat_message("assistant"):
        intro = "<GREETINGS>"
        st.markdown(intro)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": intro})
        st.session_state.greetings = True

# Example prompts
example_prompts = [
    "A movie night with friends",
    "Vampires cards with flying ability",
    "Blue and green colored sorcery cards",
    "White card with protection from black",
    "The famous 'Black Lotus' card",
    "Wizard card with Vigiliance ability",
]

example_prompts_help = [
    "Look for a specific card effect",
    "Search for card type: 'Vampires', card color: 'black', and ability: 'flying'",
    "Color cards and card type",
    "Specifc card effect to another mana color",
    "Search for card names",
    "Search for card types with specific abilities",
]

button_cols = st.columns(3)
button_cols_2 = st.columns(3)

button_pressed = ""

if button_cols[0].button(example_prompts[0], help=example_prompts_help[0]):
    button_pressed = example_prompts[0]
elif button_cols[1].button(example_prompts[1], help=example_prompts_help[1]):
    button_pressed = example_prompts[1]
elif button_cols[2].button(example_prompts[2], help=example_prompts_help[2]):
    button_pressed = example_prompts[2]

elif button_cols_2[0].button(example_prompts[3], help=example_prompts_help[3]):
    button_pressed = example_prompts[3]
elif button_cols_2[1].button(example_prompts[4], help=example_prompts_help[4]):
    button_pressed = example_prompts[4]
elif button_cols_2[2].button(example_prompts[5], help=example_prompts_help[5]):
    button_pressed = example_prompts[5]


def clean_input(input_text):
    return input_text.replace('"', "").replace("'", "")


# Create two input boxes
movie_type_raw = st.text_input("What movies are you looking for?")
movie_type = clean_input(movie_type_raw)
viewing_occasion_raw = st.text_input("What occasion is the movie for?")
viewing_occasion = clean_input(viewing_occasion_raw)
viewing_occasion = f"Suggest one to two movies out of the following list, for a {viewing_occasion}. Give a concise yet fun and positive recommendation."

prompt = f"Searching for: {movie_type} for {viewing_occasion}"

# Create a button to submit the inputs
submit_button = st.button("Search")

if submit_button and movie_type and viewing_occasion:
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(movie_type_raw + " for " + viewing_occasion_raw)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    images = []
    if prompt != "":
        query = prompt.strip().lower()

        df, _ = conn.hybrid_search(
            "MovieDemo",
            query=movie_type,
            return_properties=["title", "tagline", "poster"],
            filters=(
                WeaviateFilter.by_property("release_year").greater_or_equal(year_range[0]) &
                WeaviateFilter.by_property("release_year").less_or_equal(year_range[1])
            ),
            limit=SEARCH_LIMIT,
            alpha=mode_descriptions[mode][1],
        )

        with st.chat_message("assistant"):
            response = "Raw search results. Generating recommendation from these: ..."
            for index, row in df.iterrows():
                # Create a new row of columns for every NUM_IMAGES_PER_ROW images
                if index % NUM_IMAGES_PER_ROW == 0:
                    cols = st.columns(NUM_IMAGES_PER_ROW)

                if row["poster"]:
                    # Display image in the column
                    cols[index % NUM_IMAGES_PER_ROW].image(base64_to_image(row["poster"]), width=200)
                    images.append(base64_to_image(row["poster"]))
                else:
                    cols[index % NUM_IMAGES_PER_ROW].write(
                        f"No Image Available for: {row['title']}"
                    )
            st.session_state.messages.append(
                {"role": "assistant", "content": response, "images": images}
            )

        _, rag_response = conn.hybrid_search(
            "MovieDemo",
            query=movie_type,
            return_properties=["title", "tagline", "poster"],
            filters=(
                WeaviateFilter.by_property("release_year").greater_or_equal(year_range[0]) &
                WeaviateFilter.by_property("release_year").less_or_equal(year_range[1])
            ),
            limit=SEARCH_LIMIT,
            alpha=mode_descriptions[mode][1],
            rag_prompt=viewing_occasion,
            rag_properties=["title", "tagline"]
        )

        with st.chat_message("assistant"):
            rec_response = "Recommendation from these search results: ..."
            for index, row in df.iterrows():
                if index == 0:
                    message_placeholder = st.empty()
                    full_response = ""
                    for chunk in rag_response.split():
                        full_response += chunk + " "
                        time.sleep(0.02)
                        # Add a blinking cursor to simulate typing
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                    rec_response += full_response + " "

            st.session_state.messages.append(
                {"role": "assistant", "content": rec_response}
            )
            st.rerun()
