# This defines a collection of function to help parsing of yaml configuration

def ensure_dictionary(config):
    """
    ensure_dictionary

    Ensure that config is a dictionary. If not, it is probably a list of one
    element dictionaries (the writer of the configuration file probably put
    hyphens '-' in front of his keys). If it is the case, this function will
    return a single dictionary built by fusing all the elements of the list.

    This function is mostly intended to simplify the parsing functions, as
    the output is always a dictionary.
    """
    if isinstance(config, dict):
        return config
    if not isinstance(config, list):
        raise TypeError("Unforeseen error in configuration file.\n" +
                        str(config))

    output = {}
    for element in config:
        if not isinstance(element, dict):
            raise ValueError("Parsing error in the configuration file.\n" +
                             str(element))
        if len(element) != 1:
            raise ValueError("Parsing error in the configuration file.\n" +
                             str(element))

        # getting one key in the dictionary
        key = next(iter(element))

        # Checking if key is not already in the output
        if key in output.keys():
            raise ValueError("Parsing error in the configuration file."+
                             "Two elements have the same key : " + str(key))
        
        # inserting this element in the output dictionary
        output[key] = element[key]

    return output


def ensure_list(config):
    """
    ensure_list

    Ensure that config is a list of one-valued dictionaries. This is called
    when the order of elements is important when loading the config file. (The
    yaml elements MUST have hyphens '-' in front of them).
    
    Returns config if no exception was raised. This is to keep the same format
    as ensure_dictionary, and allowed possible config file repairs in the
    future without breaking the API.
    """

    if not isinstance(config, list):
        raise TypeError("config is not a list. Did you forget some '-' "+
                        "in your configuration file ?\n" + str(config))

    for element in config:
        if not isinstance(element, dict):
            raise ValueError("Parsing error in the configuration file.\n" +
                             str(element))
        if len(element) != 1:
            raise ValueError("Parsing error in the configuration file.\n" +
                             str(element))

    return config



def find_aircraft_id(key, config):
    """
    find_aircraft_id

    The aircraft identifier can be given either as a dictionary key in the yaml
    file or under the fields 'identifier' or 'id' in the aircraft configuration
    item. This function test in the parsed yaml to find the aircraft id.
    """

    if 'identifier' in config.keys():
        return str(config['identifier'])
    elif 'id' in config.keys():
        return str(config['id'])
    else:
        return str(key)

