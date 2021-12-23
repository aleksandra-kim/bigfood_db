from bw2io import Migration

from .data import (
    get_agribalyse_13_data,
)


def create_agribalyse_13_migrations():
    """Function that creates migrations for the agribalyse 1.3 database."""
    Migration("agribalyse-13").write(
        get_agribalyse_13_data(),
        "Change names in Agribalyse 1.3",
    )
