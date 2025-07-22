from typing import Literal
from pydantic import BaseModel


# 🎨 Allowed artefact categories from your image
ArtefactCategory: type = Literal[
    "Paintings",
    "Photography",
    "Sculptures",
    "Crafts",
]


# 🧑‍🎨 Optional artist roles
ArtistRole: type = Literal[
    "Painter",
    "Photographer",
    "Sculptor",
    "Crafts Artist",
]


class Artefact(BaseModel):
    """Artefact / artwork metadata model."""

    title: str
    artist: str
    year_created: int
    medium: str
    short_description: str
    long_description: str
    category: list[ArtefactCategory]
    artist_role: ArtistRole
    price_in_euro: float
    available: bool
    exhibition_location: str
    exhibition_date: str  # Format: "YYYY-MM-DD"
    is_limited_edition: bool
    edition_number: int | None
    tags: list[str]
    previous_work_title: str | None


class ArtefactWithFullText(Artefact):
    """Artefact model including full catalog/display text."""

    full_text: str
