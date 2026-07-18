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
