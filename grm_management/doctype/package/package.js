frappe.ui.form.on('Package', {
    access_type: function(frm) {
        if (frm.doc.access_type && frm.doc.access_type !== 'Unlimited') {
            frm.set_df_property('access_limit_value', 'reqd', 1);
        } else {
            frm.set_value('access_limit_value', null);
            frm.set_df_property('access_limit_value', 'reqd', 0);
        }
    },
    rollover_unused: function(frm) {
        if (frm.doc.rollover_unused) {
            frm.set_df_property('max_rollover', 'reqd', 1);
        } else {
            frm.set_value('max_rollover', null);
            frm.set_df_property('max_rollover', 'reqd', 0);
        }
    },
    access_24_7: function(frm) {
        if (frm.doc.access_24_7) {
            frm.set_value('access_start_time', null);
            frm.set_value('access_end_time', null);
            frm.toggle_display('access_start_time', false);
            frm.toggle_display('access_end_time', false);
        } else {
            frm.toggle_display('access_start_time', true);
            frm.toggle_display('access_end_time', true);
        }
    }
});