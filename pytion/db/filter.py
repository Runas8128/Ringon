"""
filter=Filter(name=Text(contains=kw))
"""

from typing import Optional, Union
from dataclasses import dataclass

Data = Union[str, int, bool]

@dataclass
class BaseOption:
    def to_dict(self):
        return { }

@dataclass
class SupportEquals(BaseOption):
    equals:         Optional[Data] = None
    does_not_equal: Optional[Data] = None

    def to_dict(self):
        data = super(SupportEquals, self).to_dict()
        if self.equals:         data['equals']          = self.equals
        if self.does_not_equal: data['does_not_equal']  = self.does_not_equal
        return data

@dataclass
class SupportContains(BaseOption):
    contains:           Optional[Data] = None
    does_not_contain:   Optional[Data] = None

    def to_dict(self):
        data = super(SupportContains, self).to_dict()
        if self.contains:           data['contains']            = self.contains
        if self.does_not_contain:   data['does_not_contain']    = self.does_not_contain
        return data

@dataclass
class SupportIsEmpty(BaseOption):
    is_empty:       Optional[bool] = None
    is_not_empty:   Optional[bool] = None

    def to_dict(self):
        data = super(SupportIsEmpty, self).to_dict()
        if self.is_empty:       data['is_empty']        = self.is_empty
        if self.is_not_empty:   data['is_not_empty']    = self.is_not_empty
        return data

@dataclass
class Text(SupportEquals, SupportContains, SupportIsEmpty):
    starts_with:    Optional[str] = None
    ends_with:      Optional[str] = None

    def to_dict(self):
        data = super(Text, self).to_dict()
        if self.starts_with:    data['starts_with'] = self.starts_with
        if self.ends_with:      data['ends_with']   = self.ends_with
        return { 'rich_text': data }

@dataclass
class Number(SupportEquals, SupportIsEmpty):
    greater_than:               Optional[float] = None
    greater_than_or_equal_to:   Optional[float] = None
    less_than:                  Optional[float] = None
    less_than_or_equal_to:      Optional[float] = None

    def to_dict(self):
        data = super(Number, self).to_dict()
        if self.greater_than:
            data['greater_than']                = self.greater_than
        if self.greater_than_or_equal_to:
            data['greater_than_or_equal_to']    = self.greater_than_or_equal_to
        if self.less_than:
            data['less_than']                   = self.less_than
        if self.less_than_or_equal_to:
            data['less_than_or_equal_to']       = self.less_than_or_equal_to
        return { 'number': data }

@dataclass
class Select(SupportEquals, SupportIsEmpty):
    def to_dict(self):
        data = super(Select, self).to_dict()
        return { 'select': data }

class Filter:
    def __init__(self, rule: str="and", **kwargs: BaseOption):
        self.kwargs = kwargs
    
    def _to_dict(self, key: str):
        data = { 'property': key }
        data.update(self.kwargs[key].to_dict())
        return data
    
    def to_dict(self):
        ls = [ self._to_dict(key) for key in self.kwargs.keys() ]
        if len(ls) == 0:    return None
        elif len(ls) == 1:  return ls[0]
        else:
            if rule not in ('and', 'or'): raise ValueError(rule)
            return { rule: ls }
