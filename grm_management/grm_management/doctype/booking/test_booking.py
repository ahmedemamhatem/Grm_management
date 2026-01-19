# Copyright (c) 2026, Wael ELsafty and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import ValidationError

class TestBooking(FrappeTestCase):
    def test_booking_overlap(self):
        # create minimal space
        space = frappe.get_doc({
            'doctype': 'Space',
            'space_name': 'Test Space 1'
        }).insert()

        # first booking - Confirmed
        b1 = frappe.get_doc({
            'doctype': 'Booking',
            'member': 'Guest',
            'space': space.name,
            'booking_date': frappe.utils.nowdate(),
            'start_time': '09:00',
            'end_time': '10:00',
            'rate_type': 'Hourly Rate',
            'hourly_rate': 10,
            'status': 'Confirmed'
        })
        b1.insert()

        # second booking overlapping should raise
        b2 = frappe.get_doc({
            'doctype': 'Booking',
            'member': 'Guest',
            'space': space.name,
            'booking_date': frappe.utils.nowdate(),
            'start_time': '09:30',
            'end_time': '10:30',
            'rate_type': 'Hourly Rate',
            'hourly_rate': 10,
            'status': 'Confirmed'
        })
        with self.assertRaises(ValidationError):
            b2.insert()

    def test_membership_decrement_on_checkin(self):
        # create package
        pkg = frappe.get_doc({
            'doctype': 'Package',
            'package_name': 'Test Package',
            'package_code': 'TPKG001',
            'package_category': 'Hot Desk',
            'status': 'Active',
            'billing_cycle': 'Monthly',
            'duration_value': 1,
            'price': 100,
            'access_type': 'Limited Entries',
            'access_limit_value': 2
        }).insert()

        # create member
        member = frappe.get_doc({'doctype':'Member','member_name':'Test Member'}).insert()

        mem = frappe.get_doc({
            'doctype': 'Membership',
            'member': member.name,
            'package': pkg.name,
            'status': 'Active',
            'start_date': frappe.utils.nowdate(),
            'end_date': frappe.utils.add_days(frappe.utils.nowdate(), 30),
            'package_price': pkg.price
        }).insert()

        space = frappe.get_doc({
            'doctype': 'Space',
            'space_name': 'Test Space 2'
        }).insert()

        b = frappe.get_doc({
            'doctype': 'Booking',
            'member': member.name,
            'space': space.name,
            'booking_date': frappe.utils.nowdate(),
            'start_time': '11:00',
            'end_time': '12:00',
            'rate_type': 'Package',
            'membership': mem.name,
            'status': 'Confirmed'
        }).insert()

        # change status to Checked-In and save
        b.status = 'Checked-In'
        b.save()

        mem.reload()
        self.assertEqual(mem.access_used, 1)
