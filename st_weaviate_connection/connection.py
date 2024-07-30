from typing import Optional, List

import pandas as pd
import weaviate
from streamlit.connections import BaseConnection
from streamlit.runtime.caching import cache_data
from weaviate.client import WeaviateClient
from weaviate.auth import _APIKey
from weaviate.classes.init import Auth
from weaviate.collections.classes.internal import _RawGQLReturn
from weaviate.collections.classes.filters import (
    _Filters,
)
from weaviate.collections.classes.grpc import TargetVectorJoinType
from weaviate.collections.classes.data import DataObject
from weaviate.collections.classes.types import WeaviateProperties


def weaviate_response_objects_to_df(
    objects: List[DataObject[WeaviateProperties, None]]
) -> pd.DataFrame:
    """
    Convert a list of Weaviate DataObjects to a pandas DataFrame.
    """
    if objects:
        df = pd.json_normalize([obj.properties for obj in objects])
        return df
    else:
        return None


class WeaviateConnection(BaseConnection["WeaviateClient"]):
    """
    A Streamlit connection to a Weaviate database.
    """

    def __init__(
        self,
        connection_name: str,
        url: str=None,
        api_key=None,
        additional_headers=None,
        **kwargs,
    ) -> None:
        """
        Initialize the Weaviate connection.

        Parameters
        ----------
        connection_name : str
            The name of the connection.
        url : str, optional
            The URL of a Weaviate Cloud cluster.
            Provide this or the `weaviate_client` parameter.
            Default: None.
        api_key : str, optional
            The Weaviate API key to use for authentication. Default: None.
        additional_headers : dict, optional
            Additional headers to include in the request.
            e.g.: "X-<PROVIDER>-Api-Key": "<API_KEY>".
            Default: None.
        """

        self.url = url
        self.api_key = api_key
        self.additional_headers = additional_headers
        if url == "localhost":
            self._client = weaviate.connect_to_local(
                auth_credentials=self._create_auth_config(),
                headers=self.additional_headers,
                skip_init_checks=True,
            )
        else:
            self._client = weaviate.connect_to_weaviate_cloud(
                cluster_url=url,
                auth_credentials=self._create_auth_config(),
                headers=self.additional_headers,
                skip_init_checks=True,
            )
        super().__init__(connection_name, **kwargs)

    def _connect(self) -> WeaviateClient:
        self._client.connect()
        return self._client

    def _create_auth_config(self) -> Optional[_APIKey]:
        api_key = self.api_key or self._secrets.get("WEAVIATE_API_KEY")
        if api_key is not None:
            return Auth.api_key(api_key=api_key)
        else:
            return None

    def _gql_to_dataframe(self, results: _RawGQLReturn) -> pd.DataFrame:
        collection_name = list(results.get.keys())[0]
        data = results.get[collection_name]
        df = pd.DataFrame(data)
        return df

    def hybrid_search(
        self,
        collection_name: str,
        query: str,
        limit: int = 10,
        filters: Optional[_Filters] = None,
        target_vectors: Optional[TargetVectorJoinType] = None,
        query_properties: Optional[List[str]] = None,
        alpha: float = 0.7,
    ) -> pd.DataFrame:
        """
        Query a Weaviate collection using a simplified hybrid query.

        Parameters
        ----------
        collection_name : str
            The name of the collection to query.
        query : str
            The query to search for.
        limit : int, optional
            The number of results to return.
            Default: 10.
        filters : Filter, optional
            The filters to apply to the query.
            Import the `WeaviateFilter` class from `st_weaviate_connection` to use this argument.
        target_vectors : string, List[string], List[TargetVectors], optional
            The target vector(s) to search in the semantic search part of the query.
            Only required if the target collection uses named vectors.
            Optionally, import the `WeaviateTargetVectors` class from `st_weaviate_connection` to use this argument.
        query_properties : List[str], optional
            The properties to query in the keyword search part of the query.
            If not provided, all properties are queried.
        alpha: float, optional
            The weight of the semantic search part of the query. (alpha=1 is a semantic search, alpha=0 is a keyword search).
            If not provided, the Weaviate server default value is used.
        """

        collection = self._client.collections.get(name=collection_name)

        def _hybrid_search(
            query: str,
            limit: int = 10,
            filters: Optional[_Filters] = None,
            target_vectors: Optional[TargetVectorJoinType] = None,
            query_properties: Optional[List[str]] = None,
            alpha: float = None,
        ):
            response = collection.query.hybrid(
                query=query,
                limit=limit,
                filters=filters,
                target_vector=target_vectors,
                query_properties=query_properties,
                alpha=alpha,
            )
            return response

        response = _hybrid_search(
            query, limit, filters, target_vectors, query_properties, alpha
        )

        return weaviate_response_objects_to_df(response.objects)

    def graphql_query(self, query: str, cache_ttl: int = 3600) -> pd.DataFrame:
        """
        Query Weaviate using a raw GraphQL query.

        Parameters
        ----------
        query : str
            The raw GraphQL query to execute.
        cache_ttl : int, optional
            The Streamlit time-to-live for the cached data. Default: 3600.
        """

        @cache_data(ttl=cache_ttl)
        def _graphql_query(_client: WeaviateClient, query: str):
            results = _client.graphql_raw_query(query)
            if results.errors is not None:
                error_message = f"The GraphQL query returned an error: {results.errors}"
                raise Exception(error_message)
            else:
                return results

        with self.client() as client:
            results = _graphql_query(client, query)

        return self._gql_to_dataframe(results)

    def client(self) -> WeaviateClient:
        """
        Connect to Weaviate and return the client object for use in queries.
        """

        self._connect()

        return self._client

    def close(self) -> None:
        """
        Close the connection to Weaviate.
        """

        self._client.close()

        return None
