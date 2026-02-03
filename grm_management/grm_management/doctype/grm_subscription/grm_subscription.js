// Copyright (c) 2026, Wael ELsafty and contributors
// For license information, please see license.txt

frappe.ui.form.on('GRM Subscription', {
	refresh: function(frm) {
		// Activate button - only for Draft subscriptions
		if (frm.doc.status === 'Draft' && !frm.is_new()) {
			frm.add_custom_button(__('Activate Subscription'), function() {
				frappe.confirm(
					__('This will activate the subscription and mark all spaces as Rented. Continue?'),
					function() {
						frm.call('activate').then(() => {
							frm.reload_doc();
						});
					}
				);
			}, __('Actions'));
		}

		// Create Invoice button - only for Active subscriptions
		if (frm.doc.status === 'Active' && !frm.is_new()) {
			frm.add_custom_button(__('Create Invoice'), function() {
				frm.call('create_invoice').then((r) => {
					if (r.message) {
						frm.reload_doc();
						frappe.set_route('Form', 'Sales Invoice', r.message);
					}
				});
			}, __('Actions'));
		}

		// Record Entry button - only for Entry-based Active subscriptions
		if (frm.doc.status === 'Active' && frm.doc.subscription_type === 'Entry-based' && !frm.is_new()) {
			frm.add_custom_button(__('Record Entry'), function() {
				frm.call('record_entry').then(() => {
					frm.reload_doc();
				});
			}, __('Actions'));
		}

		// View last invoice link
		if (frm.doc.last_invoice) {
			frm.add_custom_button(__('View Last Invoice'), function() {
				frappe.set_route('Form', 'Sales Invoice', frm.doc.last_invoice);
			});
		}

		// Status indicator colors
		if (frm.doc.status === 'Active') {
			frm.page.set_indicator(__('Active'), 'green');
		} else if (frm.doc.status === 'Draft') {
			frm.page.set_indicator(__('Draft'), 'orange');
		} else if (frm.doc.status === 'Expired') {
			frm.page.set_indicator(__('Expired'), 'red');
		} else if (frm.doc.status === 'Cancelled') {
			frm.page.set_indicator(__('Cancelled'), 'grey');
		} else if (frm.doc.status === 'Suspended') {
			frm.page.set_indicator(__('Suspended'), 'yellow');
		}
	}
});
