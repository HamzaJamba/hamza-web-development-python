import { useEffect, useState, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import TopBar from "../../components/TopBar";
import StatusBadge from "../../components/StatusBadge";
import { getOrder, cancelOrder, createReview } from "../../api/services";

const TRACK_STEPS = ["PENDING", "ACCEPTED", "PREPARING", "READY_FOR_PICKUP", "OUT_FOR_DELIVERY", "COMPLETED"];
const CANCELLABLE = ["PENDING", "ACCEPTED"];

export default function OrderDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const [cancelling, setCancelling] = useState(false);
  const [reviewOpen, setReviewOpen] = useState(false);
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");
  const [reviewDone, setReviewDone] = useState(false);

  const load = useCallback(() => {
    getOrder(id).then(setOrder);
  }, [id]);

  useEffect(load, [load]);
  useEffect(() => {
    if (!order || ["COMPLETED", "CANCELLED"].includes(order.status)) return;
    const interval = setInterval(load, 8000);
    return () => clearInterval(interval);
  }, [order, load]);

  if (!order) {
    return (
      <div className="page" style={{ display: "flex", justifyContent: "center", padding: 60 }}>
        <span className="spinner" />
      </div>
    );
  }

  const stepIndex = TRACK_STEPS.indexOf(order.status);
  const isCancelled = order.status === "CANCELLED";

  const handleCancel = async () => {
    setCancelling(true);
    try {
      await cancelOrder(id, "Changed my mind");
      load();
    } finally {
      setCancelling(false);
    }
  };

  const submitReview = async () => {
    await createReview({ order: id, rating, comment });
    setReviewDone(true);
    setReviewOpen(false);
  };

  return (
    <div className="page">
      <TopBar title={order.order_number} showBack onBack={() => navigate(-1)} />

      <div style={{ padding: "0 18px" }}>
        <div className="card" style={{ marginBottom: 16 }}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
            <span style={{ fontSize: 14, fontWeight: 600 }}>{order.restaurant_name}</span>
            <StatusBadge status={order.status} />
          </div>
        </div>

        {!isCancelled && (
          <div className="card" style={{ marginBottom: 16 }}>
            {TRACK_STEPS.map((step, i) => (
              <div key={step} style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: i < TRACK_STEPS.length - 1 ? 4 : 0 }}>
                <div style={{
                  width: 10, height: 10, borderRadius: "50%",
                  background: i <= stepIndex ? "var(--gold)" : "var(--surface-raised)",
                  flexShrink: 0,
                }} />
                <span style={{ fontSize: 12, color: i <= stepIndex ? "var(--text)" : "var(--text-muted)" }}>
                  {step.replaceAll("_", " ").toLowerCase()}
                </span>
              </div>
            ))}
          </div>
        )}

        <div className="card" style={{ marginBottom: 16 }}>
          {order.items.map((item) => (
            <div key={item.id} style={{ display: "flex", justifyContent: "space-between", fontSize: 13, marginBottom: 6 }}>
              <span>{item.quantity}x {item.food_name_snapshot}</span>
              <span>Rs {Number(item.line_total).toFixed(0)}</span>
            </div>
          ))}
          <div style={{ borderTop: "1px solid var(--border)", marginTop: 8, paddingTop: 8 }}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, color: "var(--text-muted)", marginBottom: 4 }}>
              <span>Subtotal</span><span>Rs {Number(order.subtotal).toFixed(0)}</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, color: "var(--text-muted)", marginBottom: 4 }}>
              <span>Delivery</span><span>Rs {Number(order.delivery_charges).toFixed(0)}</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, color: "var(--text-muted)", marginBottom: 4 }}>
              <span>Tax</span><span>Rs {Number(order.tax).toFixed(0)}</span>
            </div>
            {Number(order.discount_amount) > 0 && (
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, color: "var(--gold)", marginBottom: 4 }}>
                <span>Discount</span><span>-Rs {Number(order.discount_amount).toFixed(0)}</span>
              </div>
            )}
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 14, fontWeight: 600, marginTop: 6 }}>
              <span>Total</span><span>Rs {Number(order.grand_total).toFixed(0)}</span>
            </div>
          </div>
        </div>

        {CANCELLABLE.includes(order.status) && (
          <button className="btn btn-danger btn-block" disabled={cancelling} onClick={handleCancel}>
            {cancelling ? <span className="spinner" /> : "Cancel order"}
          </button>
        )}

        {order.status === "COMPLETED" && !reviewDone && (
          <>
            {!reviewOpen ? (
              <button className="btn btn-secondary btn-block" onClick={() => setReviewOpen(true)}>
                <i className="ti ti-star" style={{ fontSize: 14 }} /> Rate this order
              </button>
            ) : (
              <div className="card">
                <div style={{ display: "flex", gap: 6, marginBottom: 12, justifyContent: "center" }}>
                  {[1, 2, 3, 4, 5].map((n) => (
                    <button
                      key={n}
                      onClick={() => setRating(n)}
                      aria-label={`${n} stars`}
                      style={{ background: "none", border: "none", padding: 0 }}
                    >
                      <i className={`ti ${n <= rating ? "ti-star-filled" : "ti-star"}`} style={{ fontSize: 24, color: "var(--gold)" }} />
                    </button>
                  ))}
                </div>
                <textarea
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  placeholder="How was the food?"
                  rows={3}
                  style={{ width: "100%", background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 8, padding: 10, color: "var(--text)", marginBottom: 12, fontSize: 13 }}
                />
                <button className="btn btn-primary btn-block" onClick={submitReview}>Submit review</button>
              </div>
            )}
          </>
        )}

        {reviewDone && <p style={{ textAlign: "center", fontSize: 13, color: "var(--gold)" }}>Thanks for your review!</p>}
      </div>
    </div>
  );
}
