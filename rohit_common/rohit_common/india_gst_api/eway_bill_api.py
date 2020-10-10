# -*- coding: utf-8 -*-
# Copyright (c) 2020, Rohit Industries Group Private Limited and contributors
# For license information, please see license.txt
import frappe
from datetime import datetime
from .common import get_gsp_details, get_api_url
from frappe.utils import get_datetime, getdate
from frappe.utils.file_manager import save_file
import requests

api = 'eway'


def create_ewb_from_json(ewb_json):
    action = 'GENEWAYBILL'
    res_json = process_ewb_post_request(api=api, action=action, json_data=ewb_json)
    return res_json


def cancel_ewb(ewb_no):
    action = 'CANEWB'
    res_json = process_ewb_post_request(api=api, action=action, json_data=ewb_json)


def update_partb_ewb (ewb_doc):
    action = 'VEHEWB'
    ewb_veh_data = {}
    for veh in ewb_doc.vehicles:
        ewb_veh_data['ewbNo'] = ewb_doc.eway_bill_no
        if veh.vehicle_number:
            ewb_veh_data['vehicleNo'] = veh.vehicle_number
            ewb_veh_data['transMode'] = get_transport_mode(veh.mode_of_transport)
        ewb_veh_data['fromPlace'] = veh.from_place
        ewb_veh_data['fromState'] = veh.from_state_number
        ewb_veh_data['reasonRem'] = 'First Time'
        ewb_veh_data['reasonCode'] = 4
        if veh.transport_doc_no:
            ewb_veh_data['transDocNo'] = veh.transport_doc_no
            ewb_veh_data['transDocDate'] = (getdate(veh.transport_doc_date)).strftime('%d/%m/%Y')
            ewb_veh_data['transMode'] = 4
    res_json = process_ewb_post_request(api=api, action=action, json_data=ewb_veh_data)
    ewb_doc.json_reply = str(res_json)
    return res_json


def get_eway_bill_details(ewb_no, raw_resp=0):
    action = 'GetEwayBill'
    parameter = 'ewbNo'
    res_json = process_ewb_get_request(api=api, action=action, parm_name=parameter, parm_val=ewb_no, raw_resp=raw_resp)
    return res_json


def get_ewb_by_dt_dn(dt, dn):
    action = 'GetEwayBillGeneratedByConsigner'
    parameter = 'docType'
    parm2 = 'docNo'
    dt_code = get_doctype(text=dt)
    res_json = process_ewb_get_request(api=api, action=action, parm_name=parameter, parm_val=dt_code, parm_name2=parm2,
                                       parm_val2=dn)
    return res_json


def get_ewb_date(ewb_date):
    action = 'GetEwayBillsByDate'
    parameter = 'date'
    res_json = process_ewb_get_request(api=api, action=action, parm_name=parameter, parm_val=ewb_date)
    return res_json


def get_ewb_others(ewb_date):
    action = 'GetEwayBillsofOtherParty'
    parameter = 'date'
    res_json = process_ewb_get_request(api=api, action=action, parm_name=parameter, parm_val=ewb_date)
    return res_json


def get_ewb_detailed_print(ewbdoc, json_data):
    api = 'asp'
    action = 'printdetailewb'
    response = process_print_request(ewbdoc=ewbdoc, api=api, action=action, json=json_data)
    return response


def process_print_request(ewbdoc, api, action, json):
    gsp_link, aspid, asppass, gstin = get_gsp_details(api=api, action=action)
    api_url = get_api_url(api, action)
    full_url = gsp_link + api_url + action + '?aspid=' + aspid + '&password=' + asppass + '&Gstin=' + gstin
    response = requests.post(full_url, json=json)
    image_data = response.content
    save_file('{}.pdf'.format(ewbdoc.eway_bill_no), image_data, ewbdoc.doctype, ewbdoc.name, is_private=1)
    return response


def process_ewb_post_request(api, action, json_data):
    full_url = get_ewb_url(api, action)
    response = requests.post(full_url, json=json_data)
    res_json = response.json()
    ewb_no = res_json.get('ewayBillNo', "")
    if ewb_no == "":
        ewb_no = res_json.get('ewbNo', "")
    if ewb_no != "":
        if int(res_json.get('status_cd')) == 1:
            return res_json
        elif int(res_json.get('status_cd')) == 0:
            frappe.msgprint('Error Returned from GST Server Check Logs')
            frappe.msgprint(str(res_json.get('error')))
    else:
        return res_json


def process_ewb_get_request(api, action, parm_name, parm_val, parm_name2=None, parm_val2=None, raw_resp=0):
    if parm_name2:
        full_url = get_ewb_url(api, action) + '&' + parm_name + '=' + parm_val + '&' + parm_name2 + '=' + parm_val2
    else:
        full_url = get_ewb_url(api, action) + '&' + parm_name + '=' + str(parm_val)
    response = requests.get(full_url)
    if raw_resp == 1:
        res_json = response
    else:
        res_json = response.json()
    print (res_json)
    return res_json


def get_ewb_url(api, action):
    gsp_link, aspid, asppass, gstin = get_gsp_details(api=api, action=action)
    auth_token = get_ewb_access_token()
    api_url = get_api_url(api, action)
    url = gsp_link + api_url + api + 'api?action=' + action + '&aspid=' + aspid + '&password=' + asppass + \
               '&gstin=' + gstin + '&authtoken=' + auth_token
    return url


def get_ewb_access_token():
    rset = frappe.get_single('Rohit Settings')
    now_time = datetime.now()
    ac_token_time = get_datetime(rset.access_token_time)
    if not rset.access_token_time:
        time_diff_hrs = 6
    else:
        time_diff_hrs = (now_time - ac_token_time).total_seconds()/3600
    # Only Need Access Token after 6 hours of getting the first one since Access Token is Valid for 6 hours
    if time_diff_hrs >= 6:
        res_json = get_eway_auth_token()
        if res_json.get("status") == '1':
            access_token = res_json.get("authtoken")
            rset.access_token = access_token
            rset.access_token_time = now_time
            rset.save()
            frappe.db.commit()
            rset.reload()
            return access_token
        else:
            print('Error')
    else:
        access_token = rset.access_token
        return access_token


def get_eway_auth_token():
    rset = frappe.get_single('Rohit Settings')
    api = 'eway'
    action = 'ACCESSTOKEN'
    gsp_link, aspid, asppass, gstin = get_gsp_details(api=api, action=action)
    api_url = get_api_url(api=api, action=action)
    if rset.sandbox_mode == 1:
        gstin = '05AAACG1539P1ZH'
        ewb_uname = '05AAACG1539P1ZH'
        ewb_pass = 'abc123@@'
    else:
        ewb_uname = rset.eway_bill_id
        ewb_pass = rset.eway_bill_password
    full_url = gsp_link + api_url + 'authenticate?action=' + action + '&aspid=' + aspid + '&password=' + asppass + \
               '&gstin=' + gstin + '&username=' + ewb_uname + '&ewbpwd=' + ewb_pass
    response = requests.get(full_url)
    return response.json()


def get_supply_type(data, text):
    if text == 'Outward':
        data.supplyType = 'O'
    else:
        data.supplyType = 'I'
    return data


def get_supply_sub_type(data, text):
    if text == 'Supply':
        data.subSupplyType = 1
    elif text == 'Import':
        data.subSupplyType = 2
    elif text == 'Export':
        data.subSupplyType = 3
    elif text == 'Job Work':
        data.subSupplyType = 4
    elif text == 'For Own Use':
        data.subSupplyType = 5
    elif text == 'Job work Returns':
        data.subSupplyType = 6
    elif text == 'Sales Return':
        data.subSupplyType = 7
    elif text == 'Others':
        # Here also need to mention the data.subSypplyDesc for describing supply type text(20)
        data.subSupplyType = 8
    elif text == 'SKD/CKD/Lots':
        data.subSupplyType = 9
    elif text == 'Line Sales':
        data.subSupplyType = 10
    elif text == 'Recipient Not Known':
        data.subSupplyType = 11
    elif text == 'Exhibition or Fairs':
        data.subSupplyType = 12
    return data


def get_doctype(text, data=None):
    if text == 'Tax Invoice':
        code = 'INV'
    elif text == 'Delivery Challan':
        code = 'CHL'
    elif text == 'Bill of Supply':
        code = 'BIL'
    elif text == 'Bill of Entry':
        code = 'BOE'
    elif text == 'Others':
        code = 'OTH'
    else:
        frappe.throw('Undefined Document Type {}'.format(text))
    if not data:
        return code
    else:
        data.docType = code
        return data


def get_docno (data, dt, dn):
    # Text(16) Alphanum, -, /
    doc = frappe.get_doc(dt, dn)
    if dt == 'Purchase Order':
        tax_doc = frappe.get_doc('Purchase Taxes and Charges Template', doc.taxes_and_charges)
        if tax_doc.is_import == 1:
            data.docNo = doc.boe_no
        else:
            data.docNo = dn
    else:
        data.docNo = dn
    return data


def get_from_address(doc, data, text):
    if text == 'fromGstin':
        data.fromGstin = doc.from_gstin
    elif text == 'userGstin':
        data.userGstin = doc.generated_by
    elif text == 'toGstin':
        data.toGstin = doc.to_gstin
    elif text == 'toPincode':
        data.toPincode = int(doc.to_pincode)
    elif text == 'fromPincode':
        data.fromPincode = int(doc.from_pincode)
    elif text == 'fromStateCode':
        data.fromStateCode = int(doc.from_state_code)
        if doc.from_state_code != 99:
            data.actFromStateCode = int(doc.from_state_code)
        else:
            data.actFromStateCode = int(doc.to_state_code)
    elif text == 'toStateCode':
        data.toStateCode = int(doc.to_state_code)
        data.actToStateCode = int(doc.to_state_code)
    return data


def get_value_of_tax(data, dt, dn, text):
    doc = frappe.get_doc(dt, dn)
    tax_dict = get_taxes_type(dt, dn)
    if text == 'total':
        data.totalValue = doc.base_grand_total
    elif text == 'net':
        data.totInvValue = doc.base_net_total
    elif text == 'cgst':
        data.cgstValue = tax_dict.get('cgst_amt', 0)
    elif text == 'sgst':
        data.sgstValue = tax_dict.get('sgst_amt', 0)
    elif text == 'igst':
        data.igstValue = tax_dict.get('igst_amt', 0)
    elif text == 'cess':
        data.cessValue = tax_dict.get('cess_amt', 0)
    elif text == 'cess_non_advol':
        data.cessNonAdvolValue = 0

    return data


def get_transport_mode(text):
    if text == 'Road':
        return 1
    elif text == 'Rail':
        return 2
    elif text == 'Air':
        return 3
    elif text == 'Ship':
        return 4
    elif text == 'InTransit':
        return 5


def get_transporter_id(data, dt, dn, eway_doc):
    doc = frappe.get_doc(dt, dn)
    transp_doc = frappe.get_doc('Transporters', doc.transporters)
    if transp_doc.self_pickup == 1:
        data.transporterId = eway_doc.generated_by
    else:
        if transp_doc.gstin_for_eway:
            data.transporterId = transp_doc.gstin_for_eway
        else:
            frappe.throw('GSTIN for {} is not mentioned'.format(frappe.get_desk_link('Transporters', doc.transporters)))
    return data


def convert_int_transport_mode(mode_integer):
    if int(mode_integer) == 1:
        return "Road"
    elif int(mode_integer) == 2:
        return "Rail"
    elif int(mode_integer) == 3:
        return "Air"
    elif int(mode_integer) == 4:
        return "Ship"
    elif int(mode_integer) == 5:
        return "InTransit"
    else:
        frappe.throw('Error Code Not in Transport List')


def get_trans_type(data, text):
    if text == 'Regular':
        data.transactionType = 1
    elif text == 'Bill To - Ship To':
        data.transactionType = 2
    elif text == 'Bill From - Dispatch From':
        data.transactionType = 3
    elif text == 'Combination of 2 and 3':
        data.transactionType = 4
    return data


def get_doc_date(data, dt, dn):
    doc = frappe.get_doc(dt, dn)
    if dt == 'Sales Invoice':
        date_string = doc.posting_date
    elif dt == 'Purchase Order':
        date_string = doc.transaction_date
    date_string = date_string.strftime('%d/%m/%Y')
    data.docDate = date_string
    return data


def get_taxes_type(dt, dn):
    taxes_dict = {}
    doc = frappe.get_doc(dt, dn)
    gset = frappe.get_single('GST Settings')
    for tax in doc.taxes:
        for acc in gset.gst_accounts:
            if tax.account_head == acc.cgst_account:
                taxes_dict["cgst_amt"] = tax.base_tax_amount
                taxes_dict["cgst_per"] = tax.rate
            elif tax.account_head == acc.sgst_account:
                taxes_dict["sgst_amt"] = tax.base_tax_amount
                taxes_dict["sgst_per"] = tax.rate
            elif tax.account_head == acc.igst_account:
                taxes_dict["igst_amt"] = tax.base_tax_amount
                taxes_dict["igst_per"] = tax.rate
    return taxes_dict


def get_items_table(data, tbl_dict):
    it_dict = {}
    for d in tbl_dict:
        uom_doc = frappe.get_doc('UOM', d.uom)
        tariff_doc = frappe.get_doc('Customs Tariff Number', d.gst_hsn_code)
        it_dict['itemNo'] = d.idx
        # it_dict['productId'] = d.item_code
        it_dict['productName'] = tariff_doc.item_code
        it_dict['productDesc'] = tariff_doc.description
        it_dict['hsnCode'] = d.gst_hsn_code
        it_dict['quantity'] = d.qty
        if uom_doc.eway_bill_uom:
            it_dict['qtyUnit'] = uom_doc.eway_bill_uom
        else:
            frappe.throw('No UOM Mapping Defined for {}'.format(frappe.get_desk_link('UOM', d.uom)))
        it_dict['cgstRate'] = d.cgst_rate
        it_dict['sgstRate'] = d.sgst_rate
        it_dict['igstRate'] = d.igst_rate
        it_dict['cessRate'] = d.cess_rate
    data.itemList = [it_dict]
    return data


def search_existing_ewb(ewb_no):
    exist_ewb = frappe.db.sql("""SELECT name FROM `tabeWay Bill` WHERE eway_bill_no = '%s' 
    AND docstatus != 2"""%(ewb_no), as_dict=1)
    return exist_ewb


def ewb_from_ewb_summary(ewbj):
    existing_ewb = search_existing_ewb(ewbj.get('ewbNo'))
    if not existing_ewb:
        ewb = frappe.new_doc('eWay Bill')
        update = 0
    else:
        ewb = frappe.get_doc('eWay Bill', existing_ewb[0].name)
        update = 1
    ewb.eway_bill_no = ewbj.get('ewbNo')
    ewb.eway_bill_date = datetime.strptime(ewbj.get('ewbDate'), '%d/%m/%Y %I:%M:%S %p')
    ewb.status = ewbj.get('status')
    ewb.generated_by = ewbj.get('genGstin')
    # Search for Doc Number in Global Search if Found Then Update the Document Type as well.
    ewb.ewb_doc_no = ewbj.get('docNo')
    ewb.document_date = datetime.strptime(ewbj.get('docDate'), '%d/%m/%Y')
    ewb.to_pincode = ewbj.get('delPinCode')
    ewb.to_state_code = ewbj.get('delStateCode')
    ewb.to_place = ewbj.get('delPlace')
    if ewbj.get('validUpto') != '':
        ewb.valid_upto = datetime.strptime(ewbj.get('validUpto'), '%d/%m/%Y %I:%M:%S %p')
    ewb.extended_times = ewbj.get('extendedTimes')
    ewb.reject_status = ewbj.get('rejectStatus')
    ewb.save()
    if update == 0:
        text = 'Created'
    else:
        text = 'Updated'
    frappe.msgprint('{} {} with eWay Bill# {}'.format(text, frappe.get_desk_link('eWay Bill', ewb.name),
                                                      ewb.eway_bill_no))


def ewb_from_ewb_detail(ewbj, created_by="self"):
    gstin = frappe.get_value('Rohit Settings', 'Rohit Settings', 'gstin')
    # First Search for eWay Bill if not exists then create a new eWay Bill
    existing_ewb = search_existing_ewb(ewbj.get('ewbNo'))
    if not existing_ewb:
        ewb = frappe.new_doc('eWay Bill')
        update = 0
    else:
        ewb = frappe.get_doc('eWay Bill', existing_ewb[0].name)
        update = 1
    ewb.eway_bill_no = ewbj.get('ewbNo')
    ewb.eway_bill_date = datetime.strptime(ewbj.get('ewayBillDate'), '%d/%m/%Y %I:%M:%S %p')
    ewb.generation_mode = ewbj.get('genMode')
    ewb.status = ewbj.get('status')
    ewb.generated_by = ewbj.get('userGstin')
    if ewb.generated_by == gstin:
        ewb.supply_type = 'Outward'
    else:
        ewb.supply_type = 'Inward'
    # Search for Doc Number in Global Search if Found Then Update the Document Type as well.
    ewb.ewb_doc_no = ewbj.get('docNo')
    ewb.document_date = datetime.strptime(ewbj.get('docDate'), '%d/%m/%Y')
    ewb.from_trade_name = ewbj.get('fromTrdName')
    ewb.from_gstin = ewbj.get('fromGstin')
    ewb.from_pincode = ewbj.get('fromPincode')
    ewb.from_state_code = ewbj.get('fromStateCode')
    ewb.from_address_text = ewbj.get('fromAddr1') + "," + ewbj.get('fromAddr2') + '\n' + ewbj.get('fromPlace') + \
                            ", " + "State Code: " + str(ewbj.get('fromStateCode')) + ", " + \
                            str(ewbj.get('fromPincode'))
    ewb.to_trade_name = ewbj.get('toTrdName')
    ewb.to_gstin = ewbj.get('toGstin')
    ewb.to_pincode = ewbj.get('toPincode')
    ewb.to_state_code = ewbj.get('toStateCode')
    ewb.to_place = ewbj.get('toPlace')
    ewb.to_address_text = ewbj.get('toAddr1') + "," + ewbj.get('toAddr2') + '\n' + ewbj.get('toPlace') + ", " \
                                "" + "State Code: " + str(ewbj.get('toStateCode')) + ", " + str(ewbj.get(
        'toPincode'))
    if ewbj.get('validUpto') != '':
        ewb.valid_upto = datetime.strptime(ewbj.get('validUpto'), '%d/%m/%Y %I:%M:%S %p')
    ewb.extended_times = ewbj.get('extendedTimes')
    ewb.reject_status = ewbj.get('rejectStatus')
    ewb.taxable_value = ewbj.get('totalValue')
    ewb.total_value = ewbj.get('totInvValue')
    ewb.sgst_value = ewbj.get('sgstValue')
    ewb.cgst_value = ewbj.get('cgstValue')
    ewb.igst_value = ewbj.get('igstValue')
    ewb.cess_value = ewbj.get('cessValue')
    ewb.approx_distance = ewbj.get('actualDist')
    ewb.items = []
    if ewbj.get('itemList'):
        it_dict = {}
        for item in ewbj.get('itemList'):
            it_dict["idx"] = item.get('itemNo')
            it_dict["product_id"] = item.get('productId')
            it_dict["item_code"] = item.get('productName')
            it_dict["description"] = item.get('productDesc')
            it_dict["gst_hsn_code"] = item.get('hsnCode')
            it_dict["qty"] = item.get('quantity')
            it_dict["uom"] = item.get('qtyUnit')
            it_dict["cgst_rate"] = item.get('cgstRate')
            it_dict["sgst_rate"] = item.get('sgstRate')
            it_dict["igst_rate"] = item.get('igstRate')
            it_dict["cess_rate"] = item.get('cessRate')
            it_dict["cess_non_advol"] = item.get('cessNonAdvol')
            it_dict["base_amount"] = item.get('taxableAmount')
        ewb.append("items", it_dict.copy())
    ewb.vehicles=[]
    if ewbj.get('VehiclListDetails'):
        veh_dict={}
        for veh in ewbj.get('VehiclListDetails'):
            veh_dict["update_mode"] = veh.get('updMode')
            veh_dict["vehicle_number"] = veh.get('vehicleNo')
            veh_dict["from_place"] = veh.get('fromPlace')
            veh_dict["from_state_number"] = veh.get('fromState')
            veh_dict["mode_of_transport"] = convert_int_transport_mode(veh.get('transMode'))
            veh_dict["transport_doc_no"] = veh.get('transDocNo')
            veh_dict["transport_doc_date"] = datetime.strptime(veh.get('transDocDate'), '%d/%m/%Y')
            ewb.append("vehicles", veh_dict.copy())
    ewb.save()
    ewb.reload()
    ewb.submit()
    if update == 0:
        text = 'Created'
    else:
        text = 'Updated'
    frappe.msgprint('{} {} with eWay Bill# {}'.
                    format(text, frappe.get_desk_link('eWay Bill', ewb.name), ewb.eway_bill_no))


def others_ewb_from_summary(ewbj):
    existing_ewb = search_existing_ewb(ewbj.get('ewbNo'))
    if not existing_ewb:
        ewb = frappe.new_doc('eWay Bill')
        update = 0
    else:
        ewb = frappe.get_doc('eWay Bill', existing_ewb[0].name)
        update = 1
    ewb.eway_bill_no = ewbj.get('ewbNo')
    ewb.eway_bill_date = datetime.strptime(ewbj.get('ewayBillDate'), '%d/%m/%Y %I:%M:%S %p')
    ewb.status = ewbj.get('status')
    ewb.generated_by = ewbj.get('genGstin')
    # Search for Doc Number in Global Search if Found Then Update the Document Type as well.
    ewb.ewb_doc_no = ewbj.get('docNo')
    ewb.document_date = datetime.strptime(ewbj.get('docDate'), '%d/%m/%Y')
    ewb.reject_status = ewbj.get('rejectStatus')
    ewb.save()
    if update == 0:
        text = 'Created'
    else:
        text = 'Updated'
    frappe.msgprint('{} {} with eWay Bill# {}'.format(text, frappe.get_desk_link('eWay Bill', ewb.name),
                                                      ewb.eway_bill_no))
