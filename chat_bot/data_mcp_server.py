import re
from datetime import datetime
from pathlib import Path

import pandas as pd
from mcp.server.fastmcp import FastMCP

mcp = FastMCP()
current_dir = Path(__file__).resolve().parent
df = pd.read_parquet(current_dir / "data_without_full_text.parquet")


def parse_zeitraum(zeitraum_str: str) -> tuple[datetime | None, datetime | None]:
    try:
        start_str, end_str = zeitraum_str.split(" - ")
        return (
            datetime.strptime(start_str.strip(), "%d.%m.%Y"),
            datetime.strptime(end_str.strip(), "%d.%m.%Y"),
        )
    except (ValueError, TypeError):
        return None, None


def normalize_string(s: str) -> str:
    if isinstance(s, str):
        return re.sub(r"[^a-zA-Z0-9]", "", s.lower())
    return ""


def convert_pandas_column_to_str(value: list | str) -> str:
    if isinstance(value, list):
        return normalize_string(";".join(value))
    if isinstance(value, str):
        return normalize_string(value)
    return normalize_string(str(value))


def matches_any_term(value: str | list, terms: list[str]) -> bool:
    norm_value = convert_pandas_column_to_str(value)
    return any(term in norm_value for term in terms)


# -------------------------------
# Example Idea Shop Chatbot Tools
# -------------------------------

@mcp.tool()
def get_all_shop_items() -> str:
    """Get all shop items with name, price, and artist."""
    if not all(col in df.columns for col in ["title", "price_in_euro", "artist"]):
        return "Required columns missing in dataset."
    return df[["title", "price_in_euro", "artist"]].to_json(orient="records")

@mcp.tool()
def get_items_by_artist(artists: list[str]) -> str:
    """Filter shop items by artist name."""
    norm_artists = [normalize_string(a) for a in artists]
    filtered_df = df[df["artist"].apply(lambda x: matches_any_term(x, norm_artists))]
    return filtered_df.to_json(orient="records")

@mcp.tool()
def get_items_by_price_range(min_price: float, max_price: float) -> str:
    """Filter shop items within a price range."""
    filtered_df = df[(df["price_in_euro"] >= min_price) & (df["price_in_euro"] <= max_price)]
    return filtered_df.to_json(orient="records")

@mcp.tool()
def get_items_by_category(categories: list[str]) -> str:
    """Filter shop items by category."""
    norm_categories = [normalize_string(c) for c in categories]
    filtered_df = df[df["category"].apply(lambda x: matches_any_term(x, norm_categories))]
    return filtered_df.to_json(orient="records")

@mcp.tool()
def search_items_by_keyword(keywords: list[str]) -> str:
    """Search for items by keywords in title or description."""
    norm_keywords = [normalize_string(k) for k in keywords]

    def matches_keyword(row):
        name_match = matches_any_term(row.get("title", ""), norm_keywords)
        desc_match = (
            matches_any_term(row.get("short_description", ""), norm_keywords) or
            matches_any_term(row.get("long_description", ""), norm_keywords)
        )
        return name_match or desc_match

    filtered_df = df[df.apply(matches_keyword, axis=1)]
    return filtered_df.to_json(orient="records")
