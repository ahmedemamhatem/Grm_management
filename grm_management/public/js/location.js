// Copyright (c) 2026, Wael ELsafty and contributors
// For license information, please see license.txt

const costFields = [
	"electricity_budget",
	"water_budget",
	"internet_cost",
	"cleaning_cost",
	"security_cost",
	"maintenance_budget",
	"other_fixed_costs",
];

const updateTotal = (frm) => {
	let total = 0;
	costFields.forEach((field) => {
		total += flt(frm.doc[field]);
	});
	frm.set_value("total_monthly_costs", total);
    console.log("Totxal monthly costs updated to:", total);
};

frappe.ui.form.on("Location", {
	refresh(frm) {
		updateTotal(frm);
        
	},
	electricity_budget: updateTotal,
	water_budget: updateTotal,
	internet_cost: updateTotal,
	cleaning_cost: updateTotal,
	security_cost: updateTotal,
	maintenance_budget: updateTotal,
	other_fixed_costs: updateTotal,
});

const toggleHoursFields = (frm) => {
	const is24Hours = !!frm.doc.is_24_hours;
	frm.toggle_display(["opening_time", "closing_time"], !is24Hours);
	if (is24Hours) {
		frm.set_value("opening_time", null);
		frm.set_value("closing_time", null);
	}
};

frappe.ui.form.on("Location", {
	refresh: toggleHoursFields,
	is_24_hours: toggleHoursFields,
});
