"""Stream type classes for tap-nike."""

from __future__ import annotations

from pathlib import Path

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_nike.client import nikeStream

# TODO: Delete this is if not using json files for schema definition
SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")
# TODO: - Override `UsersStream` and `GroupsStream` with your own stream definition.
#       - Copy-paste as many times as needed to create multiple stream types.


class UsersStream(nikeStream):
    """Define custom stream."""

    name = "nike"
    path = "product_feed/threads/v2"
    primary_keys = ["squarishURL", "modificationDate"]
    replication_key = "modificationDate"
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    schema = th.PropertiesList(
        th.Property(
            "squarishURL",
            th.StringType,
        ),
        th.Property(
            "view",
            th.StringType,
        ),
        th.Property(
            "modificationDate",
            th.StringType,
        ),
        th.Property(
            "merchGroup",
            th.StringType,
        ),
        th.Property(
            "styleCode",
            th.StringType,
        ),
        th.Property(
            "styleColor",
            th.StringType,
        ),
        th.Property(
            "colorCode",
            th.StringType,
        ),
        th.Property(
            "channels",
            th.ArrayType(
                th.StringType
            ),
        ),
        th.Property(
            "genders",
            th.ArrayType(
                th.StringType
            ),
        ),
        th.Property(
            "sportTags",
            th.ArrayType(
                th.StringType
            ),
        ),
        th.Property(
            "msrp",
            th.NumberType,
        ),
        th.Property(
            "fullPrice",
            th.NumberType,
        ),
        th.Property(
            "currentPrice",
            th.NumberType,
        )
    ).to_dict()