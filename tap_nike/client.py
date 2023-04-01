"""REST client handling, including nikeStream base class."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Iterable

import requests
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.streams import RESTStream

_Auth = Callable[[requests.PreparedRequest], requests.PreparedRequest]
SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class nikeStream(RESTStream):
    """nike stream class."""

    # TODO: Set the API's base URL here:
    url_base = "https://api.nike.com/"

    records_jsonpath = "$[*]"  # Or override `parse_response`.
    next_page_token = ""  # Or override `get_next_page_token`.

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        headers = {
            'Host': 'api.nike.com',
            'User-Agent': 'Chrome v22.2 Linux Ubuntu',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest'
        }

        return headers

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Any | None,
    ) -> Any | None:
        """Return a token for identifying next page or None if no more pages.

        Args:
            response: The HTTP ``requests.Response`` object.
            previous_token: The previous page token value.

        Returns:
            The next pagination token.
        """
        # TODO: If pagination is required, return a token which can be used to get the
        #       next page. If this is the final page, return "None" to end the
        #       pagination loop.

        if self.next_page_token == response.json()["pages"]["next"]:
            return None
        self.next_page_token = response.json()["pages"]["next"]
        if response.json()["pages"]["next"] == "":
            return None
        else:
            return response.json()["pages"]["next"]

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        channel_id = self.config["channel_id"]
        params["filter"] = f'language(en),marketplace(US),channelId({channel_id}),inStock(false),includeExpired(true)'
        return params


    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """
        for response_object in response.json()["objects"]:
            flatten_dict = {}
            for product_info in response_object["productInfo"]:
                for k, v in product_info.items():
                    if k == "merchProduct":
                        try:
                            flatten_dict["merchGroup"] = product_info["merchProduct"]["merchGroup"]
                            flatten_dict["styleCode"] = product_info["merchProduct"]["styleCode"]
                            flatten_dict["colorCode"] = product_info["merchProduct"]["colorCode"]
                            flatten_dict["channels"] = product_info["merchProduct"]["channels"]
                            flatten_dict["genders"] = product_info["merchProduct"]["genders"]
                            flatten_dict["sportTags"] = product_info["merchProduct"]["sportTags"]
                            flatten_dict["modificationDate"] = product_info["merchProduct"]["modificationDate"]
                            flatten_dict["view"] = ""
                            flatten_dict["squarishURL"] = ""
                        except Exception as e:
                            pass
                    if k == "merchPrice":
                        try:
                            for k,v in product_info["merchPrice"].items():
                                if k == "msrp":
                                    flatten_dict["msrp"] = product_info["merchPrice"]["msrp"]
                                if k == "fullPrice":
                                    flatten_dict["fullPrice"] = product_info["merchPrice"]["fullPrice"]
                                if k == "currentPrice":
                                    flatten_dict["currentPrice"] = product_info["merchPrice"]["currentPrice"]
                        except Exception as e:
                            pass
                if response_object["publishedContent"]:
                    for node in response_object["publishedContent"]["nodes"]:
                        for k, v in node.items():
                            if k == "nodes":
                                for n_node in node["nodes"]:
                                    if n_node["properties"]:
                                        try:
                                            if n_node["properties"]["squarish"]:
                                                for k, v in n_node["properties"]["squarish"].items():
                                                    if k == "view":
                                                        flatten_dict["view"] = n_node["properties"]["squarish"]["view"]
                                                    if k == "url":
                                                        flatten_dict["squarishURL"] = n_node["properties"]["squarish"]["url"]
                                            if not self.tap_state.get("identifiers"):
                                                self.tap_state["identifiers"] = [flatten_dict["squarishURL"] +
                                                                                 flatten_dict["modificationDate"]]
                                                yield flatten_dict
                                            elif flatten_dict["squarishURL"] + flatten_dict["modificationDate"] not in \
                                                    self.tap_state["identifiers"]:
                                                self.tap_state["identifiers"].append(flatten_dict["squarishURL"] +
                                                                                     flatten_dict["modificationDate"])
                                                yield flatten_dict
                                        except Exception as e:
                                            pass
