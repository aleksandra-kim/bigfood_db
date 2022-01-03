import bw2data as bd
from bw2io.utils import rescale_exchange
from copy import deepcopy


def create_location_mapping_glo(db1, db2_name):
    """
    Create mapping between unlinked exchanges of database `db1` and their corresponding activities in `db2`.
    Here an exchange in `db1` needs to be linked to activity in `db2` with location `GLO`, which does not exist there.
    Instead, there are activities with the same name but different locations, which constitute GLO location together.
    For example, CH + DE + RoW = GLO, where Rest of the World (RoW) basically adds whatever locations are missing to
    result in GLO. Hence, the mapping is from unlinked exchanges of `db1` and list of activities in `db2` with same name
    but multiple locations.
    Example: (market for lime, GLO) can be later split by production volume into
             (market for lime, RoW) & (market for lime, RER).
    Mapping is a list of dictionaries where each dictionary corresponds to an unlinked exchange.
    The key is the (name, location) tuple of the unlinked exchange in `db`` and the values are `db2` activities.

    """

    db2 = bd.Database(db2_name)
    unlinked_list = [act for act in db1.unlinked if act['type'] == 'technosphere' and act.get('location') == "GLO"]
    mapping = []
    for i, activity in enumerate(unlinked_list):
        new_el = {}
        name = activity['name']
        loc = activity['location']
        acts_codes = [(db2_name, act['code']) for act in db2 if name == act['name']]
        if len(acts_codes) > 0:
            new_el[(name, loc)] = acts_codes
            mapping.append(new_el)
    return mapping


def create_location_mapping_rer(db1, db2_name):
    """
    Create mapping between unlinked exchanges of database `db1` and their corresponding activities in `db2`.
    Here an exchange in `db1` needs to be linked to activity in `db2` with location `RER` (Europe), which does not exist
    there. Instead, there are 2 activities with the same name but locations `Europe without XX` and `XX`, where
    XX is some country. Locations can also be given as `RER w/o XX` and `X`.
    For example, Europe without Austria + AT = RER (Europe). Hence, the mapping is from unlinked exchanges of `db1`
    and list of activities in `db2` with same name and 2 locations.
    Example: (market for lime, RER) can be later split by production volume into
             (market for lime, AT) & (market for lime, Europe without Austria).
    Mapping is a list of dictionaries where each dictionary corresponds to an unlinked exchange.
    The key is the (name, location) tuple of the unlinked exchange in `db`` and the values are `db2` activities.

    """

    db2 = bd.Database(db2_name)
    unlinked_list = [act for act in db1.unlinked if act['type'] == 'technosphere' and act.get('location') == "RER"]
    mapping = []
    import country_converter as coco
    for i, activity in enumerate(unlinked_list):
        new_el = {}
        name = activity['name']
        loc = activity['location']
        for rer_wo_string in ["Europe without ", "RER w/o "]:
            act_rer_wo_xx = [
                act for act in db2 if name == act['name'] and rer_wo_string in act['location']
            ]
            # if len(act_rer_wo_xx) >= 1:
            #     print(act_rer_wo_xx)
            if len(act_rer_wo_xx) == 1:
                act_rer_wo_xx = act_rer_wo_xx[0]
                xx_location_long = act_rer_wo_xx['location'].replace(rer_wo_string, "")
                xx_location_iso2 = coco.convert(names=xx_location_long, to='ISO2')
                act_xx = [act for act in db2 if name == act['name'] and xx_location_iso2 == act['location']]
                assert len(act_xx) == 1
                act_xx = act_xx[0]
                new_el[(name, loc)] = [
                    (db2_name, act_rer_wo_xx['code']),
                    (db2_name, act_xx['code'])
                ]
                mapping.append(new_el)
    return mapping


def get_activities_for_allocation(mapping, db2_name):
    """
    Function that adds production volume share to activities in the mapping. Needed for allocation.

    """

    acitivities_with_allocation = {}
    for dict_ in mapping:
        key = list(dict_.keys())[0]
        mapped_activities = list(dict_.values())[0]
        total_volume = 0
        data = []
        for db_code in mapped_activities:
            activity = bd.get_activity(db_code)
            production_exchange = next(item for item in activity.exchanges() if item['type'] == 'production')
            production_volume = production_exchange['production volume']
            data.append(
                {
                    'name': activity['name'],
                    'reference product': activity['reference product'],
                    'location': activity['location'],
                    'production volume share': production_volume,
                    'unit': activity['unit'],
                    'database': db2_name,
                    'type': 'technosphere'
                }
            )
            total_volume += production_volume
        #         print(production_volume)
        #     print(total_volume)
        #     print()
        for d in data:
            d["production volume share"] /= total_volume
        acitivities_with_allocation[key] = data
    return acitivities_with_allocation


def modify_exchanges(db1, mapping, db2_name):
    """
    Function that rescales exchanges in `db1.data` based on their production volume shares.

    """

    db1_copy = deepcopy(db1)
    activities_to_allocate = get_activities_for_allocation(mapping, db2_name)

    for i, act in enumerate(db1_copy.data):
        exchanges = deepcopy(act.get("exchanges", []))
        modified_exchanges = []
        for j, exc in enumerate(exchanges):
            if (exc['name'], exc.get('location', None)) in list(activities_to_allocate.keys()):
                for act_to_allocate_db1, acts_db2 in activities_to_allocate.items():
                    if (exc['name'], exc.get('location', None)) == act_to_allocate_db1:
                        for act_db2 in acts_db2:
                            modified_exchange = deepcopy(exc)
                            modified_exchange['location'] = act_db2['location']
                            modified_exchanges.append(
                                rescale_exchange(modified_exchange, act_db2['production volume share'])
                            )
            else:
                modified_exchanges.append(exc)
        # if len(exchanges) != len(modified_exchanges):
        #     print(i, len(exchanges), len(modified_exchanges))
        db1.data[i]['exchanges'] = modified_exchanges
    return db1
