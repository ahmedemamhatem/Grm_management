#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Update Authorized User to link from Member Companion/Employee"""

import json

# Read current JSON
with open('/home/frappe/frappe-bench/apps/grm_management/grm_management/grm_management/doctype/authorized_user/authorized_user.json', 'r') as f:
    data = json.load(f)

# Update field_order
data['field_order'] = [
    "user_type", "member_companion", "member_employee", "user_name",
    "access_granted", "column_break_1", "zk_user_id",
    "access_start_time", "access_end_time"
]

# Add new fields
new_fields = []
for field in data['fields']:
    if field['fieldname'] == 'user_type':
        new_fields.append(field)
        # Add companion link
        new_fields.append({
            "fieldname": "member_companion",
            "fieldtype": "Link",
            "label": "Member Companion | المرافق",
            "options": "Member Companion",
            "depends_on": "eval:doc.user_type=='Companion'"
        })
        # Add employee link
        new_fields.append({
            "fieldname": "member_employee",
            "fieldtype": "Link",
            "label": "Member Employee | الموظف",
            "options": "Member Employee",
            "depends_on": "eval:doc.user_type=='Employee'"
        })
    else:
        new_fields.append(field)

data['fields'] = new_fields
data['modified'] = "2026-02-03 01:00:00.000000"

# Write updated JSON
with open('/home/frappe/frappe-bench/apps/grm_management/grm_management/grm_management/doctype/authorized_user/authorized_user.json', 'w') as f:
    json.dump(data, f, indent=1)

print("Authorized User JSON updated successfully!")
