# Streamlit-Weaviate Connection

[![Weaviate](https://img.shields.io/static/v1?label=Built%20with&message=Weaviate&color=green&style=flat-square)](https://weaviate.io/) [![Weaviate](https://img.shields.io/static/v1?label=%20made%20with%20%E2%9D%A4%20for&message=Streamlit&color=red&style=flat-square)](https://streamlit.io/)

This project provides a Streamlit connector for the open-source vector database, [Weaviate](https://weaviate.io/).

## Overview

The Streamlit-Weaviate Connector enables developers to connect to a Weaviate database with the following Python code:

 ```python
    conn = st.connection(
        "weaviate",
        type=WeaviateConnection,
        url=os.getenv("WEAVIATE_URL"),
        api_key=os.getenv("WEAVIATE_API_KEY"),
    )
 ```

## Features

- Hybrid search functionality
- GraphQL query support
- Advanced operations using the Weaviate Python client
- Secrets management for secure connections

## 🔧 Installation

This project uses [`poetry`](https://python-poetry.org/docs/dependency-specification/) for dependency management. To install:

1. Ensure you have Python >=3.11.0 installed
2. Install poetry: `pip install poetry`
3. Install the project: `poetry add git+https://github.com/weaviate/st-weaviate-connection.git`

## Usage

Check out the [demo notebook](./notebooks/01_demo.ipynb) for basic usage examples.

Before running, set these environment variables:
```
WEAVIATE_URL=YOUR_WEAVIATE_CLUSTER_URL
WEAVIATE_API_KEY=YOUR_WEAVIATE_API_KEY
```

## 🔗 Basic Usage

### Connecting to a Weaviate Cloud instance

To connect to a Weaviate Cloud instance, use the following code:

```python
conn = st.connection(
    "weaviate",
    type=WeaviateConnection,
    url=weaviate_url,
    api_key=weaviate_apikey,
    additional_headers={"X-OpenAI-Api-Key": openai_apikey},
)
```

Where `weaviate_url` and `weaviate_apikey` are the URL and API key of your Weaviate Cloud instance, respectively.

### Queries

You can use the `hybrid_search` method or `graphql_query` method to query your Weaviate instance.

To perform a hybrid search, use the following method:

```python
df = conn.hybrid_search(
    collection_name="<COLLECTION NAME>",
    query="<QUERY STRING>",
)
```

To perform a GraphQL `GET` query, use the following method:

```python
df = conn.graphql_query(
    """
    {
        Get {
            <YOUR QUERY GOES HERE>
        }
    }
    """
)
```

Both methods return a Pandas DataFrame.

#### `hybrid_search` method

The `hybrid_search` method is a convenience method that was created for the Weaviate connector.

It performs a hybrid search on the Weaviate instance. The method requires `collection_name` and `query` as arguments.

- `collection_name` : str
    - The name of the collection to query.
- `query` : str
    - The query to search for.

It also accepts `limit`, `filters`, `target_vectors`, `query_properties`, and `alpha` as optional arguments.

## Advanced Usage

The Weaviate connector uses the Weaviate Python client under-the-hood to interact with the Weaviate instance.

Accordingly, you can use the Weaviate client object directly to perform advanced operations.

We recommend using the following syntax:

```python
with conn.client() as client:
    # Use the client object to perform required operations
    # e.g. 1: Create a collection
    # client.collections.create(...)
    #
    # e.g. 2: Perform retrieval augmented generation & print the generated recommendation
    # collection = client.collections.get(...)
    # response = collection.generate.hybrid(
    #     limit=4,
    #     query="a sweet european red wine",
    #     grouped_task="From these, recommend a wine that would pair well with a steak",
    # )
    #
    # print("## Generated recommendation")
    # print(response.generated)
    ...
```

This way, the client will also automatically close the connection after the block is executed, ensuring that there are no resource leaks.

See the [Weaviate Python client documentation](https://weaviate.io/developers/weaviate/client-libraries/python), and the [Weaviate documentation](https://weaviate.io/developers/weaviate/) for more information on the available operations.

## Example notebook

The project includes a demonstration notebook to showcase basic functionalities of the connector (see here [demo notebook](./notebooks/01_demo.ipynb))

Before you run the Jupyter notebook make sure that you have set the following environment variables

**Set environment variables:**
```
WEAVIATE_URL=<YOUR WEAVIATE CLOUD INSTANCE URL>
WEAVIATE_API_KEY=<YOUR WEAVIATE CLOUD INSTANCE API KEY>
```

## 📚 Documentation

All connector functionality can be found in the [`connection.py`](./st_weaviate_connection/connection.py) python file. Documentation about `st.connection` can be found [here](https://docs.streamlit.io/library/api-reference/connections/st.experimental_connection).

## Demo app(s)

### Movie Magic

*🎬🍿 Movie Magic* is a simple, but fun movie recommendation app built with Streamlit and Weaviate, using `st-weaviate-connection` Weaviate connector.

The app allows users to search for movies based on search terms using hybrid, semantic, and keyword search options. Then, the app provides recommendations based on the viewing occasion.

Run the app using the following command:

```bash
streamlit run demo_app.py
```

### Magic Chat

*🔮 Magic Chat* searches through Magic The Gathering cards with various search options, such as keyword, semantic and hybrid, and performs retrieval-augmented. The live demo is accessible through [Streamlit Community Cloud](https://weaviate-magic-chat.streamlit.app/).

It was built using a previous version (0.0.1) of the Weaviate connector, and the code can be found in the [this repository](https://github.com/thomashacker/weaviate-magic-chat-demo/tree/main).

## 💖 Open Source Contribution

Now, you're all set to use the Weaviate Connector for Streamlit. Happy coding!

We encourage contributions. Feel free to suggest improvements, provide feedback, create issues, and submit bug reports!
