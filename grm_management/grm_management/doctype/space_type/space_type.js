// Copyright (c) 2026, Wael ELsafty and contributors
// For license information, please see license.txt

const togglePricingFields = (frm) => {
	const hasField = (fieldname) => !!frm.fields_dict[fieldname];

	const allowHourly = !!frm.doc.allow_hourly;
	const allowDaily = !!frm.doc.allow_daily;
	const allowMonthly = !!frm.doc.allow_monthly;

	if (hasField("hourly_rate")) {
		frm.toggle_display("hourly_rate", allowHourly);
	}
	if (hasField("min_booking_hours")) {
		frm.toggle_display("min_booking_hours", allowHourly);
	}
	if (hasField("max_booking_hours")) {
		frm.toggle_display("max_booking_hours", allowHourly);
	}
	if (hasField("daily_rate")) {
		frm.toggle_display("daily_rate", allowDaily);
	}
	if (hasField("monthly_rate")) {
		frm.toggle_display("monthly_rate", allowMonthly);
	}
	// Assumption: weekly_rate follows allow_daily for visibility.
	if (hasField("weekly_rate")) {
		frm.toggle_display("weekly_rate", allowDaily);
	}
};

frappe.ui.form.on("Space Type", {
	refresh: togglePricingFields,
	allow_hourly: togglePricingFields,
	allow_daily: togglePricingFields,
	allow_monthly: togglePricingFields,
});