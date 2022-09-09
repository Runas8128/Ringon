"""Provides simple parser to Notion-API database query result object

This module has not only Parser object but also some pre-defined property types
so I recommend you to import module and Parser object independently.

Typical usage example:
    from pytion import parser, Parser, ...

    Database(dbID=...).query(
        filter=Filter(...),
        parser=Parser(pageID=parser.PageID, ID=parser.Number)
    )
"""

from dataclasses import dataclass

@dataclass
class Type:
    """`Type` indicator factory

    ### Attributes ::
        _type (str):
            name of type to be parsed
    """
    _type: str

    @property
    def type(self):
        """str: name of type to be parsed"""
        return self._type

    def __hash__(self):
        return hash(self._type)

Text = Type("Text")
Number = Type("Number")
Select = Type("Select")
PageID = Type("PageID")

def parse_richtext(richtext: dict):
    """parse one richtext object

    if richtext object has one of 'paragraph', 'title', 'rich_text',
    parse content of it.

    ### Args ::
        richtext (dict): richtext object to parse

    ### Returns ::
        first plain text of richtext object
        if given object is not richtext object, return empty string
    """
    if 'paragraph' in richtext:
        richtext = richtext['paragraph']
    if 'title' in richtext:
        richtext = richtext['title']
    if 'rich_text' in richtext:
        richtext = richtext['rich_text']

    try:
        return richtext[0]['plain_text']
    except IndexError:
        return ""

parser_map = {
    Text: parse_richtext,
    Number: lambda prop: prop['number'],
    Select: lambda prop: prop['select']['name']
}

# pylint: disable=redefined-builtin
def _parser_base(result: dict, name: str, type: Type):
    if not isinstance(type, Type):
        raise TypeError(type)

    if type == PageID:
        return result['id']

    if type in parser_map:
        return parser_map[type](result['properties'][name])

    raise NotImplementedError(type)

class Parser:
    """Notion-API object to python dictionary parser

    ### Args ::
        only_values (bool):
            if this flag is set, return only values by list.
            if not, return with provided name by dictionary.
            default value is False.
        **kwargs:
            keys to parse in query result.
            key should be match to property name in notion.

    ### Examples ::
        from pytion import parser, Parser, ...

        Database(dbID=...).query(
            filter=Filter(...),
            parser=Parser(pageID=parser.PageID, ID=parser.Number)
        )
    """
    def __init__(self, only_values: bool = False, **kwargs):
        self.func = self.parse_only_values if only_values else self.parse_with_key
        self.kwargs = kwargs

    def __call__(self, result: dict):
        return self.func(result)

    def parse_only_values(self, result: dict):
        """Parse only values by list."""
        data = [
            _parser_base(result, name, type)
            for name, type in self.kwargs.items()
        ]
        if len(data) == 1:
            data = data[0]
        return data

    def parse_with_key(self, result: dict):
        """Parse with provided name by dictionary."""
        return {
            name: _parser_base(result, name, type)
            for name, type in self.kwargs.items()
        }
