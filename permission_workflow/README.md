# Permission Workflow

A Frappe app that adds an approval workflow around granting access, instead of
editing permissions directly. Requesters ask for a **Role Profile** and/or
**Module Profile** to be assigned to a user; an approver reviews and
approves or rejects the request; the access is only applied to the `User`
record once it is approved.

This is a companion app to ERPNext, not a modification of ERPNext itself.
It is included in this branch/repo for review, but should be installed on a
bench as its own app (see below) rather than merged into the `erpnext` app.

## What it adds

- **Permission Request** doctype (submittable): pick a `Request Type`
  (`New Employee` or `Modify Existing Permission`), a `User`, a `Role
  Profile` and/or `Module Profile`, and a business justification.
- A **Workflow** ("Permission Request Approval") with four states:
  - `Draft` — editable by the requester.
  - `Pending Approval` — submitted, awaiting an approver. Locked from
    further edits by the requester.
  - `Approved` — the approver signed off. This is the only state that
    triggers writing `role_profile_name` / `module_profile` onto the
    target `User`.
  - `Rejected` — the approver declined; a comment explaining why is
    required. The requester can amend the rejected request into a new
    draft and resubmit.
- Two new roles: `Permission Requester` (can create/submit requests for
  themselves) and `Permission Approver` (can approve/reject requests in
  `Pending Approval`).
- The actual "apply to the system" step reuses Frappe/ERPNext's own `User`
  doctype logic for `Role Profile` and `Module Profile` (the same fields
  exposed on the standard User form) — this app does not reimplement
  permission plumbing, it only gates *when* that assignment happens behind
  an approval step.
- A starter set of **Role Profiles** and **Module Profiles** for a
  construction company, shipped as fixtures so there's something real to
  pick from a `Permission Request` on day one instead of an empty dropdown.
  See "Pre-built profiles" below.

## Pre-built profiles

`permission_workflow/fixtures/` ships one **Module Profile** per department
(it hides the ERPNext workspaces that department doesn't need) and one
**Role Profile** per department/level combination (it bundles the existing
ERPNext roles that match that seniority), plus the `Permission Requester`
and `Permission Approver` roles themselves. These are plain Frappe
[fixtures](https://frappeframework.com/docs/user/en/basics/fixtures) —
`role.json`, `role_profile.json`, `module_profile.json` — synced
automatically by `bench migrate` / `bench install-app`, the same mechanism
ERPNext itself uses to ship reference data. Nothing here is invented —
every role name is one that already ships with ERPNext and already carries
real DocType permissions; these profiles just group them the way a
construction company is usually organized:

| Department | Module Profile scope | Levels seeded |
|---|---|---|
| Executive | everything | Director |
| Project & Site Engineering | Projects, Stock, Quality Management, Maintenance, Buying, Setup | Manager, Engineer |
| Procurement | Buying, Stock, Setup | Manager, Officer |
| Warehouse & Equipment | Stock, Assets, Maintenance, Setup | Manager, Store Keeper |
| Finance & Accounts | Accounts, Buying, Selling, Setup | Manager, Accountant |
| HR & Admin | Setup, Support | Manager, Officer |
| Business Development | CRM, Selling, Setup | Manager, Executive |
| Quality & Safety | Quality Management, Projects, Maintenance, Setup | Manager, Inspector |
| Manufacturing & Fabrication | Manufacturing, Stock, Subcontracting, Setup | Manager, Operator |

Role Profiles are named `<Department> - <Level>`, e.g. `Procurement -
Officer` or `Project & Site Engineering - Engineer`. To rename a department,
add a level, or change which roles a level gets, edit the relevant fixture
JSON directly and run `bench migrate` — fixture sync is an upsert by name,
so it never overwrites a site's own edits to a profile that already
diverged from these files, it only creates what's still missing. The
`fixtures` list in `hooks.py` is filtered to exactly these record names, so
running `bench export-fixtures` later (after editing profiles on a live
site) only re-exports this app's own records, not unrelated ones on the
same site.

Two things this does **not** try to do: it doesn't invent new Roles or
DocType permissions for construction-specific titles (a made-up "Site
Engineer" role with no `Custom DocPerm` behind it would grant nothing), so
every profile is built from ERPNext's real roles; and `HR Manager`/`HR
User` only unlock full HR doctypes if the separate `hrms` app is also
installed — without it they still grant whatever Project/Task/Timesheet/
Issue permissions ERPNext ties to those role names.

## What it deliberately does not do

- It does not replace the granular DocType-level Permission Manager
  (`Custom DocPerm` editing). It governs access at the Role Profile /
  Module Profile level, which is the level ERPNext already recommends for
  assigning access to end users. If you also want approval-gated,
  field-by-field DocType permission edits (like the `role_permission_manager`
  app this was scoped from), that would be a second doctype/workflow
  layered on top — ask if you want that added.

## Install on a bench

```bash
bench get-app permission_workflow /path/to/permission_workflow
bench --site <site-name> install-app permission_workflow
```

Installing syncs the fixtures (the two roles, and the pre-built Role/Module
Profiles described below) and then runs `after_install`, which creates the
four `Workflow State` records, the `Workflow Action Master` records, and the
`Permission Request Approval` workflow itself. Re-running install (or
`bench migrate`, via the bundled patch) is safe — fixture sync is an
upsert, and every step in `after_install` checks for an existing record
first.

## Using it

1. Assign the `Permission Requester` role to anyone who should be able to
   request access changes, and `Permission Approver` to whoever reviews
   them.
2. A requester creates a **Permission Request**, sets the `Request Type`
   (onboarding a `New Employee` vs. `Modify Existing Permission` for
   someone who already has access), picks the target `User`, a
   `Role Profile` and/or `Module Profile`, fills in the justification,
   and clicks **Submit for Approval**.
3. An approver opens the request (list filtered to `Pending Approval`),
   adds `Approver Comments`, and clicks **Approve** or **Reject**.
4. On **Approve**, the app writes the chosen Role Profile/Module Profile
   onto the target `User` and saves it (`applied` flips to 1, `applied on`
   is stamped). On **Reject**, nothing is applied and the requester can
   amend and resubmit.

## Testing

This app was written and reviewed but not installed against a live Frappe
site in this session (no bench/site was available in this environment).
Before relying on it, install it on a dev bench and walk through the
request → submit → approve/reject flow end-to-end, and run:

```bash
bench --site <site-name> run-tests --app permission_workflow
```
