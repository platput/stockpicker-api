from pydantic import BaseModel


def to_camel(string: str) -> str:
    converted = ''.join(word.capitalize() for word in string.split('_'))
    return converted[0].lower() + converted[1:]


class SectorDetails(BaseModel):
    sector_name: str
    sector_details_url: str

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True

