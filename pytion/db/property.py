"""Provides basic property object for Notion API.

This module has only the options, and it's value.

Typical usage example:
    from pytion import property as prop, ...

    Database(...).append(
        title=prop.Title(text="This is title"),
        property=prop.Text(text="Hello?")
    )
"""

from dataclasses import dataclass

@dataclass
class BaseProperty:
    """Base class for indicating `property`"""

    def to_dict(self):
        """Converts this property object into a dict.

        Classes that inherits `BaseProperty` class should override this method.

        ### Returns::
            Packed not-None properties of self as dictionary
        """
        return { }

@dataclass
class RichText:
    """Base class for richtext.

    By inheriting this, you can simply use `RichText.to_dict()`
    to get jsonified richtext object.

    ### NOTE::
        You should not use instance of this class to indicate property.
    """
    text: str

    def to_dict(self):
        """Converts provided text into richtext object.

        ### Returns::
            Packed richtext object
        """
        return [{ 'text': { 'content': self.text } }]

@dataclass
class Title(RichText, BaseProperty):
    """Class indicating title object.

    This class inherits RichText since title object is notated with richtext internally.
    """
    def to_dict(self):
        data = super(Title, self).to_dict()
        return { 'title': data }

@dataclass
class Text(RichText, BaseProperty):
    """Class indicating text object.

    This class inherits RichText since text object is notated with richtext internally.
    """
    def to_dict(self):
        data = super(Text, self).to_dict()
        return { 'rich_text': data }

@dataclass
class Select(BaseProperty):
    """Class indicating select object."""
    name: str

    def to_dict(self):
        return { 'select': { 'name': self.name } }

@dataclass
class Number(BaseProperty):
    """Class indicating number object."""
    number: float

    def to_dict(self):
        return { 'number': self.number }
