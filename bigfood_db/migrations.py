from bw2io import Migration

from .data import (
    get_agribalyse_13_names_data,
    get_agribalyse_13_names_locations_data,
    get_agribalyse_13_names_refproducts_data,
)


def create_agribalyse_13_migrations():
    """Function that creates migrations for the agribalyse 1.3 database."""
    Migration("agribalyse-13-names").write(
        get_agribalyse_13_names_data(),
        "Change names in Agribalyse 1.3",
    )
    Migration("agribalyse-13-names-locations").write(
        get_agribalyse_13_names_locations_data(),
        "Change names and locations in Agribalyse 1.3",
    )
    Migration("agribalyse-13-names-refproducts").write(
        get_agribalyse_13_names_refproducts_data(),
        "Change names and reference products in Agribalyse 1.3",
    )
