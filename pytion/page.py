from util.load_token import provider

from .version import Version
from .db.property import Text

def parse_richtext(richTextObj: dict):
    if 'title' in richTextObj:
        richTextObj = richTextObj['title']
    if 'rich_text' in richTextObj:
        richTextObj = richTextObj['rich_text']
    return richTextObj[0]['plain_text']

class Page:
    def __init__(self, *, blockID: str, version: str = Version.default):
        self.client = httpx.Client(
            base_url=f"https://api.notion.com/v1/blocks/{blockID}",
            headers={
                "Authorization":    "Bearer " + provider.load_token('notion'),
                "Content-Type":     "application/json",
                "Notion-Version":   version
            }
        )
    
    def get_block_text(self, blockID):
        content = self.request(method="GET", url="/").json()
        return parse_richtext(content['paragraph'])
    
    def get_block_text_list(self):
        content = self.request(method="GET", url="/children").json()
        return [parse_richtext(item['paragraph']) for item in content['results']]

    def update_block_text(self, newText: str):
        resp = self.request(method="PATCH", url="/", data={"paragraph": Text(newText).to_dict()})
        return resp.is_success
