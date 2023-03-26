"""nike tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

# TODO: Import your custom stream types here:
from tap_nike import streams


class Tapnike(Tap):
    """nike tap class."""

    name = "tap-nike"
    # TODO: Update this section with the actual config values you expect:
    # config_jsonschema = th.PropertiesList(
    #     # th.Property(
    #     #     "id",
    #     #     th.StringType,
    #     #     required=True,
    #     # ),
    #     # th.Property(
    #     #     "channelId",
    #     #     th.ArrayType(th.StringType),
    #     #     required=True,
    #     # ),
    # ).to_dict()

    def discover_streams(self) -> list[streams.nikeStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.UsersStream(self),
        ]


if __name__ == "__main__":
    Tapnike.cli()
