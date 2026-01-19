// Copyright (c) 2026, Wael ELsafty and contributors
// For license information, please see license.txt

const toggleHoursFields = (frm) => {
	const is24Hours = !!frm.doc.is_24_hours;
	frm.toggle_display(["opening_time", "closing_time"], !is24Hours);
	if (is24Hours) {
		frm.set_value("opening_time", null);
		frm.set_value("closing_time", null);
	}
};

frappe.ui.form.on("Operating Hours", {
	refresh: toggleHoursFields,
	is_24_hours: toggleHoursFields,
});
