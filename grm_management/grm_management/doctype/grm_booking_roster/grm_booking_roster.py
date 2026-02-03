# -*- coding: utf-8 -*-
# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_days, get_datetime, time_diff_in_hours
import json

class GRMBookingRoster(Document):
	def validate(self):
		if self.from_date > self.to_date:
			frappe.throw("From Date cannot be greater than To Date")

	def get_roster_data(self):
		"""Get roster data for the date range"""
		spaces = self.get_spaces()
		dates = self.get_date_range()
		bookings = self.get_bookings()

		return {
			'spaces': spaces,
			'dates': dates,
			'bookings': bookings
		}

	def get_spaces(self):
		"""Get all spaces for the location"""
		filters = {'allow_booking': 1}
		if self.location:
			filters['location'] = self.location

		return frappe.get_all('GRM Space',
			filters=filters,
			fields=['name', 'space_name', 'space_type', 'capacity', 'hourly_rate'],
			order_by='space_type, space_name'
		)

	def get_date_range(self):
		"""Get list of dates in the range"""
		dates = []
		current_date = getdate(self.from_date)
		end_date = getdate(self.to_date)

		while current_date <= end_date:
			dates.append({
				'date': current_date,
				'weekday': current_date.strftime('%a'),
				'is_weekend': current_date.weekday() in [4, 5]  # Friday, Saturday
			})
			current_date = add_days(current_date, 1)

		return dates

	def get_bookings(self):
		"""Get all bookings in the date range"""
		filters = {
			'booking_date': ['between', [self.from_date, self.to_date]],
			'status': ['not in', ['Cancelled', 'No-show']]
		}

		if self.location:
			spaces = frappe.get_all('GRM Space',
				filters={'location': self.location},
				pluck='name'
			)
			if spaces:
				filters['space'] = ['in', spaces]

		bookings = frappe.get_all('GRM Booking',
			filters=filters,
			fields=[
				'name', 'space', 'member', 'booking_date',
				'start_time', 'end_time', 'status', 'duration_hours',
				'total_amount'
			]
		)

		# Enrich with member names
		for booking in bookings:
			booking['member_name'] = frappe.db.get_value('GRM Member', booking['member'], 'full_name')

		# Group by space and date
		grouped = {}
		for booking in bookings:
			key = f"{booking['space']}|{booking['booking_date']}"
			if key not in grouped:
				grouped[key] = []
			grouped[key].append(booking)

		return grouped

@frappe.whitelist()
def get_roster_html(name):
	"""Generate HTML for roster view"""
	doc = frappe.get_doc('GRM Booking Roster', name)
	data = doc.get_roster_data()

	html = '''
		<style>
			.roster-table {
				width: 100%;
				border-collapse: collapse;
				font-size: 12px;
			}
			.roster-table th, .roster-table td {
				border: 1px solid #d1d8dd;
				padding: 8px;
				text-align: center;
			}
			.roster-table th {
				background-color: #f0f4f7;
				font-weight: 600;
				position: sticky;
				top: 0;
				z-index: 10;
			}
			.roster-table .space-name {
				text-align: left;
				font-weight: 500;
				background-color: #f8f9fa;
				position: sticky;
				left: 0;
				z-index: 5;
			}
			.roster-table .weekend {
				background-color: #fff3cd;
			}
			.booking-cell {
				position: relative;
				min-height: 60px;
				vertical-align: top;
			}
			.booking-item {
				background: #d4edda;
				border: 1px solid #28a745;
				border-radius: 4px;
				padding: 4px;
				margin: 2px 0;
				font-size: 10px;
				cursor: pointer;
			}
			.booking-item:hover {
				background: #c3e6cb;
			}
			.booking-item.confirmed {
				background: #cce5ff;
				border-color: #007bff;
			}
			.booking-item.checked-in {
				background: #d4edda;
				border-color: #28a745;
			}
			.booking-item.draft {
				background: #e2e3e5;
				border-color: #6c757d;
			}
			.add-booking {
				color: #007bff;
				cursor: pointer;
				font-size: 18px;
				display: none;
			}
			.booking-cell:hover .add-booking {
				display: block;
			}
			.time-slot {
				font-size: 9px;
				color: #666;
			}
		</style>
		<div class="roster-container" style="overflow-x: auto;">
			<table class="roster-table">
				<thead>
					<tr>
						<th class="space-name" style="min-width: 150px;">Space</th>
	'''

	# Add date headers
	for date_info in data['dates']:
		weekend_class = 'weekend' if date_info['is_weekend'] else ''
		html += f'''
			<th class="{weekend_class}" style="min-width: 120px;">
				{date_info['weekday']}<br>
				{date_info['date'].strftime('%d/%m')}
			</th>
		'''

	html += '''
					</tr>
				</thead>
				<tbody>
	'''

	# Add space rows
	for space in data['spaces']:
		html += f'''
			<tr>
				<td class="space-name">
					<strong>{space['space_name']}</strong><br>
					<small class="text-muted">{space['space_type']}</small>
				</td>
		'''

		# Add booking cells for each date
		for date_info in data['dates']:
			key = f"{space['name']}|{date_info['date']}"
			bookings = data['bookings'].get(key, [])

			weekend_class = 'weekend' if date_info['is_weekend'] else ''
			html += f'<td class="booking-cell {weekend_class}" data-space="{space["name"]}" data-date="{date_info["date"]}">'

			# Add existing bookings
			for booking in bookings:
				status_class = booking['status'].lower().replace('-', '')
				html += f'''
					<div class="booking-item {status_class}"
						onclick="open_booking('{booking["name"]}')"
						title="{booking['member_name']}">
						<div class="time-slot">{booking['start_time'][:5]} - {booking['end_time'][:5]}</div>
						<div style="font-weight: 500;">{booking['member_name'][:15]}</div>
						<div class="text-muted">{booking['duration_hours']}h</div>
					</div>
				'''

			# Add button to create new booking
			html += f'''
				<div class="add-booking" onclick="create_booking('{space["name"]}', '{date_info["date"]}')">
					+
				</div>
			'''

			html += '</td>'

		html += '</tr>'

	html += '''
				</tbody>
			</table>
		</div>
		<script>
			function open_booking(name) {
				frappe.set_route('Form', 'GRM Booking', name);
			}

			function create_booking(space, date) {
				frappe.new_doc('GRM Booking', {
					space: space,
					booking_date: date
				});
			}

			// Refresh roster on form load
			frappe.ui.form.on('GRM Booking Roster', {
				refresh: function(frm) {
					frm.add_custom_button(__('Refresh Roster'), function() {
						frm.trigger('load_roster');
					});

					frm.trigger('load_roster');
				},
				from_date: function(frm) {
					frm.trigger('load_roster');
				},
				to_date: function(frm) {
					frm.trigger('load_roster');
				},
				location: function(frm) {
					frm.trigger('load_roster');
				},
				load_roster: function(frm) {
					if (frm.doc.name) {
						frappe.call({
							method: 'grm_management.grm_management.doctype.grm_booking_roster.grm_booking_roster.get_roster_html',
							args: {name: frm.doc.name},
							callback: function(r) {
								if (r.message) {
									frm.fields_dict.roster_html.$wrapper.html(r.message);
								}
							}
						});
					}
				}
			});
		</script>
	'''

	return html
