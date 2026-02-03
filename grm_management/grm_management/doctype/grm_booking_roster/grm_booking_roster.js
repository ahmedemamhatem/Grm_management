// Copyright (c) 2026, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('GRM Booking Roster', {
	refresh: function(frm) {
		// Set default to_date (7 days from from_date)
		if (frm.doc.from_date && !frm.doc.to_date) {
			frm.set_value('to_date', frappe.datetime.add_days(frm.doc.from_date, 6));
		}

		// Add custom buttons
		frm.add_custom_button(__('Refresh Roster'), function() {
			frm.trigger('load_roster');
		});

		frm.add_custom_button(__('Export'), function() {
			frappe.msgprint(__('Export functionality will be added soon'));
		});

		// Load roster after fields are set
		setTimeout(() => {
			frm.trigger('load_roster');
		}, 500);
	},

	from_date: function(frm) {
		if (frm.doc.from_date && !frm.doc.to_date) {
			frm.set_value('to_date', frappe.datetime.add_days(frm.doc.from_date, 6));
		}
		frm.trigger('load_roster');
	},

	to_date: function(frm) {
		frm.trigger('load_roster');
	},

	location: function(frm) {
		frm.trigger('load_roster');
	},

	load_roster: function(frm) {
		if (!frm.doc.name || !frm.doc.from_date || !frm.doc.to_date) {
			return;
		}

		frappe.call({
			method: 'grm_management.grm_management.doctype.grm_booking_roster.grm_booking_roster.get_roster_html',
			args: {
				name: frm.doc.name
			},
			callback: function(r) {
				if (r.message) {
					frm.fields_dict.roster_html.$wrapper.html(r.message);
				}
			}
		});
	}
});
