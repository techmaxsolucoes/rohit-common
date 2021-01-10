# -*- coding: utf-8 -*-
# Copyright (c) 2020, Rohit Industries Group Pvt Ltd. and contributors
# For license information, please see license.txt

# This Manual Patch would list all the public and private files if the files are not in the DB `tabFiles`
# then it would delete them.


from __future__ import unicode_literals
import frappe
import time
import os
from os import listdir
from os.path import isfile, join
from pathlib import Path
from frappe.utils import get_files_path


def execute():
    st_time = time.time()
    public_files_path = get_files_path()
    private_files_path = get_files_path(is_private=1)
    public_files = [f for f in listdir(public_files_path) if isfile(join(public_files_path, f))]
    private_files = [f for f in listdir(private_files_path) if isfile(join(private_files_path, f))]
    orphan_private = 0
    orp_priv_size = 0
    orphan_pub = 0
    orp_pub_size = 0

    for list_of_files in [public_files, private_files]:
        if list_of_files:
            for files in list_of_files:
                if list_of_files == public_files:
                    file_path = public_files_path + '/' + files
                else:
                    file_path = private_files_path + '/' + files
                if '"' in files:
                    query = """SELECT name, attached_to_doctype, attached_to_name, file_url, file_name 
                    FROM `tabFile` WHERE  file_name = '%s' """ % (files)
                else:
                    query = """SELECT name, attached_to_doctype, attached_to_name, file_url, file_name
                    FROM `tabFile` WHERE  file_name = "%s" """ % (files)
                file_db = frappe.db.sql(query, as_list=1)
                if file_db:
                    pass
                # print(file_db)
                else:
                    file_size_kb = round(Path(file_path).stat().st_size / 1024, 2)
                    print(f"Deleted file with Size = {file_size_kb} kB and Name = {files} and file path = {file_path}")
                    if list_of_files == public_files:
                        orphan_pub += 1
                        orp_pub_size += Path(file_path).stat().st_size
                    else:
                        orphan_private += 1
                        orp_priv_size += Path(file_path).stat().st_size
                # os.remove(file_path)
    tot_time = int(time.time() - st_time)
    tot_pub_size = round(orp_pub_size / 1024 / 1024, 2)
    tot_priv_size = round(orp_priv_size / 1024 / 1024, 2)

    print(f"Total Public Files = {len(public_files)}, Total Size = ")
    print(f"Total Private Files = {len(private_files)}, Total Size = ")
    print(f"Public Files Orphaned and hence Deleted = {orphan_pub} with Total = {tot_pub_size} MB")
    print(f"Private Files Orphaned and hence Deleted = {orphan_private} with Total Size = {tot_priv_size} MB")
    print(f"Total Time Taken = {tot_time} seconds")
