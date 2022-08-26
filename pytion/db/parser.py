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

class Parser:
    def __init__(self, only_values: bool = False, **kwargs):
        self.func = self.parse_only_values if only_values else self.parse_with_key
        self.kwargs = kwargs
    
    def __call__(self, result: dict):
        return self.func(result)
    
    def parse_only_values(self, result: dict):
        properties = result['properties']
        data = []

        for name in self.kwargs.keys():
            type: Type = self.kwargs[name]
            if not isinstance(type, Type):
                raise TypeError(type)
            
            if type == PageID:
                data.append(result['id'])
                continue

            try:
                prop = properties[name]
            except KeyError as E:
                raise ValueError(name) from E
            
            if type == Text:
                if 'title' in prop: prop = prop['title']
                if 'rich_text' in prop: prop = prop['rich_text']
                data.append(prop[0]['plain_text'])
            elif type == Select:
                data.append(prop['select']['name'])
            elif type == Number:
                data.append(prop['number'])
            else:
                raise NotImplementedError(type)
        
        if len(data) == 1: data = data[0]
        return data

    def parse_with_key(self, result: dict):
        properties = result['properties']
        data = {}

        for name in self.kwargs.keys():
            type = self.kwargs[name]
            if not isinstance(type, Type):
                raise TypeError(type)
            
            if type == PageID:
                data[name] = result['id']
                continue

            try:
                prop = properties[name]
            except KeyError as E:
                raise ValueError(name) from E
            
            if type == Text:
                if 'title' in prop: prop = prop['title']
                if 'rich_text' in prop: prop = prop['rich_text']
                data[name] = prop[0]['plain_text']
            elif type == Select:
                data[name] = prop['select']['name']
            elif type == Number:
                data[name] = prop['number']
            else:
                raise NotImplementedError(type)
        
        return data
