"""Indicates database object for notion.

It provides append, query, delete and update feature.

Typical usage example:
    from pytion import Database, ...

    print(Database(dbID=...).query(filter=..., parser=...)))
"""

from typing import Optional, Callable, Any

import json
import httpx

from util.load_token import provider

from .version import Version
from .db.filter import Filter
from .db.property import BaseProperty

class Database:
    """Class that indicates database object for notion.

    ### Args ::
        dbID (str):
            ID of target database in notion.
        version (str):
            Notion API version.
            You can pass raw string (e.g. '2022-02-22')
            and from Version class (e.g. Version.v3, Version.default) two ways.
    """
    def __init__(self, *, dbID: str, version: str = Version.default):
        self._id = dbID

        self.client = httpx.Client(
            base_url="https://api.notion.com/v1",
            headers={
                "Authorization":    "Bearer " + provider.load_token('notion'),
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
                (It means that "/" indicates "https://.../v1")
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

    def append(self, **properties: BaseProperty):
        """Append new page to connected database.

        ### Args ::
            **properties:
                Properties of new data.
                Key is property name, and value is property object.

        ### Returns ::
            True if appending page to database, False if not.

        ### Examples ::
            from pytion import Database, prop

            Database(...).append(
                name=prop.Title(name),
                desc=prop.Text(desc),
                ...
            )
        """

        properties = {key: prop.to_dict() for key, prop in properties.items()}

        resp = self.request(
            method='POST',
            url='/pages',
            data={'parent': { 'database_id': self._id }, 'properties': properties, 'children': []}
        )

        return resp.is_success

    def query(
        self,
        filter: Optional[Filter], # pylint: disable=redefined-builtin
        parser: Callable[[dict], Any]
    ):
        """Query pages from connected database.

        ### Args ::
            filter (pytion.Filter, optional):
                Filter object.
                You can omit this field when you query all pages of database.
            parser (Callable[[dict], Any]):
                Parser callback function.
                You can simply pass pytion.Parser object.

        ### Returns ::
            Parsed query result.
            If an error occured, return empty list.

        ### Examples ::
            from pytion import filter, parser
            from pytion import Database, Filter, Parser

            Database(...).query(
                filter=Filter(rule="and", name=filter.Text(contains=kw), ...),
                parser=Parser(only_values=True, ID=Type.Number)
            )
        """

        results = self.request(
            method="POST",
            url=f"/databases/{self._id}/query",
            data=None if filter is None else {'filter': filter.to_dict()}
        ).json().get('results', [])

        return [parser(result) for result in results]

    def delete(self, page_id: str):
        """Delete page (archive from notion server).

        ### Args ::
            page_id (str):
                Page id to delete.

        ### Returns ::
            True if deleting page is successful, False if not.

        ### Examples ::
            from pytion import Database

            Database(...).delete(page_id)
        """
        return self.request('DELETE', f'/blocks/{page_id}').is_success

    def update(self, page_id: str, **properties: BaseProperty):
        """Update page's properties.

        ### Args ::
            page_id (str):
                Page id to update properties.
            **properties:
                Properties to update.
                Key is property name, and value is property object.

        ### Returns ::
            True if updating page is successful, False if not.

        ### Examples ::
            from pytion import Database, prop

            Database(...).update(
                pageID=pageID,
                desc=prop.Text(desc),
                clazz=prop.Select(clazz),
                version=prop.Number(ver+1),
                ...
            )
        """

        properties = {key: prop.to_dict() for key, prop in properties.items()}

        resp = self.request(
            method='PATCH',
            url=f'/pages/{page_id}',
            data={'properties': properties}
        )

        return resp.is_success
