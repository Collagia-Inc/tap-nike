"""REST client handling, including nikeStream base class."""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Callable, Iterable

import requests
from singer_sdk.streams import RESTStream
import traceback

_Auth = Callable[[requests.PreparedRequest], requests.PreparedRequest]
SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class nikeStream(RESTStream):
    """nike stream class."""

    # TODO: Set the API's base URL here:
    url_base = "https://api.nike.com/"
    records_jsonpath = "$[*]"  # Or override `parse_response`.
    next_page_token = ""  # Or override `get_next_page_token`

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        headers = {
            "Host": "api.nike.com",
            "User-Agent": "Chrome v22.2 Linux Ubuntu",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "X-Requested-With": "XMLHttpRequest",
        }

        return headers

    def get_url(self, response: requests.Response) -> str:
        if self.tap_state["bookmarks"][self.name].get('replication_key_value'):
            self.path = self.tap_state["bookmarks"][self.name].get('replication_key_value')
        return "".join([self.url_base, self.path or ""])

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
        if self.path == response.json()["pages"]["next"]:
            return ""
        logging.info(f"TAP STATE {self.tap_state}")
        next_token = response.json()["pages"]["next"]
        logging.info(f"$$$$$$$ pages updated here {self.path} next token {next_token}")
        self.path = response.json()["pages"]["next"]
        time.sleep(5)
        return response.json()["pages"]["next"]


    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """
        for response_object in response.json()["objects"]:
            flatten_dict = {}
            if response_object.get("productInfo"):
                for product_info in response_object["productInfo"]:
                    try:
                        for k, v in product_info.items():
                            if k == "merchProduct":
                                try:
                                    flatten_dict["next_token"] = response.json()["pages"]["next"]
                                    flatten_dict["merchGroup"] = product_info["merchProduct"]["merchGroup"]
                                    flatten_dict["styleCode"] = product_info["merchProduct"]["styleCode"]
                                    flatten_dict["styleColor"] = product_info["merchProduct"]["styleColor"]
                                    flatten_dict["colorCode"] = product_info["merchProduct"]["colorCode"]
                                    flatten_dict["channels"] = product_info["merchProduct"]["channels"]
                                    flatten_dict["genders"] = product_info["merchProduct"]["genders"]
                                    flatten_dict["sportTags"] = product_info["merchProduct"]["sportTags"]
                                    flatten_dict["modificationDate"] = product_info["merchProduct"]["modificationDate"]
                                    flatten_dict["ITEM_IDENTIFIER"] = ""
                                except Exception as e:
                                    traceback.print_exc()
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
                                    traceback.print_exc()
                        if response_object["publishedContent"]:
                            for node in response_object["publishedContent"]["nodes"]:
                                try:
                                    for k, v in node.items():
                                        if k == "nodes":
                                            for n_node in node["nodes"]:
                                                if n_node["properties"]:
                                                    try:
                                                        if n_node["properties"]["squarish"]:
                                                            for k, v in n_node["properties"]["squarish"].items():
                                                                if k == "url":
                                                                    flatten_dict["ITEM_IDENTIFIER"] = n_node["properties"]["squarish"]["url"]
                                                                     yield flatten_dict
                                                    except Exception as e:
                                                        traceback.print_exc()
                                except Exception as e:
                                    traceback.print_exc()
                    except Exception as e:
                        traceback.print_exc()
                        pass

