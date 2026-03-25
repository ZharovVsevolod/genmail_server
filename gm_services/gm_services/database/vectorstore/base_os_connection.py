#
# With the great help of the Internet, offical documentation and developer's tears
# 
# Offical documentation, page about working with recordings in indexes:
# https://docs.opensearch.org/latest/im-plugin
#
# Offical github, creating (and working with) indexes
# https://github.com/opensearch-project/opensearch-py/blob/main/guides/json.md
#
# Offical documentation, search:
# https://docs.opensearch.org/latest/search-plugins/keyword-search/
# https://docs.opensearch.org/latest/search-plugins/searching-data/sort/
# https://docs.opensearch.org/latest/search-plugins/filter-search/
# https://docs.opensearch.org/latest/query-dsl/query-filter-context/
# https://docs.opensearch.org/latest/api-reference/index-apis/refresh/
# 
 
import os
import json
from httpx import Client

from ...config import Settings

from httpx import Response
from typing import Literal, Any


# ----------------------
# Some helpful functions
# ----------------------
def make_address_index_name(index: str) -> str:
    """Add "/" before index name to make an address"""
    if index[0] != "/":
        index = "/" + index
    return index


def make_address_document_name(
    index: str, 
    id: str | None = None,
    action: Literal["document", "update", "search"] = "document"
) -> str:
    """
    Make from the index name and document id correct address for OpenSearch client
    """
    index = make_address_index_name(index)

    match action:
        case "document":
            addr_action = "_doc"
        
        case "update":
            addr_action = "_update"
        
        case "search":
            addr = index + "/_search"
            return addr

    addr = index + "/" + addr_action + "/" + id
    return addr


# -------------------------
# Class of Index Management
# -------------------------
class IndexesManager:
    def __init__(self, http: Client):
        self.http = http


    def _default_new_index_body(self):
        index_body = {
            "settings": {
                "index": {
                    "number_of_shards": 4
                }
            }
        }
        return index_body
    

    def _is_error_returned(self, responce: dict | Response) -> bool:
        if type(responce) is not dict:
            responce = responce.json()

        if responce.get("error") is None:
            return False
        return True


    def create(self, index: str, body: dict | None = None):
        """Create a new index"""
        # Default index body
        if body is None:
            body = self._default_new_index_body()
        body = json.dumps(body)
        
        index = make_address_index_name(index)
        
        responce = self.http.put(index, data = str(body))

        if self._is_error_returned(responce):
            print("Index is already exists")


    def exists(self, index: str) -> bool:
        """Check if index is exists"""
        index = make_address_index_name(index)
        responce = self.http.get(index)
        return not self._is_error_returned(responce)


    def delete(self, index: str) -> None:
        """Delete an index"""
        index = make_address_index_name(index)
        self.http.delete(index)


# -----------------------------------
# Main OpenSearch custom client class
# -----------------------------------
class CustomOpenSearch:
    def __init__(self) -> None:
        # http client
        auth = (
            os.environ["OPENSEARCH_LOGIN"], 
            os.environ["OPENSEARCH_PASSWORD"]
        )
        self.http = Client(
            base_url = Settings.services.vectorbase.base_url,
            auth = auth,
            headers = {"Content-Type": "application/json"},
            verify = False
        )

        self.indices = IndexesManager(self.http)
    

    def info(self) -> dict:
        """Get base info about connection to OpenSearch"""
        responce = self.http.get("/")
        responce = responce.json()
        return responce
    

    def refresh(self, index: str | None = None) -> None:
        refresh_addr = "/_refresh"
        if index is None:
            self.http.post(refresh_addr)
        else:
            index = make_address_index_name(index)
            addr = index + refresh_addr
            self.http.post(addr)
            

    def exists(self, index: str, id: str) -> bool:
        addr = make_address_document_name(index, id, action = "document")
        responce = self.http.get(addr)
        responce: dict = responce.json()
        does_exist = responce.get("found")
        return does_exist
    

    def search(
        self, 
        index: str, 
        query: dict, 
        size: int | None = None,
        sort: str | None = None,
        search_after: dict[str, Any] | None = None
    ) -> dict:
        """
        Search for a record in the index
        
        sort: Should be as "<PARAMETER>:<SORT_TYPE>"
        """
        addr = make_address_document_name(index, action = "search")

        # Add sort if needed
        if sort is not None:
            sort = sort.split(":")
            query["sort"] = [
                {
                    sort[0]: {
                        "order": sort[1]
                    }
                }
            ]

        # Add search_after if needed
        if search_after is not None:
            query["search_after"] = search_after.get("search_after", default = [])
        
        # Final query
        query = {"query": query}
        query = json.dumps(query)

        # responce = self.http.get(addr, params = query)
        responce = self.http.request(
            method = "GET",
            url = addr,
            data = query
        )
        responce = responce.json()
        
        if size is not None:
            responce["hits"]["hits"] = responce["hits"]["hits"][:size]
        
        return responce


    def index(self, index: str, id: str, body: dict, refresh: bool = True) -> None:
        """Create or update record in the index"""
        if self.exists(index, id):
            self.update(index, id, body, refresh)
        else:
            self.create(index, id, body, refresh)


    def update(self, index: str, id: str, body: dict, refresh: bool = True) -> None:
        """Change the record in the index"""
        addr = make_address_document_name(index, id, action = "update")
        body = {"doc": body}
        body = json.dumps(body)
        responce = self.http.post(addr, data = body)
        print(responce.json())
        if refresh:
            self.refresh(index)


    def create(self, index: str, id: str, body: dict, refresh: bool = True) -> None:
        """Add the record to the index"""
        addr = make_address_document_name(index, id, action = "document")
        body = json.dumps(body)
        responce = self.http.put(addr, data = body)
        print(responce.json())
        if refresh:
            self.refresh(index)


    def delete(self, index: str, id: str, refresh: bool = True) -> None:
        """Delete the record in the index"""
        addr = make_address_document_name(index, id, action = "document")
        self.http.delete(addr)
        if refresh:
            self.refresh(index)


    def delete_by_query(
        self, 
        index: str, 
        body: dict, 
        refresh: bool = True
    ) -> None:
        """Delete documents matching the provided query"""
        responce = self.search(
            index = index,
            query = body
        )
        hits: dict = responce.get("hits")
        matching_ids = []

        if hits.get("value") > 0:
            for record in hits.get("hits"):
                record_id = record.get("_id")
                matching_ids.append(record_id)
        
            for next_id in matching_ids:
                self.delete(
                    index = index,
                    id = next_id,
                    refresh = False
                )

        if refresh:
            self.refresh(index)