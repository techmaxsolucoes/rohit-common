#  Copyright (c) 2022. Rohit Industries Group Private Limited and Contributors.
#  For license information, please see license.txt

import frappe
import phonenumbers as pnos


def comma_phone_validations(csv_phones, country_code, backend=True):
    """
    Returns comma separated validated phone numbers
    """
    val_csv_ph = ""
    if csv_phones:
        ph_list = csv_phones.split(",")
        for phone in ph_list:
            if phone != "":
                val_phone = single_phone_validations(phone, country_code, backend)
                if val_phone:
                    if val_csv_ph:
                        val_csv_ph += f", {val_phone.phone}"
                    else:
                        val_csv_ph = val_phone.phone
    return val_csv_ph


def single_phone_validations(phone_txt, country_code, backend=True):
    """
    Returns Validated Phone Dictionary. The dictionary has following keys
    phone:{fomatted_phone}, phone_type:{phone_type_int}, phone_validation:{ph_val_int}
    Now if the phone is not possible the dict is none
    """
    val_ph_dict = frappe._dict({})
    parsed_ph = parse_ph_nos(phone_txt, country_code)
    if parsed_ph:
        val_ph_dict["phone"] = format_phone(parsed_ph)
        val_ph_dict["phone_validation"] = validate_no(parsed_ph)
        val_ph_dict["phone_type"] = get_phone_type(parsed_ph)
    else:
        message = f"Phone No: {phone_txt} for Country Code= {country_code} could not be Parsed"
        if backend == 1:
            print(message)
        else:
            frappe.msgprint(message)
    return val_ph_dict


def parse_ph_nos(phone_txt, country_code):
    """
    Returns a phone object for a phone number and a country code (in Upper Case)
    """
    try:
        parse_ph = pnos.parse(phone_txt, country_code)
        return parse_ph
    except Exception as e:
        return None

def validate_no(parsed_phone):
    """
    Returns 0 when number not possible, 1 when number is valid, 2 when number
    is possible but not valid
    """
    if parsed_phone:
        if pnos.is_possible_number(parsed_phone) == 1:
            if pnos.is_valid_number(parsed_phone) == 1:
                return 1
            else:
                return 2
        else:
            return 0
    else:
        return 0


def format_phone(parsed_phone):
    """
    Returns phone number in E164 format for a parsed number
    """
    formatted_no = pnos.format_number(parsed_phone, pnos.PhoneNumberFormat.E164)
    return formatted_no


def get_phone_type(parsed_phone):
    """
    Returns the type of Phone number for a parsed number
    0=Fixed Line, 1=Mobile, 2=Fixed_or_mobile, 3=Toll Free, 4=Premium Rate
    5=Shared Cost, 6=VOIP, 7=Personal Number, 8=Pager, 9=UAN, 10=Voicemail,
    99=Unknown

    Return 1 for Mobile and 0 for Others
    """
    phone_type = pnos.number_type(parsed_phone)
    if phone_type == 1:
        return 1
    else:
        return 0
