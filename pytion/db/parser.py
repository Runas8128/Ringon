"""
parser=Parser(ID=Type.Number)
"""

from enum import Enum, auto

class Parser:
    class Type(Enum):
        Text = auto()
        Select = auto()
        Number = auto()
    
    def __init__(self, only_values: bool = False, **kwargs):
        self.func = self.parse_only_values if only_values else self.parse_with_key
        self.kwargs = kwargs
    
    def __call__(self, result: dict):
        return self.func(result)
    
    def parse_only_values(self, result: dict):
        properties = result['properties']
        data = []

        for name in self.kwargs.keys():
            type = self.kwargs[name]
            if not isinstance(type, Type):
                raise TypeError(type)

            try:
                prop = properties[name]
            except KeyError as E:
                raise ValueError(name) from E
            
            if type == Type.Text:
                prop = prop.get('title', prop).get('rich_text', prop)
                data.append(prop[0]['plain_text'])
            elif type == Type.Select:
                data.append(prop['select']['name'])
            elif type == Type.Number:
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

            try:
                prop = properties[name]
            except KeyError as E:
                raise ValueError(name) from E
            
            if type == Type.Text:
                prop = prop.get('title', prop).get('rich_text', prop)
                data[name] = prop[0]['plain_text']
            elif type == Type.Select:
                data[name] = prop['select']['name']
            elif type == Type.Number:
                data[name] = prop['number']
            else:
                raise NotImplementedError(type)
        
        if self.rstType == list:
            data = list(data.values())
        return data
