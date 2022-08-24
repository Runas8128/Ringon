from typing import Optional, Callable, Any, Union
import json, httpx

from util.load_token import provider

from .db.filter import Filter
from .db.property import BaseProperty, Text

def parse_richtext(richTextObj: dict):
    if 'title' in richTextObj:
        richTextObj = richTextObj['title']
    if 'rich_text' in richTextObj:
        richTextObj = richTextObj['rich_text']
    return richTextObj[0]['plain_text']

class Notion:
    class Version:
        v1 =            "2021-05-13"
        v2 =            "2021-08-16"
        v3 = default =  "2022-02-22"
        v4 =            "2022-06-28"
    
    def __init__(self, *, version: Version = Version.default):
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
    
    def add_database(self, dbID: str, **properties: BaseProperty):
        """ Usage
        notion.add_database(
            dbID=ID.database.deck.data,
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
            data={'parent': { 'database_id': dbID }, 'properties': properties, 'children': []}
        )

        return resp.is_success
    
    def query_database(
        self,
        dbID: str,
        filter: Optional[Filter],
        parser: Callable[[dict], Any]
    ):
        """ Usage
            notion.query_database(
                dbID=ID.database.deck.data,
                filter=Filter(rule="and", name=filter.Text(contains=kw), ...),
                parser=Parser(ID=Type.Number, only_values=True)
            )
        )
        """
        
        results = self.request(
            method="POST",
            url=f"/databases/{dbID}/query",
            data=None if filter == None else {'filter': filter.to_dict()}
        ).json().get('results', [])
        
        return [parser(result) for result in results]
    
    def get_block_text(self, blockID: str):
        content = self.request(method="GET", url=f"/blocks/{blockID}").json()
        return parse_richtext(content['paragraph'])
    
    def get_block_text_list(self, rootBlockID: str):
        content = self.request(method="GET", url=f"/blocks/{rootBlockID}/children").json()
        return [parse_richtext(item['paragraph']) for item in content['results']]

    def update_block_text(self, blockID: str, newText: str):
        resp = self.request(
            method="PATCH",
            url=f"/blocks/{blockID}",
            data={ "paragraph": Text(newText).to_dict() }
        )

        return resp.is_success
    
    def append_text(self, rootBlockID: str, newText: str):
        resp = self.request(
            method="PATCH",
            url=f"/blocks/{rootBlockID}/children",
            data={
                "children": [{
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": Text(newText).to_dict()
                }]
            }
        )

        return resp.is_success
