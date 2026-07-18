# Copyright (c) 2026, Your Organization and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class PermissionRequest(Document):
	def validate(self):
		if not self.role_profile and not self.module_profile:
			frappe.throw(
				_("Select at least one of {0} or {1} to request.").format(
					frappe.bold(_("Role Profile")), frappe.bold(_("Module Profile"))
				)
			)

		if self.user == "Administrator":
			frappe.throw(_("Permissions for {0} cannot be requested through this workflow.").format(
				frappe.bold("Administrator")
			))

		if not self.requested_by:
			self.requested_by = frappe.session.user

	def before_cancel(self):
		# Reaching Rejected goes through cancel(); require a reason so the
		# requester knows why the request was turned down.
		if self.workflow_state == "Rejected" and not self.approver_comments:
			frappe.throw(_("Please add {0} before rejecting this request.").format(
				frappe.bold(_("Approver Comments"))
			))

	def on_update_after_submit(self):
		if self.workflow_state == "Approved" and not self.applied:
			self.apply_permission_changes()

	def apply_permission_changes(self):
		user_doc = frappe.get_doc("User", self.user)

		if self.role_profile:
			user_doc.role_profile_name = self.role_profile

		if self.module_profile:
			user_doc.module_profile = self.module_profile

		user_doc.flags.ignore_permissions = True
		user_doc.save()

		self.db_set("applied", 1)
		self.db_set("applied_on", frappe.utils.now())

		frappe.msgprint(
			_("Applied requested permissions to {0}.").format(frappe.bold(self.user)),
			alert=True,
			indicator="green",
		)
