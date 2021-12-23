import bw2data as bd
import bw2io as bi

from .importers import Agribalyse13Importer


def import_ecoinvent(ei_path, ei_name):
    if ei_name in bd.databases:
        print(ei_name + " database already present!!! No import is needed")
    else:
        ei = bi.SingleOutputEcospold2Importer(ei_path, ei_name)
        ei.apply_strategies()
        ei.match_database(db_name='biosphere3', fields=('name', 'category', 'unit', 'location'))
        ei.statistics()
        ei.write_database()


def import_agribalyse_13(ag_path, ag_name="Agribalyse 1.3", ei_name=None):
    if ag_name in bd.databases:
        print(ei_name + " database already present!!! No import is needed")
    else:
        ag = Agribalyse13Importer()
        # ag.match_database()
        # ag.match_database(db_name='biosphere3', fields=('name', 'category', 'unit', 'location'))
        # ag.match_database(db_name=ei_name, fields=('name', 'unit', 'reference product', 'location'))

        assert ag.statistics()[2] == 0  # TODO where's all_linked property? check bw2io version
        ag.apply_strategies()
        ag.statistics()
        ag.write_database()