"""WHADID I DO?! for Tired But Here (tag "drop 002"): tee, women's tee and back-print hoodie, Black.

Uses create_brand.py's product builder with its own tags and progress file (printify/whadid.json).
Art: designs/print-brand/08-whadid-i-do.png (owner's edit with the jersey logo removed, upscaled 4x, 300 DPI).

Usage: python3 printify/create_whadid.py --commit SHA
"""
from pathlib import Path
import create_brand as brand
import create_brand2  # noqa: F401  (sets the product kinds: tee, women's tee, back-print hoodie)

brand.OUT = Path(__file__).with_name("whadid.json")
brand.BASE_TAGS = ["drop 002", "funny", "party", "graphic tee"]
brand.DESIGNS = [
    ("08-whadid-i-do", "WHADID I DO?!", ["hangover", "party", "beer", "retro"],
     "Bubbly 90s lettering asks the only question that matters the morning after, over a goggled, tongue-out "
     "party legend in an orange mesh jersey, a beer in each hand.", "No regrets. Some questions."),
]

if __name__ == "__main__":
    brand.main()
