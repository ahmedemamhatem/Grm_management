// Copyright (c) 2026, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('GRM Booking', {
	refresh: function(frm) {
		// Add Hijri date display
		if (frm.doc.booking_date) {
			update_hijri_date(frm);
		}
	},

	booking_date: function(frm) {
		// Update Hijri date when booking date changes
		if (frm.doc.booking_date) {
			update_hijri_date(frm);
		}
	}
});

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
