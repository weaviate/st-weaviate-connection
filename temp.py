from st_weaviate_connection import WeaviateConnection, WeaviateFilter
import streamlit as st
import os

openai_apikey = os.environ["OPENAI_API_KEY"]
weaviate_url = os.environ["WEAVIATE_URL"]
weaviate_apikey = os.environ["WEAVIATE_API_KEY"]

conn = st.connection(
    "weaviate",
    type=WeaviateConnection,
    url=weaviate_url,
    api_key=weaviate_apikey,
    additional_headers={"X-OpenAI-Api-Key": openai_apikey},
)

df = conn.hybrid_search(collection_name="Movie", query="Superhero")

print(df)

df = conn.near_text_search(collection_name="Movie", query="romanzzz filmstuff")

print(df)

df = conn.hybrid_search(
    collection_name="Movie",
    query="Superhero",
    filters=WeaviateFilter.by_property("vote_average").greater_than(8)
)

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
