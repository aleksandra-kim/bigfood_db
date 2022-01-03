import bw2data as bd
from bw2io.utils import rescale_exchange
from copy import deepcopy


def create_location_mapping(db1, db2_name):
    """
    Create mapping between unlinked exchanges of database `db1` and their corresponding activities in `db2`.
    Here an exchange in `db1` needs to be linked to activity in `db2` with location `GLO`, which does not exist there.
    Instead, there are activities with the same name but different locations, which constitute GLO location together.
    For example, CH + DE + RoW = GLO, where Rest of the World (RoW) basically adds whatever locations are missing to
    result in GLO. Hence, the mapping is from unlinked exchanges of `db1` and list of activities in `db2` with same name
    but multiple locations.
    Example: (market for lime, GLO) is split by production volume into
             (market for lime, RoW) & (market for lime, RER).
    Mapping is a list of dictionaries where each dictionary corresponds to an unlinked exchange.
    The key is the index of the unlinked exchange in `db`` and the values are `db2` activities codes.
    """
    db2 = bd.Database(db2_name)
    unlinked_list = [act for act in db1.unlinked if act['type'] == 'technosphere' and act.get('location') == "GLO"]
    mapping = [0]*len(unlinked_list)
    for i, activity in enumerate(unlinked_list):
        new_el = {}
        name = activity['name']
        loc = activity['location']
        acts_codes = [act['code'] for act in db2 if name == act['name']]
        new_el[(name, loc)] = acts_codes
        mapping[i] = new_el
    return mapping


def get_allocated_excs(db1, mapping, db2_name):
    """
    Function that generates list of exchanges with
    Each "inner" list contains dictionaries of exchanges in the correct format.
    By correct format we mean the one consistent with the format of exchanges
    in the (not written yet) consumption database (see eg co.data[0]['exchanges']).
    We exclude amounts for now and instead add field 'production volume share'

    Attributes
    ----------
    db1 : object
        Brightway database
    mapping : list of dictionaries
        Each dictionary corresponds to an unlinked exchange with
            key = index of the unlinked exchange in `list(db1.unlinked)`
            values = codes of corresponding activities
    db2_name : name of the database to link to

    Returns
    -------
    unlinked_list_used : list
        List of unlinked exchanges that are actually present in the mapping.
    allocated_excs : list of lists
        Each inner list contains exchanges dictionaries

    """

    unlinked_list = [act for act in db1.unlinked if act['type'] == 'technosphere' and act.get('location')]
    len_unlinked = len(unlinked_list)

    unlinked_names_loc = [0]*len_unlinked
    for i in range(len_unlinked):
        unlinked_names_loc[i] = (unlinked_list[i]['name'], unlinked_list[i]['location'])

    unlinked_list_used = []
    allocated_excs = []

    for m in range(len(mapping)):
        try:
            # If current element from mapping is in unlinked exchanges, save it in `unlinked_list_used`
            index = unlinked_names_loc.index(list(mapping[m].keys())[0])
            unlinked_list_used.append(unlinked_list[index])

            # Change exchanges of the current activity if some of them are unlinked.
            # Involves adding new allocation exchanges to `allocated_excs` and adding field `production volume share`
            new_exchanges = []
            vols = 0
            codes = list(mapping[m].values())[0]
            for code in codes:
                act = bd.get_activity((db2_name, code))
                production_exc = next(item for item in act.exchanges() if item['type'] == 'production')
                vol = production_exc['production volume']
                vols += vol
                exc = deepcopy(unlinked_list[index])
                # Update some values to be consistent with db_name
                exc2 = {'name': act['name'],
                        'reference product': act['reference product'],
                        'location': act['location'],
                        'production volume share': vol,
                        'unit': act['unit'],
                        'database': db2_name,
                        'type': 'technosphere'}
                exc.update(exc2)

                new_exchanges.append(exc)

            for exc in new_exchanges:
                exc['production volume share'] /= vols

            allocated_excs.append(new_exchanges)

        except ValueError:
            pass

    return unlinked_list_used, allocated_excs


def compare_exchanges(exc1, exc2, db_name):
    """Function that compares two exchanges based on certain fields. Return True if exchanges are the same."""

    # Do not consider biosphere exchanges
    if exc1['type'] == 'biosphere' or exc2['type'] == 'biosphere':
        return False

    # Do not need to consider exchanges that are not in the database we're linking to
    try:
        if exc1['input'][0] != db_name:
            return False
    except:
        pass

    # Compare exchanges based on their dictionary fields
    fields_to_compare = ['name', 'location', 'unit', 'type']
    same = all([exc1[f] == exc2[f] for f in fields_to_compare])

    return same


def modify_exchanges(db1, mapping, db2_name):
    """
    Change exchanges of activities if they are unlinked, adjust their amount based on `production volume share` field.
    TODO: change the code to removing unlinked exchanges instead of adding them - line 121-...
    TODO: uncertainty info is not scaled!!!
    """

    db1 = deepcopy(db1)
    unlinked_list_used, allocated_excs = get_allocated_excs(db1, mapping, db2_name)
    for act in db1.data:
        try:
            exchanges = deepcopy(act['exchanges'])
            new_exchanges = []

            for exc in exchanges:

                ind = next(
                    (i for i, item in enumerate(unlinked_list_used) if compare_exchanges(exc, item, db2_name)),
                    None
                )

                if ind is not None:
                    # if we find current exchange in the unlinked exchanges list, replace it with other ones
                    # while using allocation by production volume
                    allocated_excs_new_amt = deepcopy(allocated_excs[ind])
                    # for exc_new_amt in allocated_excs_new_amt:÷
                    # exc_new_amt['amount'] = exc_new_amt['production volume share'] * exc['amount']
                    for exc_new_amt in allocated_excs_new_amt:
                        if 'production volume share' in exc_new_amt:
                            exc_new_amt['amount'] = exc['amount']
                            new_exchanges.append(rescale_exchange(exc_new_amt, exc_new_amt['production volume share']))

                else:
                    # if we don't find current exchange in the unlinked exchanges list, append current to the list
                    new_exchanges.append(exc)

            act['exchanges'] = new_exchanges

        except:
            pass

    db1.match_database(db2_name, fields=('name', 'reference product', 'unit', 'location'))

    return db1
