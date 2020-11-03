import frappe

def execute():
    query_assign = '''SELECT name, status, reference_type, reference_name, {} as assignees FROM `tabToDo` 
    WHERE COALESCE(reference_type, '') != '' AND COALESCE(reference_name, '') != '' AND status != 'Cancelled' 
    AND status != 'Closed' GROUP BY reference_type, reference_name'''

    query_unassign = '''SELECT name, status, reference_type, reference_name, {} as assignees FROM `tabToDo` 
    WHERE COALESCE(reference_type, '') != '' AND COALESCE(reference_name, '') != '' AND (status = 'Cancelled' 
    OR status = 'Closed') GROUP BY reference_type, reference_name'''

    un_assign = frappe.db.multisql({
        'mariadb': query_unassign.format('GROUP_CONCAT(DISTINCT `owner`)'),
        'postgres': query_unassign.format('STRING_AGG(DISTINCT "owner", ",")')
    }, as_dict=True)

    for doc in un_assign:
        print("Removing TODO from {}: {}".format(doc.reference_type, doc.reference_name))
        frappe.db.set_value(doc.reference_type, doc.reference_name, '_assign', None, update_modified=False)
    print("Removed all Assignments")
    frappe.db.commit()

    assignments = frappe.db.multisql({
        'mariadb': query_assign.format('GROUP_CONCAT(DISTINCT `owner`)'),
        'postgres': query_assign.format('STRING_AGG(DISTINCT "owner", ",")')
    }, as_dict=True)

    for doc in assignments:
        print("Adding TODO to {}: {}".format(doc.reference_type, doc.reference_name))
        assignments = doc.assignees.split(',')
        frappe.db.set_value(doc.reference_type, doc.reference_name, '_assign', frappe.as_json(assignments),
                            update_modified=False)
    print("Added all Open Assignments")
