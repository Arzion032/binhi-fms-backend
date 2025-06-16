import React, { useState, useEffect, useMemo, useCallback } from "react";
import { Search, SlidersHorizontal, RefreshCw } from "lucide-react";
import OrderManagementModal from "./OrderManagementModal";
import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000";

const BADGE_STYLES = {
  pending: { color: "#F59E42", background: "#FFF6E9", border: "#F59E42" },
  processing: { color: "#2563EB", background: "#E0E7FF", border: "#2563EB" },
  shipped: { color: "#22C55E", background: "#DCFAE6", border: "#22C55E" },
  delivered: { color: "#0EA5E9", background: "#E0F2FE", border: "#0EA5E9" },
  cancelled: { color: "#EF4444", background: "#FEE2E2", border: "#EF4444" },
  paid: { color: "#22C55E", background: "#DCFAE6", border: "#22C55E" },
  refunded: { color: "#EF4444", background: "#FEE2E2", border: "#EF4444" },
  gcash: {
    color: "#fff",
    background: "#40a3fe",
    border: "#106cbb",
    custom: true,
  },
  "cash on delivery": {
    color: "#9a6600",
    background: "#fff7cc",
    border: "#ffb300",
    custom: true,
  },
};

export default function OrderManagement() {
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState("");
  const [orderRows, setOrderRows] = useState([]);
  const [selectedOrderRows, setSelectedOrderRows] = useState([]);
  const [orderPage, setOrderPage] = useState(1);
  const [totalOrders, setTotalOrders] = useState(0);
  const [loading, setLoading] = useState(true);
  const [orderManagementModalOpen, setOrderManagementModalOpen] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [userMap, setUserMap] = useState({});
  const [statusCategories, setStatusCategories] = useState([
    { name: "Pending", value: "pending", count: 0, border: "#F59E42" },
    { name: "Processing", value: "processing", count: 0, border: "#2563EB" },
    { name: "Shipped", value: "shipped", count: 0, border: "#22C55E" },
    { name: "Delivered", value: "delivered", count: 0, border: "#0EA5E9" },
    { name: "Cancelled", value: "cancelled", count: 0, border: "#EF4444" }
  ]);

  const ordersPerPage = 7;

  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearchQuery(searchQuery), 300);
    return () => clearTimeout(t);
  }, [searchQuery]);

  const fetchUsers = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/users/members/`);
      const users = response.data;
      const userMap = {};
      users.forEach(user => {
        userMap[user.id] = user.username;
      });
      setUserMap(userMap);
    } catch (error) {
      console.error("Error fetching users:", error);
    }
  }, []);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const fetchOrders = useCallback(async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/orders/order-history/`, {
        params: {
          page: orderPage,
          per_page: ordersPerPage,
          search: debouncedSearchQuery
        }
      });

      const mappedOrders = response.data.map(order => ({
        ...order,
        date: order.orderDate ? order.orderDate.split("T")[0] : "-",
        time: order.orderDate
          ? (order.orderDate.split("T")[1] || "").split("+")[0].slice(0, 5)
          : "",
        customer: {
          name: order.deliveryAddress?.name || "-",
          email: order.deliveryAddress?.address || "-",
          address: order.deliveryAddress?.address || "-",
          avatar: "/avatar-user.png",
          contact: order.deliveryAddress?.phone || "-",
        },
        product: {
          name: order.items?.[0]?.name || "-",
          image: order.items?.[0]?.image?.image || "/sampleproduct.png",
          variation: order.items?.[0]?.variation || "-",
        },
        transaction: order.payment_method || "Pending",
        payment_status: order.payment_status || "Pending", // Show as is!
        buyer: {
          username: userMap[order.buyer_id] || "-"
        }
      }));

      setOrderRows(mappedOrders);
      setTotalOrders(mappedOrders.length);

      const newStatusCategories = statusCategories.map((cat) => ({
        ...cat,
        count: mappedOrders.filter((o) =>
          o.status?.toLowerCase() === cat.value
        ).length,
      }));
      setStatusCategories(newStatusCategories);
    } catch (err) {
      setOrderRows([]);
      setTotalOrders(0);
    }
    setLoading(false);
  }, [orderPage, ordersPerPage, debouncedSearchQuery, userMap]);

  useEffect(() => {
    fetchOrders();
  }, [orderPage, debouncedSearchQuery]);

  const orderTotalPages = Math.ceil(totalOrders / ordersPerPage);

  const renderLoading = () => (
    <div className="flex justify-center items-center h-64">
      <img
        src="/BINHI-LOADING-unscreen.gif"
        alt="Loading..."
        style={{ width: 120, height: 120, objectFit: "contain" }}
      />
    </div>
  );

  const handleCloseModalWithoutRefresh = () => {
    setOrderManagementModalOpen(false);
    setSelectedOrder(null);
  };

  return (
    <div className="px-6 pb-6">
      {/* Top bar */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between py-4 mb-2">
        <div className="flex items-center gap-2 mb-2 md:mb-0">
          <RefreshCw
            size={20}
            style={{ color: "#16A34A" }}
            className="cursor-pointer hover:opacity-80"
            onClick={fetchOrders}
          />
          <span style={{ fontWeight: 500 }}>{`All Orders ${totalOrders}`}</span>
          {selectedOrderRows.length > 0 && (
            <>
              <button
                onClick={() => setSelectedOrderRows([])}
                className="flex items-center gap-1 border border-gray-200 rounded-2xl px-4 py-2 hover:bg-gray-100 ml-1"
              >
                ✕ Clear
              </button>
            </>
          )}
        </div>
        {/* Search */}
        <div className="flex items-center gap-4">
          <div className="relative" style={{ width: "240px" }}>
            <Search
              size={18}
              style={{
                position: "absolute",
                left: "0.75rem",
                top: "50%",
                transform: "translateY(-50%)",
                color: "#6B7280",
              }}
            />
            <input
              type="text"
              placeholder="Search Order"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              style={{
                width: "100%",
                padding: "0.5rem 2.5rem 0.5rem 2.5rem",
                border: "1px solid #D1D5DB",
                borderRadius: "9999px",
                outline: "none",
              }}
            />
            <SlidersHorizontal
              size={18}
              style={{
                position: "absolute",
                right: "0.75rem",
                top: "50%",
                transform: "translateY(-50%)",
                color: "#6B7280",
              }}
            />
          </div>
        </div>
      </div>

      {/* ORDER STATUS CARDS */}
      <div className="pb-4">
        <div className="flex gap-4 overflow-x-auto">
          {statusCategories.map((cat) => (
            <div
              key={cat.value}
              style={{
                position: "relative",
                border: `1.8px solid ${cat.border}`,
                borderRadius: "1.6rem",
                minWidth: "150px",
                height: "80px",
                padding: "0 1.5rem",
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                backgroundColor: "#FFFFFF",
                flex: "1",
                overflow: "hidden",
                boxShadow: "0 1px 5px 0 rgba(0,0,0,0.07)",
              }}
            >
              {loading && (
                <div
                  style={{
                    position: "absolute",
                    top: "0",
                    left: "0",
                    right: "0",
                    bottom: "0",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    backgroundColor: "rgba(255, 255, 255, 0.8)",
                    borderRadius: "1.6rem",
                  }}
                >
                  <img
                    src="/categoryloading-unscreen.gif"
                    alt="Loading"
                    style={{ 
                      width: "80px", 
                      height: "80px",
                      objectFit: "contain"
                    }}
                  />
                </div>
              )}
              <div
                style={{
                  position: "absolute",
                  left: "0",
                  top: "0",
                  bottom: "0",
                  width: "20px",
                  backgroundColor: cat.border,
                  borderRadius: "1.6rem 0 0 1.6rem",
                }}
              />
              <span
                style={{
                  fontSize: "0.875rem",
                  color: "#9CA3AF",
                  fontWeight: 500,
                  marginLeft: "8px",
                }}
              >
                {cat.name}
              </span>
              <span
                style={{
                  fontSize: "1.875rem",
                  fontWeight: 900,
                  color: "#000000",
                  marginLeft: "8px",
                }}
              >
                {cat.count}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Table */}
      <div style={{ borderRadius: "1rem", overflow: "hidden", minHeight: 420 }}>
        <h2 className="px-4 pt-4 text-xl font-bold text-gray-900">Orders List</h2>
        {loading ? renderLoading() : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead style={{ backgroundColor: "#F7F7FB" }}>
              <tr style={{ color: "#4B5563", fontSize: "0.875rem", fontWeight: 600 }}>
                <th style={{ padding: "0.75rem" }}>
                  <input
                    type="checkbox"
                    className="checkbox checkbox-sm rounded"
                    checked={
                      selectedOrderRows.length === orderRows.length &&
                      orderRows.length > 0
                    }
                    onChange={e =>
                      setSelectedOrderRows(
                        e.target.checked
                          ? orderRows.map((_, idx) => idx)
                          : []
                      )
                    }
                  />
                </th>
                <th style={{ padding: "0.75rem", textAlign: "left" }}>Order ID</th>
                <th style={{ padding: "0.75rem", textAlign: "left" }}>Buyer</th>
                <th style={{ padding: "0.75rem", textAlign: "left" }}>address</th>
                <th style={{ padding: "0.75rem", textAlign: "left" }}>Product</th>
                <th style={{ padding: "0.75rem", textAlign: "left" }}>Date Ordered</th>
                <th style={{ padding: "0.75rem", textAlign: "left" }}>Order Status</th>
                <th style={{ padding: "0.75rem", textAlign: "left" }}>Payment Method</th>
                <th style={{ padding: "0.75rem", textAlign: "left" }}>Payment Status</th>
                <th style={{ padding: "0.75rem", textAlign: "left" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {orderRows.map((o, idx) => {
                const isSelected = selectedOrderRows.includes(idx);
                const badge = BADGE_STYLES[o.status?.toLowerCase()] || {
                  color: "#757575",
                  background: "#E5E7EB",
                  border: "#D4D4D8"
                };
                const txnType = o.transaction?.toLowerCase?.() || "";
                const transactionBadge = BADGE_STYLES[txnType] || {
                  color: "#757575",
                  background: "#E5E7EB",
                  border: "#D4D4D8"
                };
                return (
                  <tr
                    key={o.id}
                    style={{
                      backgroundColor: isSelected ? "#F0FDFA" : "transparent",
                      height: "60px",
                    }}
                  >
                    <td style={{ padding: "0.75rem" }}>
                      <input
                        type="checkbox"
                        className="checkbox checkbox-sm rounded"
                        checked={isSelected}
                        onChange={e => {
                          if (e.target.checked) {
                            setSelectedOrderRows([...selectedOrderRows, idx]);
                          } else {
                            setSelectedOrderRows(selectedOrderRows.filter(i => i !== idx));
                          }
                        }}
                      />
                    </td>
                    <td style={{ padding: "0.75rem" }}>
                      <span className="font-medium">{o.orderId || o.id}</span>
                    </td>
                    <td style={{ padding: "0.75rem" }}>
                      <span className="font-medium">{o.buyer?.username || '-'}</span>
                    </td>
                    <td style={{ padding: "0.75rem" }}>
                      <div style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "0.75rem"
                      }}>
                        <img
                          src={o.customer.avatar}
                          alt={o.customer.name}
                          style={{
                            width: 38,
                            height: 38,
                            borderRadius: "50%",
                            objectFit: "cover"
                          }}
                        />
                        <div>
                          <div style={{ fontWeight: 600, color: "#111827" }}>
                            {o.customer.name}
                          </div>
                          <div style={{ fontSize: "0.87rem", color: "#6B7280" }}>
                            {o.customer.email}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td style={{ padding: "0.75rem" }}>
                      <div>
                        <div style={{ fontWeight: 600, color: "#111827" }}>
                          {o.product.name}
                        </div>
                        <div style={{
                          fontSize: "0.87rem",
                          color: "#9CA3AF",
                          marginTop: "1px"
                        }}>
                          Variation: {o.product.variation}
                        </div>
                      </div>
                    </td>
                    <td style={{ padding: "0.75rem" }}>
                      <span style={{ fontWeight: 500 }}>{o.date}</span>
                      <div className="text-gray-400 text-[0.93rem]">{o.time}</div>
                    </td>
                    <td style={{ padding: "0.75rem" }}>
                      <span
                        style={{
                          display: "inline-block",
                          padding: "0.25rem 0.75rem",
                          fontSize: "0.75rem",
                          fontWeight: 500,
                          borderRadius: "9999px",
                          color: badge.color,
                          background: badge.background,
                          border: `1.5px solid ${badge.color}`,
                        }}
                      >
                        {o.status}
                      </span>
                    </td>
                    <td style={{ padding: "0.75rem" }}>
                      <span
                        style={{
                          display: "inline-block",
                          padding: "0.25rem 0.75rem",
                          fontSize: "0.75rem",
                          fontWeight: 500,
                          borderRadius: "9999px",
                          color: transactionBadge.color,
                          background: transactionBadge.background,
                          border: `1.5px solid ${transactionBadge.border}`,
                          letterSpacing: "0.02em",
                          ...(transactionBadge.custom && {
                            boxShadow: "0 1px 4px 0 rgba(80,167,255,0.10)"
                          })
                        }}
                      >
                        {o.transaction}
                      </span>
                    </td>
                    <td style={{ padding: "0.75rem" }}>
                      <span
                        style={{
                          display: "inline-block",
                          padding: "0.25rem 0.75rem",
                          fontSize: "0.75rem",
                          fontWeight: 500,
                          borderRadius: "9999px",
                          color: BADGE_STYLES[o.payment_status?.toLowerCase()]?.color || "#757575",
                          background: BADGE_STYLES[o.payment_status?.toLowerCase()]?.background || "#E5E7EB",
                          border: `1.5px solid ${BADGE_STYLES[o.payment_status?.toLowerCase()]?.border || "#D4D4D8"}`,
                        }}
                      >
                        {o.payment_status || "Pending"}
                      </span>
                    </td>
                    <td style={{ padding: "0.75rem" }}>
                      <div
                        className="group flex items-center gap-2 cursor-pointer"
                        onClick={() => {
                          setSelectedOrder(o);
                          setOrderManagementModalOpen(true);
                        }}
                      >
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="#4CAE4F"
                          strokeWidth={2}
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          className="w-5 h-5"
                        >
                          <circle cx={11} cy={11} r={8} />
                          <line x1={21} y1={21} x2={16.65} y2={16.65} />
                        </svg>
                        <span
                          style={{ color: "#4CAE4F", marginLeft: 7, whiteSpace: "nowrap" }}
                          className="text-[0.98rem] font-semibold"
                        >
                          View Order
                        </span>
                      </div>
                    </td>
                  </tr>
                );
              })}
              {orderRows.length === 0 && !loading && (
                <tr>
                  <td colSpan={10} style={{ textAlign: "center", padding: "2rem", color: "#888" }}>
                    No orders found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}

        {/* Pagination */}
        <div className="flex justify-center my-6">
          <div className="flex items-center gap-1">
            <button
              onClick={() => setOrderPage(p => Math.max(1, p - 1))}
              className="btn btn-sm"
              disabled={orderPage === 1}
            >«</button>
            {[...Array(orderTotalPages)].map((_, i) => {
              const page = i + 1;
              return (
                <button
                  key={page}
                  onClick={() => setOrderPage(page)}
                  className={`btn btn-sm ${page === orderPage ? 'bg-gray-300 text-black' : 'btn-ghost text-gray-600'}`}
                >{page}</button>
              );
            })}
            <button
              onClick={() => setOrderPage(p => Math.min(orderTotalPages, p + 1))}
              className="btn btn-sm"
              disabled={orderPage === orderTotalPages}
            >»</button>
          </div>
        </div>
      </div>

      {/* Order Modal */}
      {orderManagementModalOpen && selectedOrder && (
        <OrderManagementModal
          isOpen={orderManagementModalOpen}
          onClose={fetchOrders}
          onCloseNoRefresh={handleCloseModalWithoutRefresh}
          order={selectedOrder}
          onStatusUpdate={(orderId, newStatus, newTransactionStatus) => {
            setOrderRows(prevRows =>
              prevRows.map(row =>
                row.id === orderId ? { ...row, status: newStatus, payment_status: newTransactionStatus } : row
              )
            );
            fetchOrders();
          }}
        />
      )}
    </div>
  );
}
