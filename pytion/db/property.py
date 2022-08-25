from dataclasses import dataclass

@dataclass
class BaseProperty:
    def to_dict(self):
        return { }

@dataclass
class RichText:
    text: str

    def to_dict(self):
        return [{ 'text': { 'content': self.text } }]

@dataclass
class Title(RichText, BaseProperty):
    def to_dict(self):
        data = super(Title, self).to_dict()
        return { 'title': data }

@dataclass
class Text(RichText, BaseProperty):
    def to_dict(self):
        data = super(Text, self).to_dict()
        return { 'rich_text': data }

@dataclass
class Select(BaseProperty):
    name: str
    
    def to_dict(self):
        return { 'select': { 'name': self.name } }

@dataclass
class Number(BaseProperty):
    number: float

    def to_dict(self):
        return { 'number': self.number }
