from typing import Optional

import pandas as pd
import weaviate
from streamlit.connections import ExperimentalBaseConnection
from weaviate.client import Client


class WeaviateConnection(ExperimentalBaseConnection["Client"]):
    def __init__(self, connection_name: str, url=None, api_key=None, **kwargs) -> None:
        self.url = url
        self.api_key = api_key
        super().__init__(connection_name, **kwargs)

    def _connect(self, **kwargs) -> Client:
        auth_config = self._create_auth_config()
        return Client(self.url, auth_client_secret=auth_config)

    def _create_auth_config(self) -> Optional[weaviate.AuthApiKey]:
        if self.api_key is not None:
            return weaviate.AuthApiKey(api_key=self.api_key)
        else:
            return None

    def _convert_to_dataframe(self, results) -> pd.DataFrame:
        class_name = list(results["data"]["Get"].keys())[0]
        data = results["data"]["Get"][class_name]
        df = pd.DataFrame(data)
        return df

    def query(self, query: str, **kwargs) -> pd.DataFrame:
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
