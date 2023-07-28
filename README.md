# Streamlit-Weaviate Connection

[![Weaviate](https://img.shields.io/static/v1?label=Built%20with&message=Weaviate&color=green&style=flat-square)](https://weaviate.io/) [![Weaviate](https://img.shields.io/static/v1?label=%20made%20with%20%E2%9D%A4%20for&message=Streamlit&color=red&style=flat-square)](https://weaviate.io/)

This project is a submission for the [Streamlit Connections Hackathon 2023](https://discuss.streamlit.io/t/connections-hackathon/47574).
It delivers a Streamlit connector for the open-source vector database, [Weaviate](https://weaviate.io/).

## Overview

The Streamlit-Weaviate Connector enables developers to connect to a Weaviate database with the following Python code:

 ```python 
    conn = st.experimental_connection(
        "weaviate",
        type=WeaviateConnection,
        url=os.getenv("WEAVIATE_URL"),
        api_key=os.getenv("WEAVIATE_API_KEY"),
    )
 ```

This project also includes a Streamlit demo, "Magic Chat", designed to search through [Magic The Gathering](https://magic.wizards.com/en) cards with various search options, such as BM25, Semantic Search, Hybrid Search and Generative Search. The live demo is accessible through [Streamlit Community Cloud](https://streamlit.io/cloud)

![Screenshot of the demo](https://github.com/weaviate/st-weaviate-connection/blob/main/img/screenshot.jpeg)

# 📚 Quickstart Guide
## 🔧 Installation

This project uses `poetry` for dependency management. You can find more details more `poetry` in [its documentation](https://python-poetry.org/docs/dependency-specification/).

1. **Create a new Python virtual environment:**
- Ensure you have python `>=3.10.0` installed
- ```python3 -m venv env```
- ```source env/bin/activate```
- ```pip install poetry```

2. **Install the project:**
- Install the project using poetry
-  ```bash 
        poetry add git+https://github.com/weaviate/st-weaviate-connection.git
    ```

## 🔗 Basic Usage

The project includes a demonstration notebook to showcase basic functionalities of the connector (see here [demo notebook](./notebooks/01_demo.ipynb)) and a [streamlit app](./streamlit_app.py) illustrating the implementation and usage of the connector.

Before you run the Jupyter notebook or the Streamlit app, create a `.env` file in the root directory of the project and add your Weaviate cluster and OpenAI API credentials:

**Set environment variables:**
```
WEAVIATE_URL= YOUR WEAVIATE_CLUSTER_URL
WEAVIATE_API_KEY= YOUR WEAVIATE_API_KEY
OPENAI_API_KEY= (ONLY NEEDED FOR STREAMLIT APP)
```

To set up your Weaviate cluster, follow either of these methods:

- **OPTION 1** Create a cluster in WCS (for more details, refer to the [Weaviate Cluster Setup Guide](https://weaviate.io/developers/wcs/guides/create-instance))
- **OPTION 2** Use Docker-Compose to setup a cluster locally [Weaviate Docker Guide](https://weaviate.io/developers/weaviate/installation/docker-compose)


All connector functionality can be found in the [`connection.py`](./st_weaviate_connection/connection.py) python file. Documentation about `st.experimental_connection` can be found [here](https://docs.streamlit.io/library/api-reference/connections/st.experimental_connection).


## ✨ Streamlit

You can start the Streamlit app with the following command:

```python
streamlit run streamlit_app.py
```

## 📦 Data Management

To use the demo locally, you need to import Magic card data into your Weaviate cluster. Inside the [data](./data/) directory, we provide three scripts.

- `add_card_schema.py` Adds a card schema to your Weaviate cluster.
- `delete_card_schema.py` Deletes the card schema and all saved objects.
- `retrieve_magic_cards.py` Uses the [Scryfall API](https://scryfall.com/) to retrieve card information and saves them to your cluster.


## 💖 Open Source Contribution

Now, you're all set to use the Weaviate Connector for Streamlit. Happy coding!

We encourage open-source contributions. Feel free to suggest improvements, provide feedback, create issues, and submit bug reports!