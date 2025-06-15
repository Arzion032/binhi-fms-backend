import React, { useState, useEffect } from "react";
import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000";

const ORDER_STATUSES = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"];
const PAYMENT_STATUS_LIST = ["Pending", "Paid", "Refunded"];
const PAYMENT_METHODS = ["GCash", "Cash on Delivery"];

export default function OrderManagementModal({
  isOpen,
  onClose,
  order,
  onStatusUpdate,
  onCloseNoRefresh,
}) {
  const [orderStatus, setOrderStatus] = useState(order?.status || "Processing");
  const [paymentStatus, setPaymentStatus] = useState(order?.payment_status || "Pending");
  const paymentMethod = order?.payment_method || "Cash on Delivery";
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const [showDisregardModal, setShowDisregardModal] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [successType, setSuccessType] = useState(""); // "confirm" | "disregard"

  useEffect(() => {
    if (paymentMethod === "GCash") {
      setPaymentStatus("Paid");
    }
  }, [paymentMethod]);

  useEffect(() => {
    setOrderStatus(order?.status || "Processing");
    setPaymentStatus(order?.payment_status || "Pending");
  }, [order]);

  if (!isOpen || !order) return null;

  async function handleConfirmSubmit() {
    try {
      setIsLoading(true);
      setError(null);

      // Update order status AND payment_status
      await axios.patch(
        `${API_BASE_URL}/orders/orders/${order.id}/status/`,
        {
          status: orderStatus.toLowerCase(),
          payment_status: paymentStatus,
        }
      );

      setShowConfirmModal(false);
      setSuccessType("confirm");
      setShowSuccessModal(true);

      if (onStatusUpdate) {
        onStatusUpdate(order.id, orderStatus, paymentStatus);
      }
    } catch (err) {
      setError('Failed to update order. Please try again.');
      console.error('Error updating order:', err);
    } finally {
      setIsLoading(false);
    }
  }

  function handleDisregardSubmit() {
    setShowDisregardModal(false);
    setSuccessType("disregard");
    setShowSuccessModal(true);
    onClose();
  }

  return (
    <div className="fixed z-50 inset-0 flex items-center justify-center bg-black bg-opacity-30">
      {/* Main Modal */}
      <div
        className="relative bg-white w-full max-w-md mx-auto rounded-[2.2rem] shadow-xl p-9 pt-8 border"
        style={{ minWidth: 370, maxWidth: 490, borderColor: "#b5b5b5" }}
      >
        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center rounded-[2.2rem]">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
          </div>
        )}

        {/* Close button */}
        <button
          type="button"
          onClick={onCloseNoRefresh}
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
            <div>{order.customer.contact}</div>
          </div>
        </div>
        <div className="text-gray-900 font-semibold mt-1 mb-2 text-sm">
          Date Ordered
        </div>
        <div className="text-gray-400 mb-2 text-sm">
          {order.date} {order.time}
        </div>

        {order.transaction && (
          <div className="grid grid-cols-2 gap-y-2 gap-x-4 mb-3 text-sm">
            <div>
              <span className="font-semibold text-black">Total Amount</span>
              <div className="text-[#16A34A] font-semibold">
                ₱{(() => {
                  const amount = parseFloat(order.total_price);
                  return isNaN(amount) ? '0.00' : amount.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                  });
                })()}
              </div>
            </div>
            <div>
              <span className="font-semibold text-black">Transaction ID</span>
              <div>{order.transaction.id}</div>
            </div>
          </div>
        )}

        {/* Dropdowns */}
        <div className="mb-2">
          <label className="font-semibold text-black text-sm mb-1 block">
            Order Status
          </label>
          <select
            className="w-full rounded-full border px-4 py-2 text-base bg-white focus:outline-none focus:ring-2 focus:ring-green-200"
            value={orderStatus}
            onChange={e => setOrderStatus(e.target.value)}
            disabled={isLoading}
          >
            {ORDER_STATUSES.map(os => (
              <option key={os} value={os}>{os}</option>
            ))}
          </select>
        </div>

        <div className="mb-2">
          <label className="font-semibold text-black text-sm mb-1 block">
            Payment Method
          </label>
          <input
            type="text"
            className="w-full rounded-full border px-4 py-2 text-base bg-gray-100 cursor-not-allowed"
            value={paymentMethod}
            readOnly
            disabled
          />
        </div>

        <div className="mb-5">
          <label className="font-semibold text-black text-sm mb-1 block">
            Payment Status
          </label>
          <select
            className="w-full rounded-full border px-4 py-2 text-base bg-white focus:outline-none focus:ring-2 focus:ring-green-200"
            value={paymentStatus}
            onChange={e => setPaymentStatus(e.target.value)}
            disabled={isLoading || paymentMethod === "GCash"}
          >
            {PAYMENT_STATUS_LIST.map(status => (
              <option key={status} value={status}>{status}</option>
            ))}
          </select>
        </div>

        <div className="flex justify-between gap-4 mt-10">
          <button
            type="button"
            onClick={() => setShowDisregardModal(true)}
            className="flex-1 bg-[#EF4444] text-white font-semibold rounded-full py-4 text-lg transition hover:bg-[#DC2626] focus:outline-none focus:ring-2 focus:ring-[#DC2626]"
            style={{ fontSize: "1.15rem" }}
            disabled={isLoading}
          >
            Disregard
          </button>
          <button
            type="button"
            onClick={() => setShowConfirmModal(true)}
            className="flex-1 bg-[#16A34A] text-white font-semibold rounded-full py-4 text-lg transition hover:bg-[#15803D] focus:outline-none focus:ring-2 focus:ring-[#15803D]"
            style={{ fontSize: "1.15rem" }}
            disabled={isLoading}
          >
            Confirm
          </button>
        </div>
      </div>

      {/* DISREGARD Confirmation Modal */}
      {showDisregardModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30">
          <div className="bg-white rounded-3xl shadow-xl relative p-10 w-full max-w-xl text-center border" style={{ borderColor: "#b5b5b5" }}>
            <button
              onClick={() => setShowDisregardModal(false)}
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
                onClick={() => setShowDisregardModal(false)}
                className="bg-[#FF3B3F] text-white font-semibold rounded-full px-12 py-4 text-base hover:bg-[#ff5c5c] transition"
                style={{ minWidth: 140, fontSize: "1.12rem" }}
                disabled={isLoading}
              >
                Cancel
              </button>
              <button
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

      {/* CONFIRM Confirmation Modal */}
      {showConfirmModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30">
          <div className="bg-white rounded-3xl shadow-xl relative p-10 w-full max-w-xl text-center border" style={{ borderColor: "#b5b5b5" }}>
            <button
              onClick={() => setShowConfirmModal(false)}
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
                onClick={() => setShowConfirmModal(false)}
                className="border-2 border-[#43B864] font-semibold rounded-full px-12 py-4 text-base bg-white text-[#43B864] transition"
                style={{ minWidth: 140, fontSize: "1.12rem" }}
                disabled={isLoading}
              >
                Cancel
              </button>
              <button
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

      {/* SUCCESS Modal */}
      {showSuccessModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30">
          <div className="bg-white rounded-3xl shadow-xl relative p-10 w-full max-w-xl text-center border" style={{ borderColor: "#b5b5b5" }}>
            <button
              onClick={() => {
                setShowSuccessModal(false);
                onCloseNoRefresh && onCloseNoRefresh();
              }}
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
                onClick={() => setShowSuccessModal(false)}
                className="border-2 border-[#43B864] font-semibold rounded-full px-12 py-4 text-base bg-white text-[#43B864] transition"
                style={{ minWidth: 140, fontSize: "1.12rem" }}
                disabled={isLoading}
              >
                Back
              </button>
              <button
                onClick={() => {
                  setShowSuccessModal(false);
                  onClose && onClose();
                }}
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
    </div>
  );
}
