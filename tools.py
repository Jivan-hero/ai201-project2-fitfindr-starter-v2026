"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import re

import config
from generate import generate
from utils.data_loader import load_listings


def _terms(value: object) -> set[str]:
    """Normalize searchable text into whole lowercase alphanumeric terms."""
    return set(re.findall(r"[a-z0-9]+", str(value).lower()))


def _size_matches(requested: str, listing_size: str) -> bool:
    """Match complete size tokens instead of unsafe substring matches."""
    wanted = requested.strip().lower()
    available = _terms(listing_size)
    aliases = {
        "small": "s",
        "medium": "m",
        "large": "l",
        "xlarge": "xl",
        "extra-large": "xl",
    }
    wanted = aliases.get(wanted, wanted)
    return wanted in available


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    query_terms = _terms(description)
    stopwords = {
        "a", "an", "and", "for", "i", "in", "is", "item", "looking",
        "me", "of", "please", "some", "the", "to", "want", "with",
    }
    query_terms -= stopwords

    ranked: list[tuple[int, float, dict]] = []
    for listing in load_listings():
        if max_price is not None and float(listing["price"]) > float(max_price):
            continue
        if size and not _size_matches(size, str(listing["size"])):
            continue

        title_terms = _terms(listing["title"])
        tag_terms = _terms(" ".join(listing.get("style_tags", [])))
        color_terms = _terms(" ".join(listing.get("colors", [])))
        detail_terms = _terms(
            " ".join(
                str(listing.get(field) or "")
                for field in ("description", "category", "brand", "platform")
            )
        )

        # Titles and style tags are stronger signals than incidental words in
        # the long description, so they receive a higher transparent weight.
        score = (
            4 * len(query_terms & title_terms)
            + 3 * len(query_terms & tag_terms)
            + 2 * len(query_terms & color_terms)
            + len(query_terms & detail_terms)
        )
        if score:
            ranked.append((score, float(listing["price"]), listing))

    ranked.sort(key=lambda entry: (-entry[0], entry[1], entry[2]["id"]))
    return [listing for _, _, listing in ranked[: config.SEARCH_RESULT_LIMIT]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    if not new_item:
        return "I need a selected listing before I can suggest an outfit."

    item_summary = (
        f"{new_item.get('title')} | colors: {', '.join(new_item.get('colors', []))} | "
        f"style: {', '.join(new_item.get('style_tags', []))} | "
        f"size: {new_item.get('size')}"
    )
    items = wardrobe.get("items", []) if isinstance(wardrobe, dict) else []

    if items:
        wardrobe_lines = []
        for item in items:
            wardrobe_lines.append(
                f"- {item.get('name')} ({item.get('category')}; "
                f"colors: {', '.join(item.get('colors', []))}; "
                f"style: {', '.join(item.get('style_tags', []))})"
            )
        prompt = (
            f"New thrift find:\n{item_summary}\n\nUser wardrobe:\n"
            + "\n".join(wardrobe_lines)
            + "\n\nSuggest one or two complete outfits. Name the exact saved wardrobe "
              "pieces you use and briefly explain why they work together."
        )
    else:
        prompt = (
            f"New thrift find:\n{item_summary}\n\nThe user has no saved wardrobe "
            "items yet. Give one or two practical general styling ideas and name "
            "the basic pieces they could pair with it."
        )

    return generate(
        prompt,
        system=(
            "You are a concise thrift stylist. Ground every suggestion in the "
            "item details supplied. Do not invent pieces in the saved wardrobe."
        ),
    )


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    if not outfit or not outfit.strip():
        return "I need an outfit suggestion before I can create a fit card."
    if not new_item:
        return "I need a selected listing before I can create a fit card."

    prompt = (
        f"Selected item: {new_item.get('title')}\n"
        f"Price: ${float(new_item.get('price', 0)):.2f}\n"
        f"Platform: {new_item.get('platform')}\n"
        f"Style tags: {', '.join(new_item.get('style_tags', []))}\n"
        f"Outfit plan: {outfit}\n\n"
        "Write a 2-to-4 sentence social caption. Mention the selected item, its "
        "price, and its platform exactly once each. Make the styling vibe "
        "specific and natural, not like a product listing."
    )
    return generate(
        prompt,
        system="You write concise, useful, non-hyped thrift outfit captions.",
    )
