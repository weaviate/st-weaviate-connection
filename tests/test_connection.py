import pandas as pd
import pytest
from .conftest import TEST_COLLECTION_NAME

from st_weaviate_connection import WeaviateConnection
from st_weaviate_connection.connection import weaviate_response_objects_to_df


@pytest.fixture
def weaviate_connection(weaviate_db):
    yield WeaviateConnection("test_weaviate_conn", url="localhost")


def test_query(weaviate_connection):
    df = weaviate_connection.query(
        query=None,
        collection_name=TEST_COLLECTION_NAME,
        return_properties=["title"],
        alpha=0
    )
    assert df.shape == (5, 1)
    assert set(df["title"]) == {
        "Animaniacs",
        "Rugrats",
        "Doug",
        "Hey Arnold!",
        "The Ren & Stimpy Show",
    }


def test_gql_query(weaviate_connection):
    query = """
    {
        Get {
            TEST_COLLECTION_NAME {
                title
            }
        }
    }
    """
    query = query.replace("TEST_COLLECTION_NAME", TEST_COLLECTION_NAME)

    df = weaviate_connection.graphql_query(query)
    assert df.shape == (5, 1)
    assert set(df["title"]) == {
        "Animaniacs",
        "Rugrats",
        "Doug",
        "Hey Arnold!",
        "The Ren & Stimpy Show",
    }


def test_malformed_query(weaviate_connection):
    query = """
    {
        Foo
    }
    """
    with pytest.raises(Exception) as exc_info:
        weaviate_connection.graphql_query(query)

    assert "The GraphQL query returned an error" in str(exc_info.value)


def test_query_with_additional_properties(weaviate_connection):
    query = """
    {
    Get {
        TEST_COLLECTION_NAME (limit: 3, bm25: {query: "Rugrats"}) {
        title
        creator
        _additional {
            score
            vector
        }
        }
    }
    }
    """
    query = query.replace("TEST_COLLECTION_NAME", TEST_COLLECTION_NAME)

    df = weaviate_connection.graphql_query(query)
    assert df.shape == (1, 4)
    assert set(df.columns) == {
        "title",
        "creator",
        "_additional.score",
        "_additional.vector",
    }
    assert set(df["title"]) == {"Rugrats"}


def test_query_builder(weaviate_connection):
    animaniacs_query_vector = [0.1, 0.2, 0.3, 0.4, 0.5]

    client = weaviate_connection.client()
    c = client.collections.get(TEST_COLLECTION_NAME)

    response = c.query.near_vector(
        near_vector=animaniacs_query_vector,
        limit=3
    )

    df = weaviate_response_objects_to_df(response.objects)

    assert df.shape == (3, 3)
    assert set(df.columns) == {"title", "creator", "_additional.distance"}
    assert df.iloc[0]["title"] == "Animaniacs"
