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
    #url_base = "https://api.nike.com/product_feed/threads/v2?filter=language(en)&filter=marketplace(US)&filter=channelId(d9a5bc42-4b9c-4976-858a-f159cf99c647)&filter=inStock(false)&filter=includeExpired(true)"

    # OR use a dynamic url_base:
    # @property
    # def url_base(self) -> str:
    #     """Return the API URL root, configurable via tap settings."""
    #     return self.config["api_url"]

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
        params["filter"] = "language(en),marketplace(US),channelId(d9a5bc42-4b9c-4976-858a-f159cf99c647),inStock(false),includeExpired(true)"
        return params


    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """
        # TODO: Parse response body and return a set of records.
        yield from extract_jsonpath(self.records_jsonpath, input=response.json()["objects"])

    # def post_process(self, row: dict, context: dict | None = None) -> dict | None:
    #     """As needed, append or transform raw data to match expected structure.
    #
    #     Args:
    #         row: An individual record from the stream.
    #         context: The stream context.
    #
    #     Returns:
    #         The updated record dictionary, or ``None`` to skip the record.
    #     """
    #     # TODO: Delete this method if not needed.
    #     print(row)
    #     return row
