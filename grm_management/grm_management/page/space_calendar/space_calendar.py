# -*- coding: utf-8 -*-
# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

@frappe.whitelist()
def get_bookings(start, end, location=None, space_type=None, space=None):
	"""Get bookings for calendar view"""
	filters = {
		'booking_date': ['between', [start, end]]
	}

	if space:
		filters['space'] = space
	elif space_type or location:
		# Get spaces matching criteria
		space_filters = {}
		if location:
			space_filters['location'] = location
		if space_type:
			space_filters['space_type'] = space_type

		spaces = frappe.get_all('GRM Space', filters=space_filters, pluck='name')
		if spaces:
			filters['space'] = ['in', spaces]
		else:
			return []

	bookings = frappe.get_all('GRM Booking',
		filters=filters,
		fields=[
			'name', 'booking_date', 'start_time', 'end_time',
			'space', 'member', 'status', 'duration_hours', 'total_amount'
		],
		order_by='booking_date, start_time'
	)

	# Enrich with space and member names
	for booking in bookings:
		booking['space_name'] = frappe.db.get_value('GRM Space', booking['space'], 'space_name')
		booking['member_name'] = frappe.db.get_value('GRM Member', booking['member'], 'full_name')

	return bookings

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
			'start': booking['start_time'],
			'end': booking['end_time'],
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
		if (start_time < booking['end_time'] and end_time > booking['start_time']):
			return {
				'conflict': True,
				'booking': booking['name'],
				'message': _('This space is already booked from {0} to {1}').format(
					booking['start_time'], booking['end_time']
				)
			}

	return {'conflict': False}
