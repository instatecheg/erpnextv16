app_name = "permission_workflow"
app_title = "Permission Workflow"
app_publisher = "Your Organization"
app_description = "Approval workflow for assigning Role Profiles and Module Profiles to users."
app_email = "support@example.com"
app_license = "mit"
required_apps = ["frappe"]

# Installation
# ------------

after_install = "permission_workflow.setup.install.after_install"

# Fixtures
# --------
# Synced automatically on `bench migrate` / install. Filtered to just the
# records this app owns, so a future `bench export-fixtures` on a site with
# other custom Role Profiles/Module Profiles won't sweep those in too.

fixtures = [
	{
		"dt": "Role",
		"filters": [["name", "in", ["Permission Requester", "Permission Approver"]]],
	},
	{
		"dt": "Role Profile",
		"filters": [["name", "in", [
			"Executive - Director",
			"Project & Site Engineering - Manager", "Project & Site Engineering - Engineer",
			"Procurement - Manager", "Procurement - Officer",
			"Warehouse & Equipment - Manager", "Warehouse & Equipment - Store Keeper",
			"Finance & Accounts - Manager", "Finance & Accounts - Accountant",
			"HR & Admin - Manager", "HR & Admin - Officer",
			"Business Development - Manager", "Business Development - Executive",
			"Quality & Safety - Manager", "Quality & Safety - Inspector",
			"Manufacturing & Fabrication - Manager", "Manufacturing & Fabrication - Operator",
		]]],
	},
	{
		"dt": "Module Profile",
		"filters": [["name", "in", [
			"Executive", "Project & Site Engineering", "Procurement",
			"Warehouse & Equipment", "Finance & Accounts", "HR & Admin",
			"Business Development", "Quality & Safety", "Manufacturing & Fabrication",
		]]],
	},
]
