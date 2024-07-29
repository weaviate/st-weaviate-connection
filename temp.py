from st_weaviate_connection import WeaviateConnection
import streamlit as st
import os

openai_apikey = os.environ["OPENAI_API_KEY"]

conn = st.connection(
    "weaviate",
    type=WeaviateConnection,
    url=os.getenv("WEAVIATE_URL"),
    api_key=os.getenv("WEAVIATE_API_KEY"),
    additional_headers={"X-OpenAI-Api-Key": openai_apikey},
)

df = conn.hybrid_query(collection_name="Movie", query="Superhero")

print(df)

df = conn.near_text_query(collection_name="Movie", query="romanzzz filmstuff")

print(df)

df = conn.graphql_query(
    """
{
  Get {
    Movie (
        limit: 10
      nearText: {
        concepts: ["historical period film"]
      }
    ) {
      title
      overview
      vote_average
    }
  }
}
"""
)

print(df)

conn.close()
