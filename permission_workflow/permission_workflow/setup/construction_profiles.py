"""Seeds Role Profiles and Module Profiles that match a typical construction
company's departments and reporting hierarchy, built entirely from Roles
and Modules that already ship with ERPNext (see README for exact sources).
Role Profiles bundle existing ERPNext roles per department/level; Module
Profiles hide the workspaces that department doesn't need. Both are
starting points, meant to be reviewed and adjusted per company, not final.
"""

import frappe

# Workspaces we manage visibility for. Left out on purpose: Utilities,
# Portal, Regional, ERPNext Integrations, Communication, Telephony, Bulk
# Transaction, EDI - cross-cutting/rarely-used sidebar items not worth
# restricting per department.
MANAGED_MODULES = [
	"Accounts",
	"CRM",
	"Buying",
	"Projects",
	"Selling",
	"Setup",
	"Manufacturing",
	"Stock",
	"Support",
	"Assets",
	"Maintenance",
	"Quality Management",
	"Subcontracting",
]

# department -> {module_profile: [...modules visible...], levels: {level_name: [...roles...]}}
DEPARTMENTS = {
	"Executive": {
		"modules_allowed": MANAGED_MODULES,
		"levels": {
			"Director": [
				"Projects Manager", "Purchase Manager", "Purchase Master Manager",
				"Sales Manager", "Sales Master Manager", "Stock Manager",
				"Accounts Manager", "Auditor", "HR Manager", "Quality Manager",
				"Manufacturing Manager", "Maintenance Manager", "Fleet Manager",
			],
		},
	},
	"Project & Site Engineering": {
		"modules_allowed": ["Projects", "Stock", "Quality Management", "Maintenance", "Buying", "Setup"],
		"levels": {
			"Manager": ["Projects Manager", "Stock User", "Purchase User", "Quality Manager", "Maintenance User"],
			"Engineer": ["Projects User", "Stock User", "Maintenance User"],
		},
	},
	"Procurement": {
		"modules_allowed": ["Buying", "Stock", "Setup"],
		"levels": {
			"Manager": ["Purchase Manager", "Purchase Master Manager", "Stock User"],
			"Officer": ["Purchase User", "Stock User"],
		},
	},
	"Warehouse & Equipment": {
		"modules_allowed": ["Stock", "Assets", "Maintenance", "Setup"],
		"levels": {
			"Manager": ["Stock Manager", "Fleet Manager", "Maintenance Manager"],
			"Store Keeper": ["Stock User", "Maintenance User", "Operator"],
		},
	},
	"Finance & Accounts": {
		"modules_allowed": ["Accounts", "Buying", "Selling", "Setup"],
		"levels": {
			"Manager": ["Accounts Manager", "Auditor"],
			"Accountant": ["Accounts User"],
		},
	},
	"HR & Admin": {
		"modules_allowed": ["Setup", "Support"],
		"levels": {
			"Manager": ["HR Manager"],
			"Officer": ["HR User", "Employee Self Service"],
		},
	},
	"Business Development": {
		"modules_allowed": ["CRM", "Selling", "Setup"],
		"levels": {
			"Manager": ["Sales Manager", "Sales Master Manager"],
			"Executive": ["Sales User"],
		},
	},
	"Quality & Safety": {
		"modules_allowed": ["Quality Management", "Projects", "Maintenance", "Setup"],
		"levels": {
			"Manager": ["Quality Manager", "Maintenance Manager"],
			"Inspector": ["Quality Manager", "Projects User"],
		},
	},
	"Manufacturing & Fabrication": {
		"modules_allowed": ["Manufacturing", "Stock", "Subcontracting", "Setup"],
		"levels": {
			"Manager": ["Manufacturing Manager", "Shop Floor Manager"],
			"Operator": ["Manufacturing User", "Shop Floor User", "Operator"],
		},
	},
}


def create_construction_profiles():
	for department, config in DEPARTMENTS.items():
		module_profile_name = create_module_profile(department, config["modules_allowed"])

		for level, roles in config["levels"].items():
			role_profile_name = f"{department} - {level}"
			create_role_profile(role_profile_name, roles)

	frappe.db.commit()


def create_module_profile(department, allowed_modules):
	name = department
	if frappe.db.exists("Module Profile", name):
		return name

	blocked_modules = [m for m in MANAGED_MODULES if m not in allowed_modules]

	doc = frappe.new_doc("Module Profile")
	doc.module_profile = name
	for module in blocked_modules:
		if frappe.db.exists("Module Def", module):
			doc.append("block_modules", {"module": module})

	doc.insert(ignore_permissions=True)
	return name


def create_role_profile(name, roles):
	if frappe.db.exists("Role Profile", name):
		return

	doc = frappe.new_doc("Role Profile")
	doc.role_profile = name
	for role in roles:
		if frappe.db.exists("Role", role):
			doc.append("roles", {"role": role})

	if not doc.get("roles"):
		return

	doc.insert(ignore_permissions=True)
