"""
parser=Parser(ID=Type.Number)
"""

from dataclasses import dataclass

@dataclass
class Type:
    _type: str
    
    @property
    def type(self):
        return self._type

Text = Type("Text")
Number = Type("Number")
Select = Type("Select")
PageID = Type("PageID")

def parse_richText(rich_text: dict):
    if 'paragraph' in rich_text.keys():
        rich_text = rich_text['paragraph']
    if 'title' in rich_text.keys():
        rich_text = rich_text['title']
    if 'rich_text' in rich_text.keys():
        rich_text = rich_text['rich_text']
    
    try:
        return rich_text[0]['plain_text']
    except IndexError:
        return ""

parser_map = {
    Text: parse_richText,
    Number: lambda prop: prop['number'],
    Select: lambda prop: prop['select']['name']
}

def _parser_base(result: dict, name: str, type: Type):
    if not isinstance(type, Type):
        raise TypeError(type)
    
    if type == PageID:
        return result['id']
    
    properties = result['properties']
    if type in parser_map.keys():
        return parser_map[type](result['properties'][name])
    else:
        raise NotImplementedError(type)

class Parser:
    def __init__(self, only_values: bool = False, **kwargs):
        self.func = self.parse_only_values if only_values else self.parse_with_key
        self.kwargs = kwargs
    
    def __call__(self, result: dict):
        return self.func(result)
    
    def parse_only_values(self, result: dict):
        data = [_parser_base(result, name, self.kwargs[name]) for name in self.kwargs.keys()]
        if len(data) == 1: data = data[0]
        return data

    def parse_with_key(self, result: dict):
        return {name: _parser_base(result, name, self.kwargs[name]) for name in self.kwargs.keys()}
