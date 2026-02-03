# -*- coding: utf-8 -*-
# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate, add_days, get_datetime, nowdate

@frappe.whitelist()
def get_calendar_data(start_date, end_date, location=None, space_type=None, space=None):
	"""Get calendar data with bookings and spaces"""
	# Get spaces
	space_filters = {'allow_booking': 1}
	if location:
		space_filters['location'] = location
	if space_type:
		space_filters['space_type'] = space_type
	if space:
		space_filters['name'] = space

	spaces = frappe.get_all('GRM Space',
		filters=space_filters,
		fields=['name', 'space_name', 'space_type', 'capacity', 'hourly_rate'],
		order_by='space_type, space_name'
	)

	# Get bookings
	booking_filters = {
		'booking_date': ['between', [start_date, end_date]],
		'status': ['not in', ['Cancelled']]
	}

	if space:
		booking_filters['space'] = space
	elif spaces:
		booking_filters['space'] = ['in', [s['name'] for s in spaces]]

	bookings = frappe.get_all('GRM Booking',
		filters=booking_filters,
		fields=[
			'name', 'space', 'tenant', 'booking_date',
			'start_time', 'end_time', 'status', 'duration_hours',
			'total_amount', 'expiry_date'
		],
		order_by='booking_date, start_time'
	)

	# Enrich bookings with tenant names and expiry status
	for booking in bookings:
		booking['tenant_name'] = frappe.db.get_value('GRM Tenant', booking.get('tenant'), 'tenant_name') or 'Unknown'
		booking['booking_date'] = str(booking['booking_date'])

		# Check if booking has expired
		if booking['expiry_date']:
			booking['is_expired'] = getdate(booking['expiry_date']) < getdate(nowdate())
		else:
			booking['is_expired'] = False

	return {
		'spaces': spaces,
		'bookings': bookings
	}

@frappe.whitelist()
def create_booking(space, tenant, booking_date, start_time, end_time, booking_type, sales_taxes_and_charges_template=None, expiry_days=7):
	"""Create a new booking with expiry"""
	# Check for conflicts
	conflict = check_space_conflict(space, booking_date, start_time, end_time)
	if conflict['conflict']:
		frappe.throw(conflict['message'])

	# Create booking
	booking = frappe.new_doc('GRM Booking')
	booking.space = space
	booking.tenant = tenant
	booking.booking_date = booking_date
	booking.start_time = start_time
	booking.end_time = end_time
	booking.booking_type = booking_type
	booking.status = 'Confirmed'

	# Set expiry date
	booking.expiry_date = add_days(booking_date, int(expiry_days))

	# Set sales tax template
	if sales_taxes_and_charges_template:
		booking.sales_taxes_and_charges_template = sales_taxes_and_charges_template

	# Calculate pricing from space
	space_doc = frappe.get_doc('GRM Space', space)
	if booking_type == 'Hourly':
		booking.hourly_rate = space_doc.hourly_rate
	elif booking_type == 'Daily':
		booking.hourly_rate = space_doc.daily_rate

	booking.insert(ignore_permissions=True)

	return booking.name

@frappe.whitelist()
def convert_booking_to_subscription(booking_id, tenant, subscription_type, start_date, end_date):
	"""Convert a booking to a subscription, create invoice and payment"""
	booking = frappe.get_doc('GRM Booking', booking_id)

	# Create subscription (starts as Draft, then activate)
	subscription = frappe.new_doc('GRM Subscription')
	subscription.tenant = tenant
	subscription.subscription_type = subscription_type
	subscription.start_date = start_date
	subscription.end_date = end_date
	subscription.status = 'Draft'

	# Add the space from booking
	subscription.append('spaces', {
		'space': booking.space,
		'start_date': start_date,
		'end_date': end_date
	})

	subscription.insert(ignore_permissions=True)

	# Activate the subscription (marks spaces as Rented)
	subscription.status = 'Active'
	for space_row in subscription.spaces:
		space_doc = frappe.get_doc('GRM Space', space_row.space)
		space_doc.status = 'Rented'
		space_doc.current_tenant = tenant
		space_doc.current_subscription = subscription.name
		space_doc.save(ignore_permissions=True)
	subscription.save(ignore_permissions=True)

	# Create Sales Invoice
	invoice = create_subscription_invoice(subscription)

	# Create Payment Entry
	payment = create_subscription_payment(invoice, subscription.tenant)

	# Update subscription with invoice details
	subscription.last_invoice = invoice.name
	subscription.total_invoiced = invoice.grand_total
	subscription.total_paid = payment.paid_amount
	subscription.outstanding_amount = invoice.outstanding_amount
	subscription.save(ignore_permissions=True)

	# Mark booking as converted and link to subscription
	booking.status = 'Checked-out'
	booking.converted_to_subscription = subscription.name
	booking.add_comment('Comment', f'Converted to subscription {subscription.name}. Invoice: {invoice.name}, Payment: {payment.name}')
	booking.save(ignore_permissions=True)

	frappe.db.commit()

	return {
		'subscription': subscription.name,
		'invoice': invoice.name,
		'payment': payment.name
	}

def create_subscription_invoice(subscription):
	"""Create Sales Invoice for subscription"""
	from frappe.utils import get_datetime, nowdate

	# Get tenant's customer
	customer = frappe.db.get_value('GRM Tenant', subscription.tenant, 'customer')
	if not customer:
		frappe.throw(_('No customer linked to tenant {0}').format(subscription.tenant))

	# Get company (default or first available)
	company = frappe.defaults.get_user_default("Company") or frappe.get_all("Company", limit=1)[0].name

	# Create invoice
	invoice = frappe.new_doc('Sales Invoice')
	invoice.customer = customer
	invoice.company = company
	invoice.posting_date = nowdate()
	invoice.due_date = nowdate()
	invoice.grm_subscription = subscription.name

	# Add subscription spaces as invoice items
	for space_row in subscription.spaces:
		space = frappe.get_doc('GRM Space', space_row.space)

		# Determine rate based on subscription type
		rate = 0
		description = f"Subscription: {subscription.subscription_type}"
		if subscription.subscription_type == 'Monthly':
			rate = space.monthly_rate or 0
			description += f" - {space.space_name}"
		elif subscription.subscription_type == 'Daily':
			rate = space.daily_rate or 0
			description += f" - {space.space_name}"
		elif subscription.subscription_type == 'Hourly':
			rate = space.hourly_rate or 0
			description += f" - {space.space_name}"

		invoice.append('items', {
			'item_code': space.item or create_space_item(space),
			'item_name': space.space_name,
			'description': description,
			'qty': 1,
			'rate': rate,
			'amount': rate
		})

	# Add taxes if subscription has tax template
	if subscription.sales_taxes_and_charges_template:
		invoice.taxes_and_charges = subscription.sales_taxes_and_charges_template
		invoice.set_taxes()

	invoice.insert(ignore_permissions=True)
	invoice.submit()

	return invoice

def create_subscription_payment(invoice, tenant):
	"""Create Payment Entry for invoice"""
	from frappe.utils import nowdate

	# Get company
	company = invoice.company

	# Get mode of payment (default Cash or first available)
	mode_of_payment = frappe.db.get_value('Mode of Payment', {'enabled': 1}, 'name') or 'Cash'

	# Get default accounts
	payment_account = frappe.db.get_value('Mode of Payment Account',
		{'parent': mode_of_payment, 'company': company}, 'default_account')

	if not payment_account:
		payment_account = frappe.db.get_value('Account',
			{'account_type': 'Cash', 'company': company, 'is_group': 0}, 'name')

	# Create payment entry
	payment = frappe.new_doc('Payment Entry')
	payment.payment_type = 'Receive'
	payment.party_type = 'Customer'
	payment.party = invoice.customer
	payment.company = company
	payment.posting_date = nowdate()
	payment.paid_from = frappe.db.get_value('Account',
		{'account_type': 'Receivable', 'company': company, 'is_group': 0}, 'name')
	payment.paid_to = payment_account
	payment.paid_amount = invoice.grand_total
	payment.received_amount = invoice.grand_total
	payment.mode_of_payment = mode_of_payment
	payment.reference_no = invoice.name
	payment.reference_date = nowdate()

	# Link to invoice
	payment.append('references', {
		'reference_doctype': 'Sales Invoice',
		'reference_name': invoice.name,
		'allocated_amount': invoice.grand_total
	})

	payment.insert(ignore_permissions=True)
	payment.submit()

	return payment

def create_space_item(space):
	"""Create Item for space if not exists"""
	item_code = f"SPACE-{space.name}"

	if frappe.db.exists('Item', item_code):
		return item_code

	# Find the Services item group (may be translated, e.g. الخدمات)
	item_group = frappe.db.get_value('Item Group', 'Services', 'name') or \
		frappe.db.get_value('Item Group', 'الخدمات', 'name')
	if not item_group:
		item_group = frappe.db.get_all('Item Group', filters={'is_group': 0}, limit=1, pluck='name')[0]

	item = frappe.new_doc('Item')
	item.item_code = item_code
	item.item_name = space.space_name
	item.item_group = item_group
	item.stock_uom = 'Nos'
	item.is_stock_item = 0
	item.is_sales_item = 1
	item.description = f"Coworking Space: {space.space_name}"
	item.insert(ignore_permissions=True)

	# Update space with item reference
	frappe.db.set_value('GRM Space', space.name, 'item', item_code)

	return item_code

@frappe.whitelist()
def get_space_availability(date, location=None, space_type=None):
	"""Get space availability for a specific date"""
	# Get all spaces
	filters = {}
	if location:
		filters['location'] = location
	if space_type:
		filters['space_type'] = space_type

	filters['status'] = ['in', ['Available', 'Rented']]
	filters['allow_booking'] = 1

	spaces = frappe.get_all('GRM Space',
		filters=filters,
		fields=['name', 'space_name', 'space_type', 'capacity', 'status', 'hourly_rate']
	)

	# Get bookings for this date
	bookings = frappe.get_all('GRM Booking',
		filters={
			'booking_date': date,
			'status': ['not in', ['Cancelled', 'No-show']]
		},
		fields=['space', 'start_time', 'end_time', 'status']
	)

	# Create booking map
	booking_map = {}
	for booking in bookings:
		if booking['space'] not in booking_map:
			booking_map[booking['space']] = []
		booking_map[booking['space']].append({
			'start': str(booking['start_time']),
			'end': str(booking['end_time']),
			'status': booking['status']
		})

	# Add availability info to spaces
	for space in spaces:
		space['bookings'] = booking_map.get(space['name'], [])
		space['is_available'] = len(space['bookings']) == 0

	return spaces

@frappe.whitelist()
def check_space_conflict(space, booking_date, start_time, end_time, exclude_booking=None):
	"""Check if there's a booking conflict for a space"""
	filters = {
		'space': space,
		'booking_date': booking_date,
		'status': ['not in', ['Cancelled', 'No-show']]
	}

	if exclude_booking:
		filters['name'] = ['!=', exclude_booking]

	existing_bookings = frappe.get_all('GRM Booking',
		filters=filters,
		fields=['start_time', 'end_time', 'name']
	)

	for booking in existing_bookings:
		# Check for time overlap
		if (start_time < str(booking['end_time']) and end_time > str(booking['start_time'])):
			return {
				'conflict': True,
				'booking': booking['name'],
				'message': _('This space is already booked from {0} to {1}').format(
					booking['start_time'], booking['end_time']
				)
			}

	return {'conflict': False}

@frappe.whitelist()
def mark_expired_bookings():
	"""Scheduled task to mark expired bookings"""
	expired_bookings = frappe.get_all('GRM Booking',
		filters={
			'expiry_date': ['<', nowdate()],
			'status': ['in', ['Draft', 'Confirmed']],
			'docstatus': ['<', 2]
		},
		pluck='name'
	)

	for booking_name in expired_bookings:
		booking = frappe.get_doc('GRM Booking', booking_name)
		booking.status = 'No-show'
		booking.add_comment('Comment', 'Booking expired - not converted to subscription')
		booking.save(ignore_permissions=True)

	if expired_bookings:
		frappe.db.commit()
		return len(expired_bookings)
	return 0
