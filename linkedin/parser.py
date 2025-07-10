# linkedin/parser.py
"""
Detect UK-based LinkedIn locations.

• A single, pre-compiled regex (`UK_REGEX`) matches
  >  – four nations  | UK / GB
  >  – “Greater …” metros
  >  – all large UK towns & cities
  >  – English/Welsh counties
• `_clean_location()` removes noisy lines (“Member’s …”, “Connected …”, etc.)
• `filter_uk_connections()` keeps only dicts that match the regex.
"""

from __future__ import annotations
import re

# ─────────────────────────────────────────────────────────────
# 1.  keyword set → regex
# ─────────────────────────────────────────────────────────────
UK_KEYWORDS: set[str] = {
    # Nations / generic
    "united kingdom", "uk", "g.b.", "gb",
    "england", "scotland", "wales", "northern ireland",

    # “Greater …”
    "greater london", "greater manchester", "greater birmingham",
    "greater glasgow", "greater liverpool", "greater leeds",
}

# English / Welsh counties (selection)
UK_KEYWORDS.update({
    "west midlands", "west yorkshire", "south yorkshire", "merseyside",
    "greater manchester", "tyne and wear", "kent", "surrey", "essex",
    "lancashire", "cheshire", "staffordshire", "leicestershire",
    "cambridgeshire", "buckinghamshire", "oxfordshire", "berkshire",
    "norfolk", "suffolk", "lincolnshire", "hampshire", "dorset",
    "somerset", "devon", "cornwall", "durham", "north yorkshire",
    "cumbria", "nottinghamshire", "derbyshire", "gloucestershire",
    "northamptonshire", "bedfordshire", "hertfordshire", "warwickshire",
    "worcestershire", "shropshire", "rutland", "isle of wight",
    "ceredigion", "powys", "gwynedd", "flintshire", "conwy", "monmouthshire",
})

# Major towns & cities (abbreviated list – extend freely)
UK_KEYWORDS.update({
    "london", "birmingham", "manchester", "liverpool", "leeds",
    "sheffield", "bristol", "glasgow", "edinburgh", "cardiff",
    "belfast", "aberdeen", "newcastle upon tyne", "nottingham",
    "leicester", "coventry", "swansea", "portsmouth", "southampton",
    "oxford", "cambridge", "york", "norwich", "bath", "exeter",
    "reading", "milton keynes", "luton", "wolverhampton", "derby",
    "plymouth", "stoke-on-trent",
})

UK_REGEX = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in sorted(UK_KEYWORDS, key=len, reverse=True)) + r")\b",
    flags=re.IGNORECASE,
)

# ─────────────────────────────────────────────────────────────
# 2.  helper – strip noise from the card’s details blob
# ─────────────────────────────────────────────────────────────
_EXCLUDE_PREFIXES = ("member’s", "member's", "member’s name", "member’s occupation", "connected")

def _clean_location(raw: str) -> str:
    """
    Remove generic lines, return a single lower-case string suitable
    for regex matching.
    """
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    lines = [ln for ln in lines if not ln.lower().startswith(_EXCLUDE_PREFIXES)]
    return " ".join(lines).lower()


# ─────────────────────────────────────────────────────────────
# 3.  public API
# ─────────────────────────────────────────────────────────────
def filter_uk_connections(connections: list[dict]) -> list[dict]:
    """
    connections : list of dicts with at least a 'location' key (str).

    Returns only those whose cleaned location matches UK_REGEX.
    """
    result: list[dict] = []
    for conn in connections:
        clean_loc = _clean_location(conn["location"])
        if UK_REGEX.search(clean_loc):
            result.append(conn)
    print(f"[INFO] Filtered {len(result)} UK-based connections.")
    return result
