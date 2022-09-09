"""Indicates block object for notion.

It provides read or update content feature.

Typical usage example:
    from pytion import Block

    print(Block(blockID=...).get_text())
"""

from typing import Optional

import json
import httpx

from util import token

from .version import Version
from .db.property import Text
from .db.parser import parse_richtext

class Block:
    """Class that indicates block object for notion.

    ### Args ::
        blockID (str):
            ID of target block in notion.
        version (str):
            Notion API version.
            You can pass raw string (e.g. '2022-02-22')
            and from Version class (e.g. Version.v3, Version.default) two ways.
    """

    def __init__(self, *, blockID: str, version: str = Version.default):
        self.client = httpx.Client(
            base_url=f"https://api.notion.com/v1/blocks/{blockID}",
            headers={
                "Authorization":    "Bearer " + token['notion'],
                "Content-Type":     "application/json",
                "Notion-Version":   version
            }
        )

    def request(self, method: str, url: str, data: Optional[dict]=None):
        """Simple request sender

        Since it's internal-use only, this func provides only method, url and
        data parameter for use.

        ### Args ::
            method (str):
                Method of your HTTP request.
                This should be one of the request method(e.g. GET, POST, ...).
            url (str):
                URL of your HTTP request.
                Since base url is set to block endpoint, you must erase it.
                (It means that "/" indicates "https://.../(blockID)")
            data (dict, optional):
                Data of your HTTP request.
                You can omit this parameter if you are requesting without data.
                Data is converted into json string, and encoded automatically.

        ### Returns ::
            httpx.Response object of your request.
        """
        return self.client.request(
            method=method,
            url=url,
            data=None if data is None else json.dumps(data).encode()
        )

    def get_text(self):
        """Load text of block as string.

        ### Returns ::
            Loaded text as string.
        """
        content = self.request(method="GET", url="/").json()
        return parse_richtext(content['paragraph'])

    def get_text_list(self):
        """Load all texts of children of this block as string.

        ### Returns ::
            List of loaded text.
        """
        content = self.request(method="GET", url="/children").json()
        return [
            parse_richtext(item['paragraph'])
            for item in content['results']
        ]

    def update_text(self, new_text: str):
        """Update text of connected block with provided text.

        ### Args ::
            new_text (str):
                Text to be updated

        ### Returns ::
            True if updating is successful, False if not.
        """
        resp = self.request(
            method="PATCH",
            url="/",
            data={"paragraph": Text(new_text).to_dict()}
        )
        return resp.is_success
