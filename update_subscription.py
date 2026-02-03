#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to update GRM Subscription DocType JSON with all requirements:
1. Remove base_price - calculate from spaces
2. Add sales_taxes_and_charges_template
3. Add grand_total field
4. Update payment_frequency to be auto-set based on subscription type
5. Add member_name fetch field
"""

import json

# Read current JSON
with open('/home/frappe/frappe-bench/apps/grm_management/grm_management/grm_management/doctype/grm_subscription/grm_subscription.json', 'r') as f:
    data = json.load(f)

# Update field_order - remove base_price, add new fields
data['field_order'] = [
    "naming_series", "member", "member_name", "package", "column_break_1",
    "status", "subscription_type", "details_section", "start_date", "end_date",
    "duration_months", "column_break_details", "auto_renew", "next_renewal_date",
    "pricing_section", "sales_taxes_and_charges_template", "discount_amount",
    "column_break_pricing", "total_amount", "tax_amount", "grand_total",
    "payment_section", "payment_frequency", "next_invoice_date",
    "entry_based_section", "total_entries_allowed", "entries_used",
    "remaining_entries", "column_break_entry", "extra_entry_rate",
    "entry_overage_charges", "spaces_section", "spaces", "users_section",
    "authorized_users", "invoicing_section", "last_invoice", "total_invoiced",
    "column_break_invoicing", "total_paid", "outstanding_amount", "notes_section", "notes"
]

# Remove base_price field and update others
new_fields = []
for field in data['fields']:
    if field['fieldname'] == 'base_price':
        continue  # Remove base_price
    elif field['fieldname'] == 'member':
        new_fields.append(field)
        # Add member_name after member
        new_fields.append({
            "fieldname": "member_name",
            "fieldtype": "Data",
            "fetch_from": "member.full_name",
            "label": "Member Name | اسم المشترك",
            "read_only": 1
        })
    elif field['fieldname'] == 'pricing_section':
        new_fields.append(field)
        # Add sales tax template
        new_fields.append({
            "fieldname": "sales_taxes_and_charges_template",
            "fieldtype": "Link",
            "label": "Sales Taxes Template | قالب الضرائب",
            "options": "Sales Taxes and Charges Template"
        })
    elif field['fieldname'] == 'total_amount':
        field['label'] = "Total (Before Tax) | المبلغ قبل الضريبة"
        field['description'] = "Calculated from spaces table"
        new_fields.append(field)
    elif field['fieldname'] == 'tax_amount':
        new_fields.append(field)
        # Add grand_total after tax_amount
        new_fields.append({
            "fieldname": "grand_total",
            "fieldtype": "Currency",
            "label": "Grand Total | الإجمالي النهائي",
            "read_only": 1,
            "bold": 1
        })
    elif field['fieldname'] == 'payment_frequency':
        # Update to be read-only and add section before it
        new_fields.append({
            "fieldname": "payment_section",
            "fieldtype": "Section Break",
            "label": "Payment | الدفع"
        })
        field['read_only'] = 1
        field['description'] = "Auto-set based on subscription type"
        field['options'] = "One-time\nMonthly\nQuarterly\nAnnual"
        field.pop('default', None)
        new_fields.append(field)
    elif field['fieldname'] == 'spaces':
        field['reqd'] = 1
        field['description'] = "The main items for this subscription"
        new_fields.append(field)
    elif field['fieldname'] == 'authorized_users':
        field['description'] = "Linked from GRM Member companions/employees"
        new_fields.append(field)
    elif field['fieldname'] == 'notes':
        # Add notes_section before notes
        new_fields.append({
            "fieldname": "notes_section",
            "fieldtype": "Section Break",
            "label": "Notes | ملاحظات"
        })
        new_fields.append(field)
    else:
        new_fields.append(field)

data['fields'] = new_fields
data['modified'] = "2026-02-03 01:00:00.000000"

# Write updated JSON
with open('/home/frappe/frappe-bench/apps/grm_management/grm_management/grm_management/doctype/grm_subscription/grm_subscription.json', 'w') as f:
    json.dump(data, f, indent=1)

print("GRM Subscription JSON updated successfully!")
