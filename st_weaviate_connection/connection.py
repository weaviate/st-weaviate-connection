from typing import Optional

import pandas as pd
import weaviate
from streamlit.connections import BaseConnection
from streamlit.runtime.caching import cache_data
from weaviate.client import WeaviateClient
from weaviate.collections.classes.internal import _RawGQLReturn


class WeaviateConnection(BaseConnection["WeaviateClient"]):
    def __init__(
        self,
        connection_name: str,
        url=None,
        api_key=None,
        additional_headers=None,
        **kwargs,
    ) -> None:
        self.url = url
        self.api_key = api_key
        self.additional_headers = additional_headers
        super().__init__(connection_name, **kwargs)

    def _connect(self, **kwargs) -> WeaviateClient:
        auth_config = self._create_auth_config()
        url = self.url or self._secrets.get("WEAVIATE_URL")
        return weaviate.connect_to_weaviate_cloud(
            cluster_url=url,
            auth_credentials=auth_config,
            headers=self.additional_headers,
        )

    def _create_auth_config(self) -> Optional[weaviate.AuthApiKey]:
        api_key = self.api_key or self._secrets.get("WEAVIATE_API_KEY")
        if api_key is not None:
            return weaviate.AuthApiKey(api_key=api_key)
        else:
            return None

    def _convert_to_dataframe(self, results: _RawGQLReturn) -> pd.DataFrame:
        class_name = list(results.get.keys())[0]
        data = results.get[class_name]
        df = pd.json_normalize(data)
        return df

    def query(self, query: str, ttl: int = 3600) -> pd.DataFrame:
        @cache_data(ttl=ttl)
        def _query(query: str):
            results = self._connect().graphql_raw_query(query)
            if "errors" in results:
                error_message = (
                    f"The GraphQL query returned an error: {results['errors']}"
                )
                raise Exception(error_message)
            else:
                return results

        results = _query(query)

        return self._convert_to_dataframe(results)

    def client(self) -> WeaviateClient:
        return self._connect()
