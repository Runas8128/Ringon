"""Indicates `Filter` for querying notion database

This module has not only Filter object but also filtering options,
so I recommend you to import module and Filter object independently.

Typical usage example:
    from pytion import filter, Filter, ...

    Database(dbID=...).query(
        filter=Filter(
            rule='or',
            ID=filter.Number(equals=8128), name=filter.Text(equals='Runas')
        ),
        parser=Parser(...)
    )
"""

from typing import Optional, Generic, TypeVar
from dataclasses import dataclass

Data = TypeVar('Data', str, float, bool)

@dataclass
class BaseOption:
    """Base class for indicating `option`"""

    def to_dict(self):
        """Converts this option object into a dict.

        Classes that inherits `BaseOption` class should override this method.

        ### Returns::
            Packed not-None properties of self as dictionary
        """
        return { }

@dataclass
class SupportEquals(BaseOption, Generic[Data]):
    """Generic base class that supports 'equal' property for data type `Data`

    ### Attributes::
        equals (Data, optional):
            Indicates 'equals' option in notion.
        does_not_equal (Data, optional):
            Indicates 'does_not_equal' option in notion.
    """
    equals:         Optional[Data] = None
    does_not_equal: Optional[Data] = None

    def to_dict(self):
        data = super(SupportEquals, self).to_dict()
        if self.equals:
            data['equals']          = self.equals
        if self.does_not_equal:
            data['does_not_equal']  = self.does_not_equal
        return data

@dataclass
class SupportContains(BaseOption, Generic[Data]):
    """Generic base class that supports 'contain' property for data type `Data`

    ### Attributes::
        contains (Data, optional):
            Indicates 'contains' option in notion.
        does_not_contain (Data, optional):
            Indicates 'does_not_contain' option in notion.
    """
    contains:           Optional[Data] = None
    does_not_contain:   Optional[Data] = None

    def to_dict(self):
        data = super(SupportContains, self).to_dict()
        if self.contains:
            data['contains']            = self.contains
        if self.does_not_contain:
            data['does_not_contain']    = self.does_not_contain
        return data

@dataclass
class SupportIsEmpty(BaseOption):
    """Base class that supports 'is_empty' property

    ### Attributes::
        is_empty (bool, optional):
            Indicates 'is_empty' option in notion.
        is_not_empty (bool, optional):
            Indicates 'is_not_empty' option in notion.
    """
    is_empty:       Optional[bool] = None
    is_not_empty:   Optional[bool] = None

    def to_dict(self):
        data = super(SupportIsEmpty, self).to_dict()
        if self.is_empty:
            data['is_empty']        = self.is_empty
        if self.is_not_empty:
            data['is_not_empty']    = self.is_not_empty
        return data

@dataclass
class Text(SupportEquals[str], SupportContains[str], SupportIsEmpty):
    """Class that provides option object for text comparers

    ### Attributes::
        equals (str, optional):
            Indicates 'equals' option in notion.
        does_not_equal (str, optional):
            Indicates 'does_not_equal' option in notion.
        contains (str, optional):
            Indicates 'contains' option in notion.
        does_not_contain (str, optional):
            Indicates 'does_not_contain' option in notion.
        is_empty (bool, optional):
            Indicates 'is_empty' option in notion.
        is_not_empty (bool, optional):
            Indicates 'is_not_empty' option in notion.
        starts_with (str, optional):
            Indicates 'starts_with' option in notion.
        ends_with (str, optional):
            Indicates 'ends_with' option in notion.
    """

    starts_with:    Optional[str] = None
    ends_with:      Optional[str] = None

    def to_dict(self):
        data = super(Text, self).to_dict()
        if self.starts_with:
            data['starts_with'] = self.starts_with
        if self.ends_with:
            data['ends_with']   = self.ends_with
        return { 'rich_text': data }

@dataclass
class Number(SupportEquals[float], SupportIsEmpty):
    """Class that provides option object for number comparers

    ### Attributes::
        equals (float, optional):
            Indicates 'equals' option in notion.
        does_not_equal (float, optional):
            Indicates 'does_not_equal' option in notion.
        is_empty (bool, optional):
            Indicates 'is_empty' option in notion.
        is_not_empty (bool, optional):
            Indicates 'is_not_empty' option in notion.
        greater_than (float, optional):
            Indicates 'greater_than' option in notion.
        greater_than_or_equal_to (float, optional):
            Indicates 'greater_than_or_equal_to' option in notion.
        less_than (float, optional):
            Indicates 'less_than' option in notion.
        less_than_or_equal_to (float, optional):
            Indicates 'less_than_or_equal_to' option in notion.
    """

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
class Select(SupportEquals[str], SupportIsEmpty):
    """Class that provides option object for select comparers

    ### Attributes::
        equals (str, optional):
            Indicates 'equals' option in notion.
        does_not_equal (str, optional):
            Indicates 'does_not_equal' option in notion.
        is_empty (bool, optional):
            Indicates 'is_empty' option in notion.
        is_not_empty (bool, optional):
            Indicates 'is_not_empty' option in notion.
    """

    def to_dict(self):
        data = super(Select, self).to_dict()
        return { 'select': data }

class Filter:
    """Class that indicates `Filter` object for querying notion database

    ### Args ::
        rule (str):
            Chaining rule for provided options.
            This should be either 'and' or 'or'
            Default value is 'and'.
        **kwargs:
            Options to filter objects.

    ### Raises ::
        ValueError: rule is neither 'and' nor 'or'

    ### Examples ::
        from pytion import filter, Filter, ...

        Database(dbID=...).query(
            filter=Filter(
                rule='or',
                ID=filter.Number(equals=8128), name=filter.Text(equals='Runas')
            ),
            parser=Parser(...)
        )
    """

    def __init__(self, rule: str = "and", **kwargs: BaseOption):
        if rule not in ('and', 'or'):
            raise ValueError(rule)
        self.rule = rule
        self.kwargs = kwargs

    def _to_dict(self, key: str):
        data = { 'property': key }
        data.update(self.kwargs[key].to_dict())
        return data

    def to_dict(self):
        """Converts this filter object into notion API style json object."""

        data = [self._to_dict(key) for key in self.kwargs]

        if len(data) == 0:
            return None
        elif len(data) == 1:
            return data[0]
        else:
            return { self.rule: data }
