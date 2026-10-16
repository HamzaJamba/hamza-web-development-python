import { pretty } from "./format";

export const opts = (vals: string[]) => vals.map((v) => ({ value: v, label: pretty(v) }));
export const ROLES = ["ADMIN", "PLANT_MANAGER", "ENGINEER", "TECHNICIAN", "SAFETY_OFFICER", "STORE_KEEPER", "HR", "VIEWER"];
export const PLANT_TYPES = ["PLANT", "REFINERY", "GAS_STATION", "TERMINAL"];
export const PLANT_STATUS = ["OPERATIONAL", "MAINTENANCE", "SHUTDOWN"];
export const EQUIP_CATEGORIES = ["PUMP", "COMPRESSOR", "VALVE", "GENERATOR", "TURBINE", "SENSOR"];
export const EQUIP_STATUS = ["OPERATIONAL", "MAINTENANCE", "FAULTY", "OFFLINE", "DECOMMISSIONED"];
export const PRIORITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];
export const WO_TYPES = ["PREVENTIVE", "CORRECTIVE", "EMERGENCY"];
export const WO_STATUS = ["OPEN", "ASSIGNED", "IN_PROGRESS", "ON_HOLD", "COMPLETED", "CANCELLED"];
export const INCIDENT_TYPES = ["GAS_LEAK", "FIRE", "EXPLOSION", "EQUIPMENT_FAILURE", "NEAR_MISS", "SAFETY_VIOLATION"];
export const SEVERITIES = ["MINOR", "MODERATE", "MAJOR", "CATASTROPHIC"];
export const INCIDENT_STATUS = ["REPORTED", "INVESTIGATING", "RESOLVED", "CLOSED"];
export const ITEM_CATEGORIES = ["SPARE_PART", "CHEMICAL", "LUBRICANT", "SAFETY"];
export const METRICS = ["TEMPERATURE", "PRESSURE", "VOLTAGE", "VIBRATION", "OIL_LEVEL"];

export const equipmentOption = { endpoint: "/equipment/", label: (r: Record<string, any>) => `${r.name} (${r.serial_number})` }; // eslint-disable-line @typescript-eslint/no-explicit-any
export const plantOption = { endpoint: "/plants/", label: (r: Record<string, any>) => r.name }; // eslint-disable-line @typescript-eslint/no-explicit-any
export const userOption = (roles: string) => ({ endpoint: "/auth/users/directory/", params: { role: roles }, label: (r: Record<string, any>) => `${r.full_name} (${r.role.toLowerCase().replace("_", " ")})` }); // eslint-disable-line @typescript-eslint/no-explicit-any
