import { ReactNode } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import Layout from "./components/Layout";
import { Spinner } from "./components/ui";
import { Role, useAuth } from "./lib/auth";
import Audit from "./pages/Audit";
import Dashboard from "./pages/Dashboard";
import Employees from "./pages/Employees";
import EquipmentDetail from "./pages/EquipmentDetail";
import EquipmentList from "./pages/EquipmentList";
import IncidentDetail from "./pages/IncidentDetail";
import Incidents from "./pages/Incidents";
import Inventory from "./pages/Inventory";
import Login from "./pages/Login";
import Maintenance from "./pages/Maintenance";
import Monitoring from "./pages/Monitoring";
import Notifications from "./pages/Notifications";
import Plants from "./pages/Plants";
import Reports from "./pages/Reports";
import UsersPage from "./pages/Users";
import WorkOrderDetail from "./pages/WorkOrderDetail";
import WorkOrders from "./pages/WorkOrders";

function Guard({ roles, children }: { roles?: Role[]; children: ReactNode }) {
  const { user, loading, can } = useAuth();
  if (loading) return <Spinner label="Signing in" />;
  if (!user) return <Navigate to="/login" replace />;
  if (roles && !can(...roles)) return <div className="py-20 text-center"><h1 className="text-2xl font-semibold">Access restricted</h1><p className="mt-1 text-slate-600">Your role does not include this area.</p></div>;
  return <>{children}</>;
}

export default function App() {
  const { user } = useAuth();
  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" replace /> : <Login />} />
      <Route element={<Guard><Layout /></Guard>}>
        <Route index element={<Dashboard />} />
        <Route path="monitoring" element={<Monitoring />} />
        <Route path="plants" element={<Plants />} />
        <Route path="equipment" element={<EquipmentList />} />
        <Route path="equipment/:id" element={<EquipmentDetail />} />
        <Route path="work-orders" element={<WorkOrders />} />
        <Route path="work-orders/:id" element={<WorkOrderDetail />} />
        <Route path="maintenance" element={<Maintenance />} />
        <Route path="incidents" element={<Incidents />} />
        <Route path="incidents/:id" element={<IncidentDetail />} />
        <Route path="inventory" element={<Inventory />} />
        <Route path="employees" element={<Guard roles={["PLANT_MANAGER", "HR", "SAFETY_OFFICER", "ENGINEER"]}><Employees /></Guard>} />
        <Route path="reports" element={<Guard roles={["PLANT_MANAGER", "ENGINEER", "SAFETY_OFFICER", "HR"]}><Reports /></Guard>} />
        <Route path="notifications" element={<Notifications />} />
        <Route path="users" element={<Guard roles={["ADMIN"]}><UsersPage /></Guard>} />
        <Route path="audit" element={<Guard roles={["ADMIN"]}><Audit /></Guard>} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
