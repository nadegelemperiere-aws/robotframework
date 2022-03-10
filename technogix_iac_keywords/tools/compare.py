""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Tool functions to manipulate json disctionaries
# -------------------------------------------------------
# Nadège LEMPERIERE, @13 november 2021
# Latest revision: 13 november 2021
# --------------------------------------------------- """

# System includes
from json import dumps

# Robotframework includes
from robot.api import logger
ROBOT = False

# pylint: disable=R1702, R0914, R0912

def compare_dictionaries(spec, test) :
    """ Test if spec dictionaries is included in test
        ---
        spec (dict) : Specs for the comparison
        test (dict) : Dictionary to test
    """

    result = True

    if not isinstance(test,dict) :
        result = False
        logger.debug('Dictionary ' + dumps(spec) + \
            ' is compared to something that is not a dictionary')

    else :

        for key in spec.keys() :
            if not key in test :
                logger.debug('Key ' + key + ' not found')
                result = False
            else :
                key_result = True
                if isinstance(spec[key], dict) :
                    key_result = compare_dictionaries(spec[key], test[key])
                elif isinstance(spec[key], list) :
                    key_result = compare_list(spec[key], test[key])
                else : key_result = (spec[key] == test[key])

                if not key_result : logger.debug('Key ' + key + ' does not match')
                result = result and key_result

        if result   :
            logger.debug('Dictionaries ' + dumps(spec) + ' and ' + dumps(test) + ' match')
        else        :
            logger.debug('Dictionaries ' + dumps(spec) + ' and ' + dumps(test) + ' does not match')

    return result


def compare_list(spec, test) :
    """ Test if spec list is included in test
        ---
        spec (list) : Specs for the comparison
        test (list) : List to test
    """

    result = True

    if not isinstance(test,list) :
        result = False
        logger.debug('List ' + dumps(spec) + ' is compared to something that is not a list')

    else :

        test_temp = test.copy()
        for item in spec :
            found = False
            for jtem in test_temp :
                if not found :
                    if isinstance(item, dict) :
                        if compare_dictionaries(item, jtem) :
                            found = True
                            test_temp.remove(jtem)
                    elif isinstance(item, list) :
                        if compare_list(item, jtem) :
                            found = True
                            test_temp.remove(jtem)
                    else :
                        if item == jtem :
                            found = True
                            test_temp.remove(jtem)

            if not found : result = False

        if result   :
            logger.debug('Lists ' + dumps(spec) + ' and ' + dumps(test) + ' match')
        else        :
            logger.debug('Lists ' + dumps(spec) + ' and ' + dumps(test) + ' does not match')


    return result


def remove_type_from_dictionary(input_dict, input_type) :
    """ Remove all object of the given type from input dictionary
        ---
        input_dict (dict) : Input dictionary to update
        input_type (str)  : Type to remove from dictionary
    """

    result = {}

    for key in input_dict.keys() :
        if isinstance(input_dict[key], input_type) :
            logger.debug('Removing element ' + key + ' from dict')
        elif isinstance(input_dict[key], dict) :
            result[key] = remove_type_from_dictionary(input_dict[key], input_type)
        elif isinstance(input_dict[key], list) :
            result[key] = remove_type_from_list(input_dict[key], input_type)
        else :
            result[key] = input_dict[key]

    return result

def remove_type_from_list(input_list, input_type) :
    """ Remove all object of the given type from input list
        ---
        input_list (list) : Input list to update
        input_type (str)  : Type to remove from dictionary
    """

    result = []

    for item in input_list :
        if isinstance(item, input_type) :
            logger.debug('Removing element from list')
        elif isinstance(item, dict) :
            result.append(remove_type_from_dictionary(item, input_type))
        elif isinstance(item, list) :
            result.append(remove_type_from_list(item, input_type))
        else :
            result.append(item)


    return result

# pylint: enable=R1702, R0914, R0912
