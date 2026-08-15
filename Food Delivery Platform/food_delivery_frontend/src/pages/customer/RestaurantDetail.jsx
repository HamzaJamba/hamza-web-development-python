import { useEffect, useState, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import TopBar from "../../components/TopBar";
import FoodItemCard from "../../components/FoodItemCard";
import { getRestaurant, listFoodItems, addCartItem, listWishlist, addWishlist, removeWishlist } from "../../api/services";
import { useAuth } from "../../context/AuthContext";

export default function RestaurantDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [restaurant, setRestaurant] = useState(null);
  const [foodItems, setFoodItems] = useState([]);
  const [wishlist, setWishlist] = useState([]);
  const [toast, setToast] = useState("");
  const [conflictItem, setConflictItem] = useState(null);

  const load = useCallback(() => {
    getRestaurant(id).then(setRestaurant);
    listFoodItems({ restaurant: id }).then((data) => setFoodItems(data.results || data));
    if (user?.role === "CUSTOMER") {
      listWishlist().then((data) => setWishlist(data.results || data));
    }
  }, [id, user]);

  useEffect(load, [load]);

  const showToast = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(""), 2000);
  };

  const handleAdd = async (item, replaceCart = false) => {
    try {
      await addCartItem({ food_item_id: item.id, quantity: 1, replace_cart: replaceCart });
      showToast(`${item.name} added to cart`);
      setConflictItem(null);
    } catch (e) {
      if (e.response?.data?.code === "DIFFERENT_RESTAURANT") {
        setConflictItem(item);
      } else {
        showToast("Could not add item.");
      }
    }
  };

  const handleWishlist = async (item) => {
    const existing = wishlist.find((w) => w.food_item === item.id);
    if (existing) {
      await removeWishlist(existing.id);
      setWishlist(wishlist.filter((w) => w.id !== existing.id));
    } else {
      const created = await addWishlist(item.id);
      setWishlist([...wishlist, created]);
    }
  };

  if (!restaurant) {
    return (
      <div className="page" style={{ display: "flex", justifyContent: "center", padding: 60 }}>
        <span className="spinner" />
      </div>
    );
  }

  return (
    <div className="page">
      <TopBar title={restaurant.name} showBack onBack={() => navigate(-1)} />

      <div style={{ padding: "0 18px 18px" }}>
        <div className="card" style={{ marginBottom: 18 }}>
          <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 4 }}>{restaurant.description}</div>
          <div style={{ display: "flex", gap: 12, fontSize: 12, color: "var(--text-muted)" }}>
            <span><i className="ti ti-star" style={{ color: "var(--gold)", fontSize: 12 }} /> {Number(restaurant.avg_rating).toFixed(1)}</span>
            <span>{restaurant.address_line}, {restaurant.city}</span>
          </div>
        </div>

        {conflictItem && (
          <div className="card" style={{ marginBottom: 14, border: "1px solid var(--maroon)" }}>
            <p style={{ fontSize: 13, marginBottom: 10 }}>
              Your cart has items from another restaurant. Clear it and add {conflictItem.name}?
            </p>
            <div style={{ display: "flex", gap: 8 }}>
              <button className="btn btn-danger" style={{ flex: 1 }} onClick={() => handleAdd(conflictItem, true)}>
                Clear cart & add
              </button>
              <button className="btn btn-secondary" style={{ flex: 1 }} onClick={() => setConflictItem(null)}>
                Cancel
              </button>
            </div>
          </div>
        )}

        {foodItems.map((item) => (
          <FoodItemCard
            key={item.id}
            item={item}
            onAdd={handleAdd}
            onWishlist={user?.role === "CUSTOMER" ? handleWishlist : undefined}
            isWishlisted={wishlist.some((w) => w.food_item === item.id)}
          />
        ))}
      </div>

      {toast && <div className="toast">{toast}</div>}

      <div style={{ position: "fixed", bottom: 20, left: "50%", transform: "translateX(-50%)", width: "100%", maxWidth: 480, padding: "0 18px" }}>
        <button className="btn btn-primary btn-block" onClick={() => navigate("/cart")}>
          <i className="ti ti-shopping-bag" style={{ fontSize: 16 }} /> View cart
        </button>
      </div>
    </div>
  );
}
