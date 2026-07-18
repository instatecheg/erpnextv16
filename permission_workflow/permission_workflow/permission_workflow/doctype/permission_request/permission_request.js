// Copyright (c) 2026, Your Organization and contributors
// For license information, please see license.txt

frappe.ui.form.on("Permission Request", {
	refresh(frm) {
		frm.set_query("user", () => ({
			filters: { user_type: "System User", enabled: 1 },
		}));

		if (frm.doc.applied) {
			frm.dashboard.set_headline_alert(
				`<div class="indicator-pill green">${__("Applied to {0} on {1}", [
					frm.doc.user,
					frappe.datetime.str_to_user(frm.doc.applied_on),
				])}</div>`
			);
		}
	},
});
