import { useState } from "react";

import ResourcePage from "../components/ResourcePage";
import { Badge, PageHeader, Tabs } from "../components/ui";
import { useAuth } from "../lib/auth";
import { date, money } from "../lib/format";
import { opts, plantOption } from "../lib/options";

type Tab = "employees" | "departments" | "positions" | "shifts" | "grades" | "trainings" | "certs";
const ref = (endpoint: string, label: (r: Record<string, any>) => string) => ({ endpoint, label }); // eslint-disable-line @typescript-eslint/no-explicit-any
const dept = ref("/employees/departments/", (r) => r.name);
const position = ref("/employees/positions/", (r) => `${r.title} (${r.department_name})`);
const shift = ref("/employees/shifts/", (r) => r.name);
const grade = ref("/employees/salary-grades/", (r) => `${r.code} - ${r.name}`);
const employee = ref("/employees/", (r) => `${r.employee_id} ${r.full_name}`);

export default function Employees() {
  const { can } = useAuth();
  const [tab, setTab] = useState<Tab>("employees");
  const hr = can("HR", "PLANT_MANAGER");
  const tabs: { id: Tab; label: string }[] = [{ id: "employees", label: "Employees" }, { id: "departments", label: "Departments" }, { id: "positions", label: "Positions" }, { id: "shifts", label: "Shifts" },
    ...(can("HR", "PLANT_MANAGER") ? [{ id: "grades" as Tab, label: "Salary grades" }] : []), { id: "trainings", label: "Training" }, { id: "certs", label: "Certifications" }];
  return (
    <div>
      <PageHeader title="People" subtitle="Employee records, structure, shifts, training and certifications." />
      <Tabs value={tab} onChange={setTab} tabs={tabs} />
      {tab === "employees" && <ResourcePage embedded noun="employee" endpoint="/employees/" canWrite={hr} canDelete={hr}
        filters={[{ name: "status", label: "Status", options: opts(["ACTIVE", "ON_LEAVE", "TERMINATED"]) }]}
        columns={[{ key: "employee_id", label: "ID" }, { key: "full_name", label: "Name" }, { key: "department_name", label: "Department" }, { key: "position_title", label: "Position" }, { key: "shift_name", label: "Shift" }, { key: "plant_name", label: "Plant" },
          { key: "status", label: "Status", render: (r) => <Badge value={r.status} /> }]}
        fields={[{ name: "employee_id", label: "Employee ID", required: true }, { name: "first_name", label: "First name", required: true }, { name: "last_name", label: "Last name", required: true }, { name: "email", label: "Email", type: "email" },
          { name: "phone", label: "Phone" }, { name: "hire_date", label: "Hire date", type: "date", required: true }, { name: "department", label: "Department", type: "select", optionsFrom: dept, required: true },
          { name: "position", label: "Position", type: "select", optionsFrom: position, required: true, hint: "Must belong to the selected department." }, { name: "shift", label: "Shift", type: "select", optionsFrom: shift },
          { name: "salary_grade", label: "Salary grade", type: "select", optionsFrom: grade }, { name: "plant", label: "Plant", type: "select", optionsFrom: plantOption },
          { name: "status", label: "Status", type: "select", options: opts(["ACTIVE", "ON_LEAVE", "TERMINATED"]), required: true }]} defaults={{ status: "ACTIVE" }} />}
      {tab === "departments" && <ResourcePage embedded noun="department" endpoint="/employees/departments/" canWrite={hr} canDelete={hr} columns={[{ key: "code", label: "Code" }, { key: "name", label: "Name" }, { key: "employee_count", label: "Employees" }]}
        fields={[{ name: "code", label: "Code", required: true }, { name: "name", label: "Name", required: true }, { name: "description", label: "Description", type: "textarea" }]} />}
      {tab === "positions" && <ResourcePage embedded noun="position" endpoint="/employees/positions/" canWrite={hr} canDelete={hr} columns={[{ key: "title", label: "Title" }, { key: "department_name", label: "Department" }]}
        fields={[{ name: "title", label: "Title", required: true }, { name: "department", label: "Department", type: "select", optionsFrom: dept, required: true }]} />}
      {tab === "shifts" && <ResourcePage embedded noun="shift" endpoint="/employees/shifts/" canWrite={hr} canDelete={hr} searchable={false} columns={[{ key: "name", label: "Shift" }, { key: "start_time", label: "Starts" }, { key: "end_time", label: "Ends" }]}
        fields={[{ name: "name", label: "Name", required: true }, { name: "start_time", label: "Start", type: "time", required: true }, { name: "end_time", label: "End", type: "time", required: true }]} />}
      {tab === "grades" && <ResourcePage embedded noun="salary grade" endpoint="/employees/salary-grades/" canWrite={can("HR")} canDelete={can("HR")} searchable={false}
        columns={[{ key: "code", label: "Grade" }, { key: "name", label: "Name" }, { key: "min_salary", label: "Minimum", render: (r) => money(r.min_salary) }, { key: "max_salary", label: "Maximum", render: (r) => money(r.max_salary) }]}
        fields={[{ name: "code", label: "Code", required: true }, { name: "name", label: "Name", required: true }, { name: "min_salary", label: "Minimum salary", type: "number", step: "0.01", required: true }, { name: "max_salary", label: "Maximum salary", type: "number", step: "0.01", required: true }]} />}
      {tab === "trainings" && <ResourcePage embedded noun="training record" endpoint="/employees/trainings/" canWrite={can("HR", "PLANT_MANAGER", "SAFETY_OFFICER")} canDelete={hr}
        columns={[{ key: "employee_name", label: "Employee" }, { key: "title", label: "Course" }, { key: "provider", label: "Provider" }, { key: "completed_on", label: "Completed", render: (r) => date(r.completed_on) }, { key: "hours", label: "Hours" }, { key: "score", label: "Score" }]}
        fields={[{ name: "employee", label: "Employee", type: "select", optionsFrom: employee, required: true }, { name: "title", label: "Course", required: true }, { name: "provider", label: "Provider" },
          { name: "completed_on", label: "Completed on", type: "date", required: true }, { name: "hours", label: "Hours", type: "number", step: "0.5" }, { name: "score", label: "Score (%)", type: "number" }]} />}
      {tab === "certs" && <ResourcePage embedded noun="certification" endpoint="/employees/certifications/" canWrite={can("HR", "PLANT_MANAGER", "SAFETY_OFFICER")} canDelete={hr}
        columns={[{ key: "employee_name", label: "Employee" }, { key: "name", label: "Certification" }, { key: "issuer", label: "Issuer" }, { key: "issued_on", label: "Issued", render: (r) => date(r.issued_on) },
          { key: "expires_on", label: "Expires", render: (r) => r.expires_on ? <span className={r.is_expired ? "font-medium text-crit" : ""}>{date(r.expires_on)}{r.is_expired && " (expired)"}</span> : "No expiry" }]}
        fields={[{ name: "employee", label: "Employee", type: "select", optionsFrom: employee, required: true }, { name: "name", label: "Certification", required: true }, { name: "issuer", label: "Issuer" }, { name: "certificate_no", label: "Certificate no." },
          { name: "issued_on", label: "Issued on", type: "date", required: true }, { name: "expires_on", label: "Expires on", type: "date" }]} />}
    </div>
  );
}
