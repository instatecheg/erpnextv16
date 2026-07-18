# Copyright (c) 2026, Your Organization and Contributors
# See license.txt

import frappe
from frappe.model.workflow import apply_workflow
from frappe.tests.utils import FrappeTestCase


class TestPermissionRequest(FrappeTestCase):
	def setUp(self):
		self.user = frappe.db.get_value("User", {"name": ["not in", ["Administrator", "Guest"]]})
		self.role_profile = frappe.db.get_value("Role Profile", {}, "name")
		if not self.role_profile:
			self.role_profile = frappe.get_doc(
				{"doctype": "Role Profile", "role_profile": "Test Role Profile"}
			).insert(ignore_permissions=True).name

	def test_request_is_not_applied_until_approved(self):
		if not self.user:
			self.skipTest("No non-admin user available to run this test against.")

		request = frappe.get_doc(
			{
				"doctype": "Permission Request",
				"request_type": "Modify Existing Permission",
				"user": self.user,
				"role_profile": self.role_profile,
				"reason": "Testing the approval workflow.",
			}
		).insert(ignore_permissions=True)

		self.assertEqual(request.workflow_state, "Draft")
		self.assertFalse(request.applied)

		apply_workflow(request, "Submit for Approval")
		request.reload()
		self.assertEqual(request.workflow_state, "Pending Approval")
		self.assertFalse(request.applied)

		request.approver_comments = "Looks good."
		apply_workflow(request, "Approve")
		request.reload()

		self.assertEqual(request.workflow_state, "Approved")
		self.assertTrue(request.applied)
		self.assertEqual(
			frappe.db.get_value("User", self.user, "role_profile_name"), self.role_profile
		)
