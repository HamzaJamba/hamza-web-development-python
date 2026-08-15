const STATUS_STYLES = {
  PENDING: "badge-muted",
  ACCEPTED: "badge-gold",
  PREPARING: "badge-gold",
  READY_FOR_PICKUP: "badge-gold",
  OUT_FOR_DELIVERY: "badge-gold",
  COMPLETED: "badge-success",
  CANCELLED: "badge-danger",
};

const STATUS_LABELS = {
  PENDING: "Pending",
  ACCEPTED: "Accepted",
  PREPARING: "Preparing",
  READY_FOR_PICKUP: "Ready for pickup",
  OUT_FOR_DELIVERY: "Out for delivery",
  COMPLETED: "Delivered",
  CANCELLED: "Cancelled",
};

export default function StatusBadge({ status }) {
  return <span className={`badge ${STATUS_STYLES[status] || "badge-muted"}`}>{STATUS_LABELS[status] || status}</span>;
}
