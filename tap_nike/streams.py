"""Stream type classes for tap-nike."""

from __future__ import annotations

from pathlib import Path

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_nike.client import nikeStream

# TODO: Delete this is if not using json files for schema definition
SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")
# TODO: - Override `UsersStream` and `GroupsStream` with your own stream definition.
#       - Copy-paste as many times as needed to create multiple stream types.


class NikeStream(nikeStream):
    """Define custom stream."""

    name = "nike"
    path = "product_feed/threads/v2?filter=language%28en%29&filter=marketplace%28US%29&filter=channelId%28d9a5bc42-4b9c-4976-858a-f159cf99c647%29&filter=inStock%28false%29&filter=includeExpired%28true%29&anchor=100"
    primary_keys = ["squarishURL", "modificationDate"]
    replication_key = "modificationDate"
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    schema = th.PropertiesList(
        th.Property(
            "ITEM_IDENTIFIER",
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

class SnkrsStream(nikeStream):
    """Define custom stream."""

    name = "Snkrs"
    path = "product_feed/threads/v2?filter=language%28en%29&filter=marketplace%28US%29&filter=channelId%28010794e5-35fe-4e32-aaff-cd2c74f89d61%29&filter=inStock%28false%29&filter=includeExpired%28true%29"
    primary_keys = ["squarishURL", "modificationDate"]
    replication_key = "modificationDate"
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    schema = th.PropertiesList(
        th.Property(
            "ITEM_IDENTIFIER",
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


class NikeMobileStream(nikeStream):
    """Define custom stream."""

    name = "nike_mobile"
    path = "product_feed/threads/v2?filter=language%28en%29&filter=marketplace%28US%29&filter=channelId%2882a74ac1-c527-4470-b7b0-fb5f3ef3c2e2%29&filter=inStock%28false%29&filter=includeExpired%28true%29"
    primary_keys = ["squarishURL", "modificationDate"]
    replication_key = "modificationDate"
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    schema = th.PropertiesList(
        th.Property(
            "ITEM_IDENTIFIER",
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