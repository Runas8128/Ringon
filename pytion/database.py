from typing import Optional, Callable, Any, Union
import json, httpx

from util.load_token import provider

from .version import Version
from .db.filter import Filter
from .db.property import BaseProperty

class Database:
    def __init__(self, *, dbID: str, version: str = Version.default):
        self.id = dbID

        self.client = httpx.Client(
            base_url="https://api.notion.com/v1",
            headers={
                "Authorization":    "Bearer " + provider.load_token('notion'),
                "Content-Type":     "application/json",
                "Notion-Version":   version
            }
        )
    
    def request(self, method: str, url: str, data: Optional[dict]=None):
        return self.client.request(method, url, data=None if data == None else json.dumps(data).encode())
    
    def append(self, **properties: BaseProperty):
        """ Usage
        notion.add_database(
            name=property.Title(name),
            desc=property.Text(desc),
            clazz=property.Select(clazz),
            ...
        )
        """

        properties = {
            key: properties[key].to_dict()
            for key in properties.keys()
        }

        resp = self.request(
            method='POST',
            url='/pages',
            data={'parent': { 'database_id': self.id }, 'properties': properties, 'children': []}
        )

        return resp.is_success
    
    def query(
        self,
        filter: Optional[Filter],
        parser: Callable[[dict], Any]
    ):
        """ Usage
            notion.query_database(
                filter=Filter(rule="and", name=filter.Text(contains=kw), ...),
                parser=Parser(ID=Type.Number, only_values=True)
            )
        )
        """
        
        results = self.request(
            method="POST",
            url=f"/databases/{self.id}/query",
            data=None if filter == None else {'filter': filter.to_dict()}
        ).json().get('results', [])
        
        return [parser(result) for result in results]
    
    def delete(self, pageID: str):
        return self.request('DELETE', f'/blocks/{pageID}').is_success
    
    def update(self, pageID: str, **properties: BaseProperty):
        """ Usage
        notion.update_database(
            pageID=pageID,
            desc=property.Text(desc),
            clazz=property.Select(clazz),
            version=property.Number(ver+1),
            ...
        )
        """

        properties = {
            key: properties[key].to_dict()
            for key in properties.keys()
        }

        resp = self.request(
            method='PATCH',
            url=f'/pages/{pageID}',
            data={'properties': properties}
        )

        return resp.is_success
