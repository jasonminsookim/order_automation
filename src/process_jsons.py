import io
import json
import os


def extract_jsons_from_directory(directory_to_jsons):
    """
    Function that extracts jsons from a directory, adds missing curly braces, and appends the dictionary to a list.
    """
    dict_list = []
    json_files = [pos_json for pos_json in os.listdir(directory_to_jsons) if pos_json.endswith('.json')]

    for file in json_files:
        full_filename = "%s/%s" % (directory_to_jsons, file)
        with io.open(full_filename, "r") as fi:
            string_of_json = fi.read()
            string_of_json = "{\n" + string_of_json.rstrip().rstrip(",") + "\n}"

            one_dict = json.loads(string_of_json)
            dict_list.append(one_dict)

    return dict_list


def filter_json(orders_dict_list, country_list):
    """
    Filters orders from Amazon.com by country.
    """

    filtered_orders_dict_list = []
    for order_dict in orders_dict_list:
        country = order_dict['shipping_address']['country']
        if country in country_list:
            filtered_orders_dict_list.append(order_dict)

    return filtered_orders_dict_list
