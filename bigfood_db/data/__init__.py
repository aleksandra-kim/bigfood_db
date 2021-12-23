from pathlib import Path
import json

dirpath = Path(__file__).parent.resolve()


def get_agribalyse_13_data():
    return json.load(
        open(dirpath / "migrations" / "agribalyse-13.json")
    )
