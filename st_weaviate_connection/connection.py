from typing import Optional

import pandas as pd
import weaviate
from streamlit.connections import BaseConnection
from streamlit.runtime.caching import cache_data
from weaviate.client import Client


class WeaviateConnection(BaseConnection["Client"]):
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

    def _connect(self, **kwargs) -> Client:
        auth_config = self._create_auth_config()
        url = self.url or self._secrets.get("WEAVIATE_URL")
        return Client(
            url,
            auth_client_secret=auth_config,
            additional_headers=self.additional_headers,
        )

    def _create_auth_config(self) -> Optional[weaviate.AuthApiKey]:
        api_key = self.api_key or self._secrets.get("WEAVIATE_API_KEY")
        if api_key is not None:
            return weaviate.AuthApiKey(api_key=api_key)
        else:
            return None

    def _convert_to_dataframe(self, results) -> pd.DataFrame:
        class_name = list(results["data"]["Get"].keys())[0]
        data = results["data"]["Get"][class_name]
        df = pd.json_normalize(data)
        return df

    def query(self, query: str, ttl: int = 3600, **kwargs) -> pd.DataFrame:
        @cache_data(ttl=ttl)
        def _query(query: str, **kwargs):
            results = self._connect().query.raw(query)
            if "errors" in results:
                error_message = (
                    f"The GraphQL query returned an error: {results['errors']}"
                )
                raise Exception(error_message)
            else:
                return results

        results = _query(query, **kwargs)

        return self._convert_to_dataframe(results)

    def client(self) -> Client:
        return self._connect()
