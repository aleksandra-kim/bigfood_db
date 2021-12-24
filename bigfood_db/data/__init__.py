from pathlib import Path
import json

dirpath = Path(__file__).parent.resolve()


def get_agribalyse_13_names_data():
    return json.load(
        open(dirpath / "migrations" / "agribalyse-13-names.json")
    )


def get_agribalyse_13_names_locations_data():
    return json.load(
        open(dirpath / "migrations" / "agribalyse-13-names-locations.json")
    )

def get_agribalyse_13_names_refproducts_data():
    return json.load(
        open(dirpath / "migrations" / "agribalyse-13-names-refproducts.json")
    )
