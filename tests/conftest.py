import pytest
import requests
from weaviate import WeaviateClient

TEST_COLLECTION_NAME = "TVShow"


def is_ready(url):
    """Check if the service is ready"""
    try:
        response = requests.get(url)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False


@pytest.fixture(scope="session")
def weaviate_service(docker_ip, docker_services):
    port = docker_services.port_for("weaviate", 8080)
    url = f"http://{docker_ip}:{port}"
    ready_endpoint = f"{url}/v1/.well-known/ready"

    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: is_ready(ready_endpoint)
    )
    return url


@pytest.fixture(scope="session")
def weaviate_client(weaviate_service):
    import weaviate

    client = weaviate.connect_to_local()
    yield client


@pytest.fixture(scope="session")
def documents():
    yield [
        {
            "title": "Animaniacs",
            "creator": "Tom Ruegger",
            "synopsis": "The wacky adventures of three zany siblings who wreak havoc on the Warner Bros. studio lot.",
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
        },
        {
            "title": "Rugrats",
            "creator": "Arlene Klasky and Gábor Csupó",
            "synopsis": "The imaginative adventures of a group of toddlers and their baby brother, as seen through their eyes.",
            "embedding": [0.5, 0.4, 0.3, 0.2, 0.1],
        },
        {
            "title": "Doug",
            "creator": "Jim Jinkins",
            "synopsis": "The everyday life of a shy and imaginative 11-year-old boy named Doug Funnie.",
            "embedding": [0.2, 0.3, 0.4, 0.5, 0.6],
        },
        {
            "title": "Hey Arnold!",
            "creator": "Craig Bartlett",
            "synopsis": "The life of a fourth-grader named Arnold, who lives with his grandparents in a boarding house.",
            "embedding": [0.6, 0.5, 0.4, 0.3, 0.2],
        },
        {
            "title": "The Ren & Stimpy Show",
            "creator": "John Kricfalusi",
            "synopsis": "The bizarre and often gross misadventures of a chihuahua and a cat.",
            "embedding": [0.3, 0.4, 0.5, 0.6, 0.7],
        },
    ]


@pytest.fixture(scope="session")
def weaviate_db(weaviate_client: WeaviateClient, documents):
    from weaviate.classes.config import Configure, Property, DataType

    weaviate_client.collections.delete(TEST_COLLECTION_NAME)
    c = weaviate_client.collections.create(
        name=TEST_COLLECTION_NAME,
        vectorizer_config=Configure.Vectorizer.none(),
        properties=[
            Property(name="title", data_type=DataType.TEXT),
            Property(name="creator", data_type=DataType.TEXT),
            Property(name="synopsis", data_type=DataType.TEXT),
        ]
    )
    with c.batch.fixed_size(100) as batch:
        for document in documents:
            embedding = document.pop("embedding")
            batch.add_object(
                properties=document, vector=embedding
            )
