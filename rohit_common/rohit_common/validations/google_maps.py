# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import frappe
import requests
import json
import ast
import re


def geocoding(doc):
    key = get_google_maps_api_key()
    url = get_google_maps_url()
    address_data = "address=" + str(doc.address_title) + " " + str(doc.address_line1) + str(doc.address_line2) + \
                   " " + str(doc.city) + " " + str(doc.state) + " " + str(doc.country) + " " + str(doc.pincode)
    full_url = url + address_data + "&key=" + key
    characters = [" ", "#"]
    for ch in characters:
        full_url = full_url.replace(ch, "+")
    # frappe.msgprint(str(full_url))
    response = requests.get(url=full_url)
    response_json = json.loads(response.content)
    # frappe.msgprint(str(response_json))
    doc.json_reply = str(response_json)


def render_gmap_json(json_txt):
    json_dict = ast.literal_eval(json_txt)
    add_dict = dict()
    if json_dict.get("status") == "OK":
        address_comps = json_dict.get("results")[0].get("address_components")
        geometry = json_dict.get("results")[0].get("geometry")
        formatted_add = json_dict.get("results")[0].get("formatted_address")
        frappe.msgprint(str(formatted_add), "Check Address Format As Below")
        plus_codes = json_dict.get("results")[0].get("plus_code")
        type_of_poi = json_dict.get("results")[0].get("types")
        partial_match = json_dict.get("results")[0].get("partial_match")
        add_dict["partial_match"] = partial_match
        if plus_codes:
            add_dict["global_code"] = plus_codes.get("global_code")
        if type_of_poi[0] != 'subpremise' and len(type_of_poi)>1:
            add_dict["poi_type"] = type_of_poi[0]
        add_dict["lat"] = geometry.get("location").get("lat")
        add_dict["lng"] = geometry.get("location").get("lng")
        postal_code = ""
        country_long = ""
        country_short = ""
        state_long = ""
        city_long = ""
        locality = ""
        sublocal1 = ""
        sublocal2 = ""

        for d in address_comps:
            if d.get("types")[0] == 'postal_code':
                postal_code = d.get("long_name")
            if d.get("types")[0] == 'country':
                country_long = d.get("long_name")
                country_short = d.get("short_name")
            if d.get("types")[0] == 'administrative_area_level_1':
                state_long = d.get("long_name")
            if d.get("types")[0] == 'administrative_area_level_2':
                city_long = d.get("long_name")
            if d.get("types")[0] == 'locality':
                locality = d.get("long_name")
            if d.get("types")[0] == 'political':
                if d.get("types")[1] == 'sublocality':
                    if d.get("types")[2] == 'sublocality_level_1':
                        sublocal1 = d.get("long_name")
                    elif d.get("types")[2] == 'sublocality_level_2':
                        sublocal2 = d.get("long_name")
        add_dict["postal_code"] = postal_code
        add_dict["country"] = country_long
        add_dict["state"] = state_long
        add_dict["city"] = city_long
        add_dict["locality"] = locality
        add_dict["sublocal1"] = sublocal1
        add_dict["sublocal2"] = sublocal2

        formatted_add = formatted_add.replace(sublocal2, "")
        formatted_add = formatted_add.replace(sublocal1, "")
        formatted_add = formatted_add.replace(locality, "")
        formatted_add = formatted_add.replace(city_long, "")
        formatted_add = formatted_add.replace(state_long, "")
        formatted_add = formatted_add.replace(postal_code, "")
        formatted_add = formatted_add.replace(country_long, "")
        formatted_add = formatted_add.replace(country_short, "")

        formatted_add = formatted_add.replace(",", " ")
        formatted_add = re.sub(' +', ' ', formatted_add)
        add_dict["address_line1"] = formatted_add
    else:
        # ZERO_RESULTS, OVER_DAILY_LIMIT, OVER_QUERY_LIMIT, REQUEST_DENIED,INVALID_REQUEST, UNKNOWN_ERROR
        frappe.msgprint("Unable to fetch the GMAPS data see the json reply")
    return add_dict


def get_google_maps_api_key():
    gmapset = frappe.get_single("Google Maps Settings")
    return gmapset.client_key


def get_google_maps_url():
    return "https://maps.googleapis.com/maps/api/geocode/json?"
