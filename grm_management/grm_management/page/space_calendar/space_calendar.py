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
def convert_booking_to_subscription(booking_id, tenant, package, subscription_type, start_date, end_date):
	"""Convert a booking to a subscription"""
	booking = frappe.get_doc('GRM Booking', booking_id)

	# Create subscription
	subscription = frappe.new_doc('GRM Subscription')
	subscription.tenant = tenant
	subscription.package = package if package else None
	subscription.subscription_type = subscription_type
	subscription.start_date = start_date
	subscription.end_date = end_date
	subscription.status = 'Active'

	# Add the space from booking
	subscription.append('spaces', {
		'space': booking.space,
		'start_date': start_date,
		'end_date': end_date
	})

	subscription.insert(ignore_permissions=True)

	# Mark booking as converted
	booking.status = 'Checked-out'
	booking.add_comment('Comment', f'Converted to subscription {subscription.name}')
	booking.save(ignore_permissions=True)

	return subscription.name

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
