import bw2io as bi
import bw2data as bd

# Local files
from bigfood_db.import_databases import import_ecoinvent
from bigfood_db.importers import Agribalyse13Importer


if __name__ == '__main__':
    project = "Food ei38"
    bd.projects.set_current(project)

    ei_path = "/Users/akim/Documents/LCA_files/ecoinvent_38_cutoff/datasets"
    ei_name = "ecoinvent 3.8 cutoff"

    bi.bw2setup()
    b3 = bd.Database('biosphere3')
    import_ecoinvent(ei_path, ei_name)
    ei = bd.Database(ei_name)

    ag_path = "/Users/akim/Documents/LCA_files/agribalyse_13/Agribalyse CSV FINAL_no links_Nov2016v3.CSV"
    ag_name = "Agribalyse 1.3"
    ag = Agribalyse13Importer(ag_path, ag_name)
    ag.statistics()

    print([act['location'] for act in ei if 'market group for electricity' in act['name']])