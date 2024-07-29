from typing import Optional, List

import pandas as pd
import weaviate
from streamlit.connections import BaseConnection
from streamlit.runtime.caching import cache_data
from weaviate.client import WeaviateClient
from weaviate.collections.classes.internal import _RawGQLReturn
from weaviate.collections.classes.filters import (
    _Filters,
)
from weaviate.collections.classes.grpc import (
    TargetVectorJoinType,
)
from weaviate.collections.classes.data import DataObject
from weaviate.collections.classes.types import WeaviateProperties


def _response_objects_to_df(
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
        url: str,
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
        url : str
            The URL of the Weaviate cluster.
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
        self._client = weaviate.connect_to_weaviate_cloud(
            cluster_url=url,
            auth_credentials=self._create_auth_config(),
            headers=self.additional_headers,
            skip_init_checks=True,
        )
        super().__init__(connection_name, **kwargs)

    def _create_auth_config(self) -> Optional[weaviate.AuthApiKey]:
        api_key = self.api_key or self._secrets.get("WEAVIATE_API_KEY")
        if api_key is not None:
            return weaviate.AuthApiKey(api_key=api_key)
        else:
            return None

    def _gql_to_dataframe(self, results: _RawGQLReturn) -> pd.DataFrame:
        class_name = list(results.get.keys())[0]
        data = results.get[class_name]
        df = pd.json_normalize(data)
        return df

    def hybrid_query(
        self,
        collection_name: str,
        query: str,
        limit: int = 10,
        target_vectors: Optional[TargetVectorJoinType] = None,
        filters: Optional[_Filters] = None,
        cache_ttl: int = 3600,
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
            The number of results to return. Default: 10.
        target_vectors : string, List[string], List[TargetVectors], optional
            The target vector(s) to search. Only required if the target collection uses named vectors. Default: None.
        filters : Filter, optional
            The filters to apply to the query. Default: None.
        cache_ttl : int, optional
            The Streamlit time-to-live for the cached data. Default: 3600.
        """
        collection = self._client.collections.get(name=collection_name)

        @cache_data(ttl=cache_ttl)
        def _hybrid_query(
            query: str,
            limit: int = 10,
            target_vectors: Optional[TargetVectorJoinType] = None,
            filters: Optional[_Filters] = None,
        ):
            response = collection.query.hybrid(
                query=query, limit=limit, target_vector=target_vectors, filters=filters
            )
            return response

        response = _hybrid_query(query, limit, target_vectors, filters)
        return _response_objects_to_df(response.objects)

    def near_text_query(
        self,
        collection_name: str,
        query: str,
        limit: int = 10,
        target_vectors: Optional[TargetVectorJoinType] = None,
        filters: Optional[_Filters] = None,
        cache_ttl: int = 3600,
    ) -> pd.DataFrame:
        """
        Query a Weaviate collection using a simplified semantic (near_text) query.

        Parameters
        ----------
        collection_name : str
            The name of the collection to query.
        query : str
            The query to search for.
        limit : int, optional
            The number of results to return. Default: 10.
        target_vectors : string, List[string], List[TargetVectors], optional
            The target vector(s) to search. Only required if the target collection uses named vectors. Default: None.
        filters : Filter, optional
            The filters to apply to the query. Default: None.
        cache_ttl : int, optional
            The Streamlit time-to-live for the cached data. Default: 3600.
        """
        collection = self._client.collections.get(name=collection_name)

        @cache_data(ttl=cache_ttl)
        def _near_text_query(
            query: str,
            limit: int = 10,
            target_vectors: Optional[TargetVectorJoinType] = None,
            filters: Optional[_Filters] = None,
        ):
            response = collection.query.hybrid(
                query=query, limit=limit, target_vector=target_vectors, filters=filters
            )
            return response

        response = _near_text_query(query, limit, target_vectors, filters)
        return _response_objects_to_df(response.objects)

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
        def _graphql_query(client: WeaviateClient, query: str):
            results = self._connect().graphql_raw_query(query)
            if "errors" in results:
                error_message = (
                    f"The GraphQL query returned an error: {results['errors']}"
                )
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
