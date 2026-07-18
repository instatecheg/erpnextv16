import frappe

from permission_workflow.setup.construction_profiles import create_construction_profiles

ROLES = ["Permission Requester", "Permission Approver"]

# (state, doc_status, style)
WORKFLOW_STATES = [
	("Draft", "0", "warning"),
	("Pending Approval", "1", "warning"),
	("Approved", "1", "success"),
	("Rejected", "2", "danger"),
]

WORKFLOW_ACTIONS = ["Submit for Approval", "Approve", "Reject"]

# (state, action, next_state, allowed_role)
TRANSITIONS = [
	("Draft", "Submit for Approval", "Pending Approval", "Permission Requester"),
	("Pending Approval", "Approve", "Approved", "Permission Approver"),
	("Pending Approval", "Reject", "Rejected", "Permission Approver"),
]

WORKFLOW_NAME = "Permission Request Approval"


def after_install():
	create_permission_workflow()


def create_permission_workflow():
	create_roles()
	create_workflow_states()
	create_workflow_actions()
	create_workflow()
	create_construction_profiles()
	frappe.db.commit()


def create_roles():
	for role in ROLES:
		if not frappe.db.exists("Role", role):
			frappe.get_doc({
				"doctype": "Role",
				"role_name": role,
				"desk_access": 1,
			}).insert(ignore_permissions=True)


def create_workflow_states():
	for state, doc_status, style in WORKFLOW_STATES:
		if not frappe.db.exists("Workflow State", state):
			frappe.get_doc({
				"doctype": "Workflow State",
				"workflow_state_name": state,
				"style": style,
			}).insert(ignore_permissions=True)


def create_workflow_actions():
	for action in WORKFLOW_ACTIONS:
		if not frappe.db.exists("Workflow Action Master", action):
			frappe.get_doc({
				"doctype": "Workflow Action Master",
				"workflow_action_name": action,
			}).insert(ignore_permissions=True)


def create_workflow():
	if frappe.db.exists("Workflow", WORKFLOW_NAME):
		return

	workflow = frappe.new_doc("Workflow")
	workflow.workflow_name = WORKFLOW_NAME
	workflow.document_type = "Permission Request"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.send_email_alert = 0

	edit_role_by_state = {
		"Draft": "Permission Requester",
		"Pending Approval": "Permission Approver",
		"Approved": "System Manager",
		"Rejected": "System Manager",
	}

	for state, doc_status, _style in WORKFLOW_STATES:
		workflow.append("states", {
			"state": state,
			"doc_status": doc_status,
			"allow_edit": edit_role_by_state[state],
		})

	for state, action, next_state, allowed_role in TRANSITIONS:
		workflow.append("transitions", {
			"state": state,
			"action": action,
			"next_state": next_state,
			"allowed": allowed_role,
		})

	workflow.insert(ignore_permissions=True)
