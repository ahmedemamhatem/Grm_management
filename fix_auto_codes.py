#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fix all code fields to be read-only and auto-generate with naming series"""

import json
import os

doctypes_to_fix = {
    'grm_location': {
        'path': '/home/frappe/frappe-bench/apps/grm_management/grm_management/grm_management/doctype/grm_location/grm_location.json',
        'code_field': 'location_code',
        'naming_series': 'LOC-.YYYY.-.####'
    },
    'grm_property': {
        'path': '/home/frappe/frappe-bench/apps/grm_management/grm_management/grm_management/doctype/grm_property/grm_property.json',
        'code_field': 'property_code',
        'naming_series': 'PROP-.YYYY.-.####'
    },
    'grm_space': {
        'path': '/home/frappe/frappe-bench/apps/grm_management/grm_management/grm_management/doctype/grm_space/grm_space.json',
        'code_field': 'space_code',
        'naming_series': 'SPACE-.YYYY.-.####'
    },
    'grm_space_type': {
        'path': '/home/frappe/frappe-bench/apps/grm_management/grm_management/grm_management/doctype/grm_space_type/grm_space_type.json',
        'code_field': 'space_type_code',
        'naming_series': 'TYPE-.####'
    },
    'grm_landlord': {
        'path': '/home/frappe/frappe-bench/apps/grm_management/grm_management/grm_management/doctype/grm_landlord/grm_landlord.json',
        'code_field': 'landlord_code',
        'naming_series': 'LAND-.YYYY.-.####'
    },
    'grm_property_contract': {
        'path': '/home/frappe/frappe-bench/apps/grm_management/grm_management/grm_management/doctype/grm_property_contract/grm_property_contract.json',
        'code_field': 'contract_number',
        'naming_series': 'CONT-.YYYY.-.####'
    }
}

for doctype_name, config in doctypes_to_fix.items():
    if not os.path.exists(config['path']):
        print(f"Skipping {doctype_name} - file not found")
        continue

    # Read JSON
    with open(config['path'], 'r') as f:
        data = json.load(f)

    # Change autoname from field to naming_series
    data['autoname'] = 'naming_series:'

    # Update code field to read_only and not required
    # Add naming_series field if not exists

    has_naming_series = False
    for field in data['fields']:
        if field['fieldname'] == 'naming_series':
            has_naming_series = True
            field['options'] = config['naming_series']
            field['default'] = config['naming_series']
        elif field['fieldname'] == config['code_field']:
            field['read_only'] = 1
            field['reqd'] = 0
            field.pop('unique', None)  # Remove unique constraint

    # Add naming_series field at beginning if not exists
    if not has_naming_series:
        # Add to field_order
        if 'field_order' in data and isinstance(data['field_order'], list):
            if 'naming_series' not in data['field_order']:
                data['field_order'].insert(0, 'naming_series')

        # Add to fields
        data['fields'].insert(0, {
            "fieldname": "naming_series",
            "fieldtype": "Select",
            "label": "Series",
            "options": config['naming_series'],
            "default": config['naming_series'],
            "reqd": 1
        })

    # Save
    with open(config['path'], 'w') as f:
        json.dump(data, f, indent=1)

    print(f"✅ Fixed {doctype_name}")

print("\n✅ All DocTypes updated to use naming_series for auto-generation!")
