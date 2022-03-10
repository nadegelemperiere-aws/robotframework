""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Keywords to manage keepass tasks
# -------------------------------------------------------
# Nadège LEMPERIERE, @05 october 2021
# Latest revision: 05 october 2021
# --------------------------------------------------- """

# Pykeepass includes
from pykeepass import PyKeePass

# Robotframework includes
from robot.api import logger
from robot.api.deco import keyword
ROBOT = False


@keyword("Load Keepass Database Secret")
def load_database_secret(database, key, entry, attribute) :
    """ Retrieve a secret from a keepass database
        ---
        database  (str) : keepass database file to retrieve value from
        key       (str) : key file associated to database
        entry     (str) : entry to retrieve from database (format ['my','entry'] => /my/entry)
        attribute (str) : attribute to retrieve in entry
    """
    result = ''

    if entry[0] == '/' : entry = entry[1:]
    if entry[-1] == '/' : entry = entry[:-1]
    entry_list = entry.split('/')
    try :
        kps = PyKeePass(database, keyfile=key)
        search = kps.find_entries_by_path(entry_list)
        if search is None : logger.error('Entry ' + entry + ' not found')
        else: result = getattr(search,attribute)

    except Exception as exc :
        logger.error(str(exc))

    return result
