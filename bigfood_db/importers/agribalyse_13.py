from time import time
from copy import deepcopy

import bw2io as bi
import bw2data as bd
from bw2io.importers.base_lci import LCIImporter
from bw2io.importers import SimaProCSVImporter
from bw2io.strategies import update_ecoinvent_locations

from ..migrations import create_agribalyse_13_migrations

# Default name of the consumption database
CONSUMPTION_DB_NAME = 'swiss consumption 1.0'


class Agribalyse13Importer(LCIImporter):
    format = "Agribalyse 1.3 Simapro CSV"

    def __init__(
            self,
            directory,
            name="Agribalyse 1.3",
    ):
        self.directory = directory
        self.db_name = name
        ei_name = self.determine_ecoinvent_db_name()

        db = SimaProCSVImporter(self.directory, self.db_name)
        db.apply_strategies()
        create_agribalyse_13_migrations()
        db.migrate('simapro-ecoinvent-3.3')
        db.migrate('agribalyse-13-names')
        db.migrate('agribalyse-13-names-locations')
        db.migrate('agribalyse-13-names-refproducts')
        db.apply_strategy(update_ecoinvent_locations)

        db.match_database()
        db.match_database(ei_name, fields=['reference product', 'name', 'location', 'unit'])
        db.match_database(ei_name, fields=['name', 'location', 'unit'])
        db.match_database('biosphere3')
        self.data = db.data

    @staticmethod
    def determine_ecoinvent_db_name():
        """Function that naively determines how ecoinvent is called in a particular BW project."""
        ei_name = [db for db in bd.databases if 'ecoinvent' in db.lower()]
        assert len(ei_name) == 1
        return ei_name[0]
