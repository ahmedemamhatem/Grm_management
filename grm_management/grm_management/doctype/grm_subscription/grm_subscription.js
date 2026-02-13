// Copyright (c) 2026, Wael ELsafty and contributors
// For license information, please see license.txt

frappe.ui.form.on('GRM Subscription', {
	refresh: function(frm) {
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

		// Create Payment button - only for Active subscriptions with outstanding amount
		if (frm.doc.status === 'Active' && frm.doc.outstanding_amount > 0 && frm.doc.last_invoice && !frm.is_new()) {
			frm.add_custom_button(__('Create Payment'), function() {
				show_create_payment_dialog(frm);
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

		// Suspend/Resume buttons for Active subscriptions
		if (frm.doc.status === 'Active' && !frm.is_new()) {
			frm.add_custom_button(__('Suspend'), function() {
				frappe.confirm(__('Are you sure you want to suspend this subscription?'), function() {
					frm.set_value('status', 'Suspended');
					frm.save();
				});
			}, __('Actions'));
		}

		if (frm.doc.status === 'Suspended' && !frm.is_new()) {
			frm.add_custom_button(__('Resume'), function() {
				frm.set_value('status', 'Active');
				frm.save();
			}, __('Actions'));
		}

		// View last invoice link
		if (frm.doc.last_invoice) {
			frm.add_custom_button(__('View Last Invoice'), function() {
				frappe.set_route('Form', 'Sales Invoice', frm.doc.last_invoice);
			});
		}

		// Show outstanding amount prominently
		if (frm.doc.outstanding_amount > 0) {
			frm.dashboard.add_indicator(
				__('Outstanding: {0}', [format_currency(frm.doc.outstanding_amount)]),
				'orange'
			);
		}
	}
});

function show_create_payment_dialog(frm) {
	frappe.call({
		method: 'frappe.client.get',
		args: {
			doctype: 'Sales Invoice',
			name: frm.doc.last_invoice
		},
		callback: function(r) {
			if (!r.message) {
				frappe.msgprint(__('Invoice not found'));
				return;
			}

			let invoice = r.message;
			let outstanding = invoice.outstanding_amount || frm.doc.outstanding_amount;

			let d = new frappe.ui.Dialog({
				title: __('Create Payment for Subscription'),
				fields: [
					{
						fieldtype: 'Currency',
						fieldname: 'amount',
						label: __('Payment Amount'),
						default: outstanding,
						reqd: 1
					},
					{
						fieldtype: 'Link',
						fieldname: 'mode_of_payment',
						label: __('Mode of Payment'),
						options: 'Mode of Payment',
						reqd: 1
					},
					{
						fieldtype: 'Data',
						fieldname: 'reference_no',
						label: __('Reference No')
					},
					{
						fieldtype: 'Date',
						fieldname: 'reference_date',
						label: __('Reference Date'),
						default: frappe.datetime.get_today()
					}
				],
				primary_action_label: __('Create Payment'),
				primary_action: function(values) {
					frappe.call({
						method: 'grm_management.grm_management.doctype.grm_subscription.grm_subscription.create_payment_for_subscription',
						args: {
							subscription_name: frm.doc.name,
							invoice_name: frm.doc.last_invoice,
							amount: values.amount,
							mode_of_payment: values.mode_of_payment,
							reference_no: values.reference_no,
							reference_date: values.reference_date
						},
						freeze: true,
						freeze_message: __('Creating payment...'),
						callback: function(r) {
							if (r.message) {
								d.hide();
								frappe.msgprint({
									title: __('Payment Created'),
									message: __('Payment Entry {0} created successfully', [r.message]),
									indicator: 'green'
								});
								frm.reload_doc();
								frappe.set_route('Form', 'Payment Entry', r.message);
							}
						}
					});
				}
			});
			d.show();
		}
	});
}
