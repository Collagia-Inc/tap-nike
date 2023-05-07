"""REST client handling, including nikeStream base class."""

from __future__ import annotations

import logging

import boto3
from botocore.exceptions import ClientError
import os
from pathlib import Path
import pickle
from typing import Any, Callable, Iterable

import requests
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
            "Host": "api.nike.com",
            "User-Agent": "Chrome v22.2 Linux Ubuntu",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "X-Requested-With": "XMLHttpRequest",
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
        if response.json()["pages"]["next"] == "":
            return None
        self.path = response.json()["pages"]["next"]
        return response.json()["pages"]["next"]

    # def get_url_params(
    #     self,
    #     context: dict | None,
    #     next_page_token: Any | None,
    # ) -> dict[str, Any]:
    #     """Return a dictionary of values to be used in URL parameterization.
    #
    #     Args:
    #         context: The stream context.
    #         next_page_token: The next page index or value.
    #
    #     Returns:
    #         A dictionary of URL query parameters.
    #     """
    #     params: dict = {}
    #     channel_id = self.config["channel_id"]
    #     params["filter"] = f'language(en),marketplace(US),channelId({channel_id}),inStock(false),includeExpired(true)'
    #     return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """
        s3 = boto3.client('s3')
        bucket_name = 'meltano-state'
        file_key = self.config["job_id"]
        logging.info(f"######### FOLLOWING file key obtained {file_key}")
        custom_state = {}
        try:
            s3.head_object(Bucket=bucket_name, Key=file_key)
        except ClientError as e:
            logging.info(f"S3 init Exception occurred {e}")
        else:
            # Load the object from S3 using pickle
            resp = s3.get_object(Bucket=bucket_name, Key=file_key)
            data = resp['Body'].read()
            custom_state = pickle.loads(data)
        for response_object in response.json()["objects"]:
            flatten_dict = {}
            if response_object.get("productInfo"):
                for product_info in response_object["productInfo"]:
                    try:
                        for k, v in product_info.items():
                            if k == "merchProduct":
                                try:
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
                                    logging.info(f"Exception occurred {e}")
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
                                    logging.info(f"Exception occurred {e}")
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
                                                        if not custom_state.get("identifiers"):
                                                            custom_state["identifiers"] = [flatten_dict["ITEM_IDENTIFIER"]]
                                                            yield flatten_dict
                                                        elif flatten_dict["ITEM_IDENTIFIER"] not in \
                                                                    custom_state["identifiers"]:
                                                            custom_state["identifiers"].append(flatten_dict["ITEM_IDENTIFIER"])
                                                            yield flatten_dict

                                                    except Exception as e:
                                                        logging.info(f"Exception occurred {e}")
                                except Exception as e:
                                    logging.info(f"Exception occurred {e}")
                    except Exception as e:
                        logging.info(f"Exception occurred {e}")
        try:
            s3.put_object(Bucket=bucket_name, Key=file_key, Body=pickle.dumps(custom_state))
        except Exception as e:
            logging.info(f"S3 put exceptiob {e}")

