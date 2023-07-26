import pandas as pd
import pytest

from st_weaviate_connection import WeaviateConnection


@pytest.fixture
def weaviate_connection(weaviate_db):
    yield WeaviateConnection("test_weaviate_conn", url="http://localhost:8080")


def test_query(weaviate_connection):
    query = """
    {
        Get {
            TVShow {
                title
            }
        }
    }
    """
    df = weaviate_connection.query(query)
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
        weaviate_connection.query(query)

    assert "The GraphQL query returned an error" in str(exc_info.value)


def test_query_with_additional_properties(weaviate_connection):
    query = """
    {
    Get {
        TVShow(limit: 3, bm25: {query: "Rugrats"}) {
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
    df = weaviate_connection.query(query)
    assert df.shape == (1, 4)
    assert set(df.columns) == {
        "title",
        "creator",
        "_additional.score",
        "_additional.vector",
    }
    assert set(df["title"]) == {"Rugrats"}


def test_query_builder(weaviate_connection):
    client = weaviate_connection.client()
    animaniacs_query_vector = [0.1, 0.2, 0.3, 0.4, 0.5]
    results = (
        client.query.get("TVShow", ["title", "creator"])
        .with_limit(3)
        .with_additional("distance")
        .with_near_vector(
            {
                "vector": animaniacs_query_vector,
            }
        )
        .do()
    )

    df = pd.json_normalize(results["data"]["Get"]["TVShow"])

    assert df.shape == (3, 3)
    assert set(df.columns) == {"title", "creator", "_additional.distance"}
    assert df.iloc[0]["title"] == "Animaniacs"
