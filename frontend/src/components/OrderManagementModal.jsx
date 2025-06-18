import React, { useState, useEffect } from "react";
import axios from "axios";

// Cancellation Modal (inline)
const CANCELLATION_REASONS = [
  "Out of Stock",
  "Incorrect Pricing",
  "Logistical Problems",
  "Customer Request",
  "Payment Issues",
  "Others"
];

// Add this helper if you use a badge for payment status in the modal
const PAYMENT_BADGE_STYLES = {
  Pending: { color: "#F59E42", background: "#FFF6E9", border: "#F59E42" },
  Paid: { color: "#22C55E", background: "#DCFAE6", border: "#22C55E" },
  Refunded: { color: "#EF4444", background: "#FEE2E2", border: "#EF4444" },
  Returned: { color: "#EF4444", background: "#FEE2E2", border: "#EF4444" },
};

function OrderManagementCancelModal({
  isOpen,
  onClose,
  order,
  onStatusUpdate,
  handleFullClose
}) {
  const [selectedReason, setSelectedReason] = useState("");
  const [customReason, setCustomReason] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  if (!isOpen || !order) return null;

  const handleSubmit = async () => {
    try {
      setIsLoading(true);
      setError(null);

      await axios.patch(
        `http://127.0.0.1:8000/orders/orders/${order.id}/status/`,
        {
          status: "cancelled",
          cancellation_reason: selectedReason === "Others" ? customReason : selectedReason
        }
      );

      setShowConfirmModal(false);

      if (onStatusUpdate) {
        onStatusUpdate(order.id, "Cancelled", order.transaction);
      }

      handleFullClose();
    } catch (err) {
      setError("Failed to cancel order. Please try again.");
      console.error("Error cancelling order:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed z-50 inset-0 flex items-center justify-center bg-black bg-opacity-30">
      <div
        className="relative bg-white w-full max-w-md mx-auto rounded-[2.2rem] shadow-xl p-9 pt-8 border"
        style={{ minWidth: 370, maxWidth: 490, borderColor: "#b5b5b5" }}
      >
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        {isLoading && (
          <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center rounded-[2.2rem]">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
          </div>
        )}
        <button
          type="button"
          onClick={handleFullClose}
          className="absolute right-7 top-7 text-gray-500 hover:text-gray-900 rounded-full focus:outline-none text-2xl"
          aria-label="Close"
          disabled={isLoading}
        >
          <svg width={22} height={22} fill="none" viewBox="0 0 24 24">
            <path stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" d="M6 6l12 12M6 18L18 6" />
          </svg>
        </button>
        <h2 className="text-2xl font-bold leading-tight mb-0">Cancel Order</h2>
        <p className="text-base text-gray-600 mb-4">
          Please select a reason for cancelling this order.
        </p>
        <hr className="mb-6 mt-1" />
        <div className="space-y-4 mb-6">
          {CANCELLATION_REASONS.map((reason) => (
            <label key={reason} className="flex items-center space-x-3 cursor-pointer">
              <input
                type="radio"
                name="cancellation_reason"
                value={reason}
                checked={selectedReason === reason}
                onChange={(e) => setSelectedReason(e.target.value)}
                className="w-5 h-5 text-green-600 focus:ring-green-500"
                disabled={isLoading}
              />
              <span className="text-gray-700">{reason}</span>
            </label>
          ))}
        </div>
        {selectedReason === "Others" && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Please specify the reason
            </label>
            <textarea
              value={customReason}
              onChange={(e) => setCustomReason(e.target.value)}
              className="w-full rounded-lg border px-4 py-2 text-base bg-white focus:outline-none focus:ring-2 focus:ring-green-200"
              rows={3}
              placeholder="Enter cancellation reason..."
              disabled={isLoading}
            />
          </div>
        )}
        <div className="flex justify-between gap-4 mt-10">
          <button
            type="button"
            onClick={handleFullClose}
            className="flex-1 bg-gray-200 text-gray-700 font-semibold rounded-full py-4 text-lg transition hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-300"
            style={{ fontSize: "1.15rem" }}
            disabled={isLoading}
          >
            Back
          </button>
          <button
            type="button"
            onClick={() => setShowConfirmModal(true)}
            className="flex-1 bg-[#EF4444] text-white font-semibold rounded-full py-4 text-lg transition hover:bg-[#DC2626] focus:outline-none focus:ring-2 focus:ring-[#DC2626]"
            style={{ fontSize: "1.15rem" }}
            disabled={isLoading || !selectedReason || (selectedReason === "Others" && !customReason)}
          >
            Cancel Order
          </button>
        </div>
      </div>
      {showConfirmModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30">
          <div className="bg-white rounded-3xl shadow-xl relative p-10 w-full max-w-xl text-center border" style={{ borderColor: "#b5b5b5" }}>
            <button
              type="button"
              onClick={handleFullClose}
              className="absolute top-6 right-6 text-gray-400 hover:text-gray-600 text-2xl"
              aria-label="Close"
              style={{ background: "none", border: "none" }}
              disabled={isLoading}
            >
              &times;
            </button>
            <div className="flex justify-center mb-6">
              <div className="bg-[#FF4B4B] rounded-full flex items-center justify-center mb-2" style={{ width: 110, height: 110 }}>
                <svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" fill="none" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="12" fill="#FF4B4B" />
                  <path d="M12 7v5m0 4h.01" stroke="#fff" strokeWidth={2.5} strokeLinecap="round" />
                </svg>
              </div>
            </div>
            <h2 className="text-2xl font-bold mb-2 mt-1" style={{ color: "#222" }}>Confirm Cancellation?</h2>
            <p className="text-gray-700 mb-8">
              Are you sure you want to cancel this order?<br />
              This action cannot be undone.
            </p>
            <div className="flex justify-center gap-5 mt-2">
              <button
                type="button"
                onClick={handleFullClose}
                className="bg-gray-200 text-gray-700 font-semibold rounded-full px-12 py-4 text-base hover:bg-gray-300 transition"
                style={{ minWidth: 140, fontSize: "1.12rem" }}
                disabled={isLoading}
              >
                Back
              </button>
              <button
                type="button"
                onClick={handleSubmit}
                className="bg-[#EF4444] text-white font-semibold rounded-full px-12 py-4 text-base hover:bg-[#DC2626] transition"
                style={{ minWidth: 140, fontSize: "1.12rem" }}
                disabled={isLoading}
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Main Modal
const API_BASE_URL = "http://127.0.0.1:8000";
const ORDER_STATUSES = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"];
const PAYMENT_STATUS_LIST = ["Pending", "Paid", "Refunded"];

export default function OrderManagementModal({
  isOpen,
  onClose,
  onCloseNoRefresh,
  order,
  onStatusUpdate,
}) {
  const [editingStatus, setEditingStatus] = useState(null);
  const [paymentStatus, setPaymentStatus] = useState(order?.payment_status || "Pending");
  const paymentMethod = order?.payment_method || "Cash on Delivery";
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const [showDisregardModal, setShowDisregardModal] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [successType, setSuccessType] = useState(""); // "confirm" | "disregard"
  const [showCancelModal, setShowCancelModal] = useState(false);

  const isCancelled = order.status?.toLowerCase() === 'cancelled';

  // Universal modal close handler (for all X and Back buttons)
  const handleFullClose = () => {
    setShowDisregardModal(false);
    setShowConfirmModal(false);
    setShowSuccessModal(false);
    setShowCancelModal(false);
    setError(null);
    setIsLoading(false);
    if (typeof onCloseNoRefresh === "function") onCloseNoRefresh();
    else if (typeof onClose === "function") onClose();
  };

  // Sync state with incoming order
  useEffect(() => {
    setEditingStatus(null);
    setPaymentStatus(order?.payment_status || "Pending");
  }, [order]);

  // Payment Status Logic
  useEffect(() => {
    if (paymentMethod === "Cash on Delivery" && order.status === "Delivered") {
      setPaymentStatus("Paid");
    }
    if (paymentMethod === "Cash on Delivery" && order.status !== "Delivered") {
      if (paymentStatus === "Paid") setPaymentStatus("Pending");
    }
    if (paymentMethod === "GCash") {
      setPaymentStatus("Paid");
    }
  }, [paymentMethod, order.status]);

  if (!isOpen || !order) return null;

  async function handleConfirmSubmit() {
    try {
      setIsLoading(true);
      setError(null);

      await axios.patch(
        `${API_BASE_URL}/orders/orders/${order.id}/status/`,
        {
          status: editingStatus !== null ? editingStatus : order.status,
          payment_status: paymentStatus,
        }
      );

      setShowConfirmModal(false);
      setSuccessType("confirm");
      setShowSuccessModal(true);

      if (onStatusUpdate) {
        onStatusUpdate(order.id, editingStatus !== null ? editingStatus : order.status, paymentStatus);
      }
    } catch (err) {
      setError("Failed to update order. Please try again.");
      console.error("Error updating order:", err);
    } finally {
      setIsLoading(false);
    }
  }

  function handleDisregardSubmit() {
    setShowDisregardModal(false);
    setSuccessType("disregard");
    setShowSuccessModal(true);
    if (typeof onCloseNoRefresh === "function") onCloseNoRefresh();
    else if (typeof onClose === "function") onClose();
  }

  function formatReason(reason) {
    if (!reason || reason === '-') return '-';
    return reason
      .replace(/_/g, ' ')
      .replace(/\w\S*/g, w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase());
  }

  // In the modal, when displaying payment status:
  const displayPaymentStatus = order.status?.toLowerCase() === 'cancelled' ? 'Returned' : paymentStatus;

  return (
    <div className="fixed z-50 inset-0 flex items-center justify-center bg-black bg-opacity-30">
      <div
        className="relative bg-white w-full max-w-md mx-auto rounded-[2.2rem] shadow-xl p-9 pt-8 border"
        style={{ minWidth: 370, maxWidth: 490, borderColor: "#b5b5b5" }}
      >
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        {isLoading && (
          <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center rounded-[2.2rem]">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
          </div>
        )}
        {/* Close button */}
        <button
          type="button"
          onClick={handleFullClose}
          className="absolute right-7 top-7 text-gray-500 hover:text-gray-900 rounded-full focus:outline-none text-2xl"
          aria-label="Close"
          disabled={isLoading}
        >
          <svg width={22} height={22} fill="none" viewBox="0 0 24 24">
            <path stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" d="M6 6l12 12M6 18L18 6" />
          </svg>
        </button>
        <h2 className="text-2xl font-bold leading-tight mb-0">Order Details</h2>
        <p className="text-base text-gray-600 mb-4">
          Shown below is the order details.
        </p>
        <hr className="mb-6 mt-1" />
        <div className="flex items-center gap-4 mb-7">
          <img
            src={order.product.image || order.product.avatar || "/sampleproduct.png"}
            alt={order.product.name}
            className="rounded-full"
            style={{ width: 65, height: 65, objectFit: "cover" }}
          />
          <div>
            <div className="text-[1.3rem] font-bold text-[#222A35] leading-tight">{order.product.name}</div>
            <div className="text-[1rem] text-gray-600" style={{ marginTop: 2 }}>
              Variation: {order.product.variation}
            </div>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-y-2 gap-x-4 mb-3 text-sm">
          <div>
            <span className="font-semibold text-black">Name</span>
            <div>{order.customer.name}</div>
          </div>
          <div>
            <span className="font-semibold text-black">Order Code</span>
            <div>{order.orderId || order.id}</div>
          </div>
          <div>
            <span className="font-semibold text-black">Address</span>
            <div>{order.customer.address}</div>
          </div>
          <div>
            <span className="font-semibold text-black">Contact Number</span>
            <div>{order.buyer?.contact_no || '-'}</div>
          </div>
          <div>
            <span className="font-semibold text-black">Cancellation Reason</span>
            <div>{order.status?.toLowerCase() === 'cancelled' ? formatReason(order.cancellation_reason) : '-'}</div>
          </div>
        </div>
        <div className="text-gray-900 font-semibold mt-1 mb-2 text-sm">
          Date Ordered
        </div>
        <div className="text-gray-400 mb-2 text-sm">
          {order.date} {order.time}
        </div>
        <div className="mb-2">
          <label className="font-semibold text-black text-sm mb-1 block">
            Order Status
          </label>
          <select
            className={`w-full rounded-full border px-4 py-2 text-base bg-white focus:outline-none focus:ring-2 focus:ring-green-200 ${isCancelled ? "opacity-50 cursor-not-allowed" : ""}`}
            value={editingStatus !== null ? editingStatus : (order?.status || "Processing")}
            onChange={e => setEditingStatus(e.target.value)}
            disabled={isLoading || isCancelled}
          >
            {ORDER_STATUSES.map(os => (
              <option key={os} value={os}>{os}</option>
            ))}
          </select>
        </div>
        <div className="mb-5">
          <label className="font-semibold text-black text-sm mb-1 block">
            Payment Status
          </label>
          <select
            className="w-full rounded-full border px-4 py-2 text-base bg-white focus:outline-none focus:ring-2 focus:ring-green-200"
            value={paymentStatus}
            onChange={e => setPaymentStatus(e.target.value)}
            disabled={
              isLoading ||
              paymentMethod === "GCash" ||
              (paymentMethod === "Cash on Delivery" && order.status !== "Delivered") ||
              isCancelled
            }
          >
            {PAYMENT_STATUS_LIST.map(status => (
              <option
                key={status}
                value={status}
                disabled={
                  (paymentMethod === "Cash on Delivery" &&
                  status === "Paid" &&
                  order.status !== "Delivered") ||
                  isCancelled
                }
              >
                {status}
              </option>
            ))}
          </select>
        </div>
        {(order.status === "Pending" || order.status?.toLowerCase() === "pending") && !isCancelled && (
          <button
            type="button"
            onClick={() => setShowCancelModal(true)}
            className="w-full bg-[#EF4444] text-white font-semibold rounded-full py-4 text-lg transition hover:bg-[#DC2626] focus:outline-none focus:ring-2 focus:ring-[#DC2626]"
            style={{ fontSize: "1.15rem" }}
            disabled={isLoading}
          >
            Cancel Order
          </button>
        )}
        {!isCancelled && (
          <div className="flex flex-col gap-4 mt-10">
            <div className="flex justify-between gap-4">
              <button
                type="button"
                onClick={() => setShowDisregardModal(true)}
                className="flex-1 bg-[#EF4444] text-white font-semibold rounded-full py-4 text-lg transition hover:bg-[#DC2626] focus:outline-none focus:ring-2 focus:ring-[#DC2626]"
                style={{ fontSize: "1.15rem" }}
                disabled={isLoading || order.status === "Cancelled"}
              >
                Disregard
              </button>
              <button
                type="button"
                onClick={() => setShowConfirmModal(true)}
                className="flex-1 bg-[#16A34A] text-white font-semibold rounded-full py-4 text-lg transition hover:bg-[#15803D] focus:outline-none focus:ring-2 focus:ring-[#15803D]"
                style={{ fontSize: "1.15rem" }}
                disabled={isLoading || order.status === "Cancelled"}
              >
                Confirm
              </button>
            </div>
          </div>
        )}
      </div>
      {/* Disregard Modal */}
      {showDisregardModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30">
          <div className="bg-white rounded-3xl shadow-xl relative p-10 w-full max-w-xl text-center border" style={{ borderColor: "#b5b5b5" }}>
            <button
              type="button"
              onClick={handleFullClose}
              className="absolute top-6 right-6 text-gray-400 hover:text-gray-600 text-2xl"
              aria-label="Close"
              style={{ background: "none", border: "none" }}
              disabled={isLoading}
            >
              &times;
            </button>
            <div className="flex justify-center mb-6">
              <div className="bg-[#FF4B4B] rounded-full flex items-center justify-center mb-2" style={{ width: 110, height: 110 }}>
                <svg xmlns="http://www.w3.org/2000/svg" width="60" height="60" fill="none" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="12" fill="#FF4B4B" />
                  <path d="M12 7v5m0 4h.01" stroke="#fff" strokeWidth={2.5} strokeLinecap="round" />
                </svg>
              </div>
            </div>
            <h2 className="text-2xl font-bold mb-2 mt-1" style={{ color: "#222" }}>Disregard changes?</h2>
            <p className="text-gray-700 mb-8">
              This action cannot be undone.<br />
              The changes will be lost.
            </p>
            <div className="flex justify-center gap-5 mt-2">
              <button
                type="button"
                onClick={handleFullClose}
                className="bg-[#FF3B3F] text-white font-semibold rounded-full px-12 py-4 text-base hover:bg-[#ff5c5c] transition"
                style={{ minWidth: 140, fontSize: "1.12rem" }}
                disabled={isLoading}
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleDisregardSubmit}
                className="border-2 border-[#FF3B3F] font-semibold rounded-full px-12 py-4 text-base bg-white transition"
                style={{
                  minWidth: 140,
                  color: '#FF3B3F',
                  fontSize: "1.12rem"
                }}
                disabled={isLoading}
                onMouseEnter={e => {
                  e.currentTarget.style.background = '#FF3B3F';
                  e.currentTarget.style.color = '#fff';
                  e.currentTarget.style.borderColor = '#FF3B3F';
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.background = '#fff';
                  e.currentTarget.style.color = '#FF3B3F';
                  e.currentTarget.style.borderColor = '#FF3B3F';
                }}
              >
                Disregard
              </button>
            </div>
          </div>
        </div>
      )}
      {/* Confirm Modal */}
      {showConfirmModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30">
          <div className="bg-white rounded-3xl shadow-xl relative p-10 w-full max-w-xl text-center border" style={{ borderColor: "#b5b5b5" }}>
            <button
              type="button"
              onClick={handleFullClose}
              className="absolute top-6 right-6 text-gray-400 hover:text-gray-600 text-2xl"
              aria-label="Close"
              style={{ background: "none", border: "none" }}
              disabled={isLoading}
            >
              &times;
            </button>
            <div className="flex justify-center mb-6">
              <div className="bg-[#43B864] rounded-full flex items-center justify-center mb-2" style={{ width: 110, height: 110 }}>
                <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" fill="none" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="12" fill="#43B864" />
                  <polyline points="17 9.5 12 15 9 12.2" fill="none" stroke="#fff" strokeWidth={2.8} strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
            </div>
            <h2 className="text-2xl font-bold mb-2 mt-1" style={{ color: "#111" }}>Confirm changes?</h2>
            <p className="text-gray-700 mb-8" style={{ fontSize: "1.1rem" }}>
              Are you sure you want to save these changes to the order?
            </p>
            <div className="flex justify-center gap-5 mt-2">
              <button
                type="button"
                onClick={handleFullClose}
                className="border-2 border-[#43B864] font-semibold rounded-full px-12 py-4 text-base bg-white text-[#43B864] transition"
                style={{ minWidth: 140, fontSize: "1.12rem" }}
                disabled={isLoading}
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleConfirmSubmit}
                className="bg-[#43B864] text-white font-semibold rounded-full px-12 py-4 text-base hover:bg-[#369C52] transition"
                style={{ minWidth: 140, fontSize: "1.12rem" }}
                disabled={isLoading}
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
      {/* Success Modal */}
      {showSuccessModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30">
          <div className="bg-white rounded-3xl shadow-xl relative p-10 w-full max-w-xl text-center border" style={{ borderColor: "#b5b5b5" }}>
            <button
              type="button"
              onClick={handleFullClose}
              className="absolute top-6 right-6 text-gray-400 hover:text-gray-600 text-2xl"
              aria-label="Close"
              style={{ background: "none", border: "none" }}
              disabled={isLoading}
            >
              &times;
            </button>
            <div className="flex justify-center mb-6">
              <div className="bg-[#43B864] rounded-full flex items-center justify-center mb-2" style={{ width: 110, height: 110 }}>
                <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" fill="none" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="12" fill="#43B864" />
                  <polyline points="17 9.5 12 15 9 12.2" fill="none" stroke="#fff" strokeWidth={2.8} strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
            </div>
            <h2 className="text-2xl font-bold mb-2 mt-1" style={{ color: "#111", fontSize: "2rem" }}>
              {successType === "confirm" ? "Order updated successfully!" : "Order disregarded successfully!"}
            </h2>
            <p className="text-gray-700 mb-8" style={{ fontSize: "1.15rem" }}>
              {successType === "confirm"
                ? "Everything's set. Feel free to check it!"
                : "The order changes have been disregarded."}
            </p>
            <div className="flex justify-center gap-5 mt-2">
              <button
                type="button"
                onClick={handleFullClose}
                className="border-2 border-[#43B864] font-semibold rounded-full px-12 py-4 text-base bg-white text-[#43B864] transition"
                style={{ minWidth: 140, fontSize: "1.12rem" }}
                disabled={isLoading}
              >
                Back
              </button>
              <button
                type="button"
                onClick={handleFullClose}
                className="bg-[#43B864] text-white font-semibold rounded-full px-12 py-4 text-base hover:bg-[#369C52] transition"
                style={{ minWidth: 140, fontSize: "1.12rem" }}
                disabled={isLoading}
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}
      {/* Cancel Modal */}
      <OrderManagementCancelModal
        isOpen={showCancelModal}
        onClose={handleFullClose}
        handleFullClose={handleFullClose}
        order={order}
        onStatusUpdate={onStatusUpdate}
      />
    </div>
  );
}
