#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Update workspace with all shortcuts and financial links"""

import json

# Read current JSON
with open('/home/frappe/frappe-bench/apps/grm_management/grm_management/grm_management/workspace/grm_coworking_space/grm_coworking_space.json', 'r') as f:
    data = json.load(f)

# Add new links including Landlord, Contracts, and Financial
data['links'] = [
    # Properties Card
    {"hidden": 0, "is_query_report": 0, "label": "Properties", "link_count": 0, "onboard": 0, "type": "Card Break"},
    {"hidden": 0, "is_query_report": 0, "label": "GRM Location", "link_count": 0, "link_to": "GRM Location", "link_type": "DocType", "onboard": 0, "type": "Link"},
    {"hidden": 0, "is_query_report": 0, "label": "GRM Property", "link_count": 0, "link_to": "GRM Property", "link_type": "DocType", "onboard": 0, "type": "Link"},
    {"hidden": 0, "is_query_report": 0, "label": "GRM Space Type", "link_count": 0, "link_to": "GRM Space Type", "link_type": "DocType", "onboard": 0, "type": "Link"},
    {"hidden": 0, "is_query_report": 0, "label": "GRM Space", "link_count": 0, "link_to": "GRM Space", "link_type": "DocType", "onboard": 0, "type": "Link"},

    # Landlords & Contracts Card
    {"hidden": 0, "is_query_report": 0, "label": "Landlords & Contracts", "link_count": 0, "onboard": 0, "type": "Card Break"},
    {"hidden": 0, "is_query_report": 0, "label": "GRM Landlord", "link_count": 0, "link_to": "GRM Landlord", "link_type": "DocType", "onboard": 0, "type": "Link"},
    {"hidden": 0, "is_query_report": 0, "label": "GRM Property Contract", "link_count": 0, "link_to": "GRM Property Contract", "link_type": "DocType", "onboard": 0, "type": "Link"},

    # Members Card
    {"hidden": 0, "is_query_report": 0, "label": "Members", "link_count": 0, "onboard": 0, "type": "Card Break"},
    {"hidden": 0, "is_query_report": 0, "label": "GRM Member", "link_count": 0, "link_to": "GRM Member", "link_type": "DocType", "onboard": 0, "type": "Link"},
    {"hidden": 0, "is_query_report": 0, "label": "GRM Subscription Package", "link_count": 0, "link_to": "GRM Subscription Package", "link_type": "DocType", "onboard": 0, "type": "Link"},
    {"hidden": 0, "is_query_report": 0, "label": "GRM Subscription", "link_count": 0, "link_to": "GRM Subscription", "link_type": "DocType", "onboard": 0, "type": "Link"},

    # Operations Card
    {"hidden": 0, "is_query_report": 0, "label": "Operations", "link_count": 0, "onboard": 0, "type": "Card Break"},
    {"hidden": 0, "is_query_report": 0, "label": "GRM Booking", "link_count": 0, "link_to": "GRM Booking", "link_type": "DocType", "onboard": 0, "type": "Link"},
    {"hidden": 0, "is_query_report": 0, "label": "GRM Access Log", "link_count": 0, "link_to": "GRM Access Log", "link_type": "DocType", "onboard": 0, "type": "Link"},
    {"hidden": 0, "is_query_report": 0, "label": "Access Device", "link_count": 0, "link_to": "Access Device", "link_type": "DocType", "onboard": 0, "type": "Link"},
    {"hidden": 0, "is_query_report": 0, "label": "BioTime Settings", "link_count": 0, "link_to": "BioTime Settings", "link_type": "DocType", "onboard": 0, "type": "Link"},

    # Financial Card - ERPNext Integration
    {"hidden": 0, "is_query_report": 0, "label": "Financial", "link_count": 0, "onboard": 0, "type": "Card Break"},
    {"hidden": 0, "is_query_report": 0, "label": "Sales Invoice", "link_count": 0, "link_to": "Sales Invoice", "link_type": "DocType", "onboard": 0, "type": "Link"},
    {"hidden": 0, "is_query_report": 0, "label": "Payment Entry", "link_count": 0, "link_to": "Payment Entry", "link_type": "DocType", "onboard": 0, "type": "Link"},
    {"hidden": 0, "is_query_report": 0, "label": "Customer", "link_count": 0, "link_to": "Customer", "link_type": "DocType", "onboard": 0, "type": "Link"},
    {"hidden": 0, "is_query_report": 0, "label": "Supplier", "link_count": 0, "link_to": "Supplier", "link_type": "DocType", "onboard": 0, "type": "Link"},
    {"hidden": 0, "is_query_report": 0, "label": "Item", "link_count": 0, "link_to": "Item", "link_type": "DocType", "onboard": 0, "type": "Link"}
]

# Add shortcuts
data['shortcuts'] = [
    {"color": "Red", "doc_view": "List", "label": "GRM Location", "link_to": "GRM Location", "type": "DocType"},
    {"color": "Orange", "doc_view": "List", "label": "GRM Property", "link_to": "GRM Property", "type": "DocType"},
    {"color": "Grey", "doc_view": "List", "label": "GRM Space Type", "link_to": "GRM Space Type", "type": "DocType"},
    {"color": "Blue", "doc_view": "List", "label": "GRM Space", "link_to": "GRM Space", "type": "DocType"},
    {"color": "Purple", "doc_view": "List", "label": "GRM Landlord", "link_to": "GRM Landlord", "type": "DocType"},
    {"color": "Pink", "doc_view": "List", "label": "GRM Property Contract", "link_to": "GRM Property Contract", "type": "DocType"},
    {"color": "Cyan", "doc_view": "List", "label": "GRM Member", "link_to": "GRM Member", "type": "DocType"},
    {"color": "Green", "doc_view": "List", "label": "GRM Subscription Package", "link_to": "GRM Subscription Package", "type": "DocType"},
    {"color": "Orange", "doc_view": "List", "label": "GRM Subscription", "link_to": "GRM Subscription", "type": "DocType"},
    {"color": "Purple", "doc_view": "List", "label": "GRM Booking", "link_to": "GRM Booking", "type": "DocType"},
    {"color": "Yellow", "doc_view": "List", "label": "GRM Access Log", "link_to": "GRM Access Log", "type": "DocType"},
    {"color": "Green", "doc_view": "List", "label": "Sales Invoice", "link_to": "Sales Invoice", "type": "DocType"},
    {"color": "Blue", "doc_view": "List", "label": "Payment Entry", "link_to": "Payment Entry", "type": "DocType"}
]

data['modified'] = "2026-02-03 01:30:00.000000"

# Write updated JSON
with open('/home/frappe/frappe-bench/apps/grm_management/grm_management/grm_management/workspace/grm_coworking_space/grm_coworking_space.json', 'w') as f:
    json.dump(data, f, indent=1)

print("Workspace updated successfully with all shortcuts!")
