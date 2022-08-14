from typing import Optional, Callable, Any
import json, httpx

from .load_token import provider

def parse_richtext(richTextObj: dict):
    if 'title' in richTextObj:
        richTextObj = richTextObj['title']
    if 'rich_text' in richTextObj:
        richTextObj = richTextObj['rich_text']
    return richTextObj[0]['plain_text']

class Version:
    v1 =            "2021-05-13"
    v2 =            "2021-08-16"
    v3 = default =  "2022-02-22"
    v4 =            "2022-06-28"

class Notion:
    def __init__(self, *, version: Version = Version.default):
        self.client = httpx.Client(
            base_url="https://api.notion.com/v1",
            headers={
                "Authorization":    "Bearer " + provider.load_token('notion'),
                "Content-Type":     "application/json",
                "Notion-Version":   version.value
            }
        )
    
    def request(self, method: str, url: str, data: Optional[dict]=None):
        return self.client.request(method, url, data=None if data == None else json.dumps(data).encode())
    
    def add_database(self, dbID: str, properties: dict):
        """
        Properties Example for Decklist
        {
            'name': { 'title': [{ 'text': { 'content': name } }] },
            'desc': { 'rich_text': [{ 'text': { 'content': desc } }] },
            'class': { 'select': { 'name': clazz } },
            'author': { 'number': author }
        }
        """
        resp = self.request(
            method='POST',
            url='/pages',
            data={'parent': { 'database_id': dbID }, 'properties': properties, 'children': []}
        )

        return resp.is_success
    
    def query_database(self, dbID: str, filter: dict, parser: Callable[[dict], Any]):
        """
        Filter Example for Decklist - class search
        {
            'property': 'class',
            'select': { 'equals': '엘프' }
        }

        Parser Example for Decklist

        def parse(self, result: dict):
            properties = result['properties']
            data = {
                'name': get_text_from_richtext(properties['name']),
                'desc': get_text_from_richtext(properties['desc']),
                'class': properties['class']['select']['name'],
                'author': properties['author']['number']
            }
            
            return data
        """
        results = self.request(
            method="POST",
            url=f"/databases/{dbID}/query",
            data={'filter': filter}
        ).json()['results']
        
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
            data={
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": { "content": newText }
                    }]
                }
            }
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
                    "paragraph": {
                        "rich_text": [{ "type": "text", "text": { "content": newText } }]
                    }
                }]
            }
        )

        return resp.is_success

class ID:
    class database:
        class deck:
            data    = "8ef3fed5a101492882ba96dab96c096b"
            contrib = "7a5aec5497b64aa5a9e0942fbeb81c97"
        
        class detect:
            full    = "481b6de47c6a41debf83fe1b93700622"
            part    = "371aa34963db4efa9b3d4b398aa3c46b"
            prob    = "5e22777f724b4f27a336cdce350bc1a2"
        
        birthday    = "a66f05422b91471da108737db205c7c7"
    
    class block:
        pack        = "b65b0b9652d04da58f960045aa01568c"
        word        = "233288a3891f4c008504470c8fbefc88"
