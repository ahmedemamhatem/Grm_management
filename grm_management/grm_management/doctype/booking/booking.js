frappe.ui.form.on('Booking', {
    rate_type: function(frm) {
        frm.toggle_display('hourly_rate', frm.doc.rate_type === 'Hourly Rate');
        frm.toggle_display('daily_rate', frm.doc.rate_type === 'Daily Rate');
        frm.toggle_display('membership', frm.doc.rate_type === 'Package');
    },
    start_time: function(frm) {
        if (frm.doc.start_time && frm.doc.end_time) {
            frm.trigger('recalc_duration');
        }
    },
    end_time: function(frm) {
        if (frm.doc.start_time && frm.doc.end_time) {
            frm.trigger('recalc_duration');
        }
    },
    recalc_duration: function(frm) {
        // simple client-side calculation
        if (frm.doc.start_time && frm.doc.end_time) {
            var s = frappe.datetime.str_to_obj(frm.doc.start_time);
            var e = frappe.datetime.str_to_obj(frm.doc.end_time);
            var diff = (e.getTime() - s.getTime())/1000/3600;
            frm.set_value('duration_hours', diff > 0 ? diff : 0);
        }
    },
    membership: function(frm) {
        if (frm.doc.membership) {
            frappe.db.get_doc('Membership', frm.doc.membership).then(mem => {
                if (mem.status !== 'Active') {
                    frappe.msgprint(__('Selected membership is not active'));
                }
            });
        }
    }
});