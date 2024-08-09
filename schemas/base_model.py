from pydantic import BaseModel as PydanticBaseModel

def to_camel_case(s: str) -> str:
        parts = s.split('_')
        return parts[0] + ''.join(word.capitalize() for word in parts[1:])

class BaseModel(PydanticBaseModel):
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        alias_generator = to_camel_case