// Copyright (c) 2026, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('GRM Booking', {
	refresh: function(frm) {
		// Add Hijri date display
		if (frm.doc.booking_date) {
			update_hijri_date(frm);
		}

		// Status indicator colors
		if (frm.doc.status === 'Confirmed') {
			frm.page.set_indicator(__('Confirmed'), 'green');
		} else if (frm.doc.status === 'Draft') {
			frm.page.set_indicator(__('Draft'), 'orange');
		} else if (frm.doc.status === 'Checked-in') {
			frm.page.set_indicator(__('Checked-in'), 'blue');
		} else if (frm.doc.status === 'Checked-out') {
			frm.page.set_indicator(__('Checked-out'), 'grey');
		} else if (frm.doc.status === 'Cancelled') {
			frm.page.set_indicator(__('Cancelled'), 'red');
		}

		// Confirm button - only for Draft bookings
		if (frm.doc.status === 'Draft' && !frm.is_new()) {
			frm.add_custom_button(__('Confirm Booking'), function() {
				frappe.confirm(
					__('Confirm this booking?'),
					function() {
						frm.call('confirm_booking').then(() => {
							frm.reload_doc();
						});
					}
				);
			}, __('Actions'));
		}

		// Convert to Subscription button - only for Confirmed bookings not yet converted
		if (!frm.is_new() && ['Confirmed', 'Checked-in'].includes(frm.doc.status) && !frm.doc.converted_to_subscription) {
			frm.add_custom_button(__('Convert to Subscription'), function() {
				show_convert_to_subscription_dialog(frm);
			}, __('Actions'));
		}

		// Check-in button
		if (frm.doc.status === 'Confirmed' && !frm.is_new()) {
			frm.add_custom_button(__('Check In'), function() {
				frm.call('check_in').then(() => {
					frm.reload_doc();
				});
			}, __('Actions'));
		}

		// Check-out button
		if (frm.doc.status === 'Checked-in' && !frm.is_new()) {
			frm.add_custom_button(__('Check Out'), function() {
				frm.call('check_out').then(() => {
					frm.reload_doc();
				});
			}, __('Actions'));
		}

		// View Subscription link if converted
		if (frm.doc.converted_to_subscription) {
			frm.add_custom_button(__('View Subscription'), function() {
				frappe.set_route('Form', 'GRM Subscription', frm.doc.converted_to_subscription);
			});
		}
	},

	booking_date: function(frm) {
		// Update Hijri date when booking date changes
		if (frm.doc.booking_date) {
			update_hijri_date(frm);
		}
	},

	booking_type: function(frm) {
		// Set rate type based on booking type and fetch rate from space
		update_rate_from_space(frm);
	},

	space: function(frm) {
		// Fetch rate from space when space changes
		update_rate_from_space(frm);
	}
});

function update_rate_from_space(frm) {
	if (!frm.doc.space || !frm.doc.booking_type) return;

	// Set rate_type based on booking_type
	if (frm.doc.booking_type === 'Hourly') {
		frm.set_value('rate_type', 'Hourly');
	} else if (frm.doc.booking_type === 'Daily' || frm.doc.booking_type === 'Multi-day') {
		frm.set_value('rate_type', 'Daily');
	}

	// Fetch rate from space
	frappe.db.get_doc('GRM Space', frm.doc.space).then(space => {
		if (frm.doc.booking_type === 'Hourly') {
			frm.set_value('hourly_rate', space.hourly_rate || 0);
		} else if (frm.doc.booking_type === 'Daily' || frm.doc.booking_type === 'Multi-day') {
			frm.set_value('hourly_rate', space.daily_rate || 0);
		}
	});
}

function show_convert_to_subscription_dialog(frm) {
	// Calculate default end date based on subscription type
	let start_date = frm.doc.booking_date || frappe.datetime.get_today();
	let default_end_date = frm.doc.expiry_date || frappe.datetime.add_months(start_date, 1);

	let d = new frappe.ui.Dialog({
		title: __('Convert Booking to Subscription'),
		fields: [
			{
				fieldtype: 'Link',
				fieldname: 'tenant',
				label: __('Tenant'),
				options: 'GRM Tenant',
				reqd: 1,
				default: frm.doc.tenant,
				get_query: () => {
					return { filters: { 'status': 'Active' } };
				}
			},
			{
				fieldtype: 'Select',
				fieldname: 'subscription_type',
				label: __('Subscription Type'),
				options: 'Hourly\nDaily\nMonthly\nAnnual',
				default: 'Monthly',
				reqd: 1,
				onchange: function() {
					// Update end date based on subscription type
					let type = d.get_value('subscription_type');
					let s_date = d.get_value('start_date');
					if (s_date) {
						let new_end;
						if (type === 'Hourly' || type === 'Daily') {
							new_end = s_date;
						} else if (type === 'Monthly') {
							new_end = frappe.datetime.add_months(s_date, 1);
						} else if (type === 'Annual') {
							new_end = frappe.datetime.add_months(s_date, 12);
						}
						d.set_value('end_date', new_end);
					}
				}
			},
			{
				fieldtype: 'Date',
				fieldname: 'start_date',
				label: __('Start Date'),
				default: start_date,
				reqd: 1,
				onchange: function() {
					// Recalculate end date when start date changes
					let type = d.get_value('subscription_type');
					let s_date = d.get_value('start_date');
					if (s_date && type) {
						let new_end;
						if (type === 'Hourly' || type === 'Daily') {
							new_end = s_date;
						} else if (type === 'Monthly') {
							new_end = frappe.datetime.add_months(s_date, 1);
						} else if (type === 'Annual') {
							new_end = frappe.datetime.add_months(s_date, 12);
						}
						d.set_value('end_date', new_end);
					}
				}
			},
			{
				fieldtype: 'Date',
				fieldname: 'end_date',
				label: __('End Date'),
				default: default_end_date,
				reqd: 1
			},
			{
				fieldtype: 'Section Break'
			},
			{
				fieldtype: 'HTML',
				options: '<p class="text-muted">' + __('This will create a Subscription, generate a Sales Invoice, and record Payment automatically.') + '</p>'
			}
		],
		primary_action_label: __('Convert'),
		primary_action: function(values) {
			frappe.call({
				method: 'grm_management.grm_management.page.space_calendar.space_calendar.convert_booking_to_subscription',
				args: {
					booking_id: frm.doc.name,
					tenant: values.tenant,
					subscription_type: values.subscription_type,
					start_date: values.start_date,
					end_date: values.end_date
				},
				freeze: true,
				freeze_message: __('Converting booking...'),
				callback: function(r) {
					if (r.message) {
						d.hide();
						frappe.msgprint({
							title: __('Conversion Successful'),
							message: `
								<p><b>${__('Subscription')}:</b> ${r.message.subscription}</p>
								<p><b>${__('Invoice')}:</b> ${r.message.invoice}</p>
								<p><b>${__('Payment')}:</b> ${r.message.payment}</p>
							`,
							indicator: 'green'
						});
						frm.reload_doc();
						// Navigate to subscription
						frappe.set_route('Form', 'GRM Subscription', r.message.subscription);
					}
				}
			});
		}
	});
	d.show();
}

function update_hijri_date(frm) {
	frappe.call({
		method: 'grm_management.grm_management.utils.hijri_utils.get_hijri_date',
		args: {
			gregorian_date: frm.doc.booking_date
		},
		callback: function(r) {
			if (r.message) {
				const hijri = r.message;
				const hijri_html = `
					<div style="padding: 10px; background-color: #f8f9fa; border-radius: 5px; margin-top: 10px;">
						<strong>📅 Hijri Date | التاريخ الهجري:</strong><br>
						<span style="font-size: 14px; direction: rtl;">
							${hijri.formatted_ar}
						</span><br>
						<span style="font-size: 12px; color: #666;">
							${hijri.formatted}
						</span>
					</div>
				`;

				// Check if hijri_date_display field exists, if not add it
				if (!frm.fields_dict.hijri_date_display) {
					// Add custom HTML field dynamically
					frm.set_df_property('booking_date', 'description', hijri_html);
				}
			}
		}
	});
}
