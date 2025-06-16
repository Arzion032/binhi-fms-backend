import React, { useState, useRef, useEffect } from 'react';

// ICONS (inline SVGs for no dependencies)
const PencilIcon = ({ className = "" }) => (
  <svg viewBox="0 0 24 24" width={18} height={18} fill="none" stroke="#333" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><path d="M12 20h9" /><path d="M16.5 3.5a2.121 2.121 0 1 1 3 3L7 19.5 2 20l.5-5L16.5 3.5z" /></svg>
);
const TrashIcon = ({ className = "" }) => (
  <svg viewBox="0 0 24 24" width={18} height={18} fill="none" stroke="#DC2626" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><polyline points="3 6 5 6 21 6" /><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2" /><line x1="10" y1="11" x2="10" y2="17" /><line x1="14" y1="11" x2="14" y2="17" /></svg>
);
const PlusIcon = ({ className = "" }) => (
  <svg width={22} height={22} fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" className={className}>
    <line x1="12" y1="5" x2="12" y2="19" />
    <line x1="5" y1="12" x2="19" y2="12" />
  </svg>
);

const MEASUREMENT_OPTIONS = [
  'pcs', 'kg', 'g', 'pounds', 'liters', 'ml', 'sacks', 'boxes', 'dozen'
];

function VariationModal({ isOpen, onClose, onConfirm, variationNumber, initialValue }) {
  const [name, setName] = useState(initialValue?.name || '');
  const [image, setImage] = useState(initialValue?.image || null);
  const [price, setPrice] = useState(initialValue?.price || '');
  const [unitMeasurement, setUnitMeasurement] = useState(initialValue?.unitMeasurement?.quantity || '');
  const [unitType, setUnitType] = useState(initialValue?.unitMeasurement?.type || '');
  const [stock, setStock] = useState(initialValue?.stock || '');
  const [error, setError] = useState('');
  const [priceError, setPriceError] = useState('');
  const [stockError, setStockError] = useState('');
  const [unitError, setUnitError] = useState('');

  useEffect(() => {
    setName(initialValue?.name || '');
    setImage(initialValue?.image || null);
    setPrice(initialValue?.price || '');
    setUnitMeasurement(initialValue?.unitMeasurement?.quantity || '');
    setUnitType(initialValue?.unitMeasurement?.type || '');
    setStock(initialValue?.stock || '');
    setError('');
    setPriceError('');
    setStockError('');
    setUnitError('');
  }, [initialValue, isOpen]);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => setImage(reader.result);
    reader.readAsDataURL(file);
  };

  const handlePriceChange = (e) => {
    let value = e.target.value.replace(/[^0-9.]/g, '');
    if ((value.match(/\./g) || []).length > 1) {
      value = value.substring(0, value.length - 1);
    }
    setPrice(value);
    if (!value || parseFloat(value) <= 0) {
      setPriceError('Unit Price must be greater than zero.');
    } else {
      setPriceError('');
    }
  };

  const handleStockChange = (e) => {
    let value = e.target.value.replace(/\D/g, '');
    setStock(value);
    if (!value || parseInt(value) <= 0) {
      setStockError('Stock must be greater than zero.');
    } else {
      setStockError('');
    }
  };

  const handleUnitMeasurementChange = (e) => {
    let value = e.target.value.replace(/\D/g, '');
    setUnitMeasurement(value);
    if (!value || parseInt(value) <= 0) {
      setUnitError('Unit Quantity must be greater than zero.');
    } else {
      setUnitError('');
    }
  };

  const handleConfirm = () => {
    if (!name.trim()) {
      setError('Product Name is required.');
      return;
    }
    if (!image) {
      setError('Product Picture is required.');
      return;
    }
    if (!price || isNaN(price) || parseFloat(price) <= 0) {
      setError('');
      setPriceError('Unit Price must be greater than zero.');
      return;
    }
    if (!unitMeasurement || isNaN(unitMeasurement) || Number(unitMeasurement) <= 0) {
      setError('');
      setUnitError('Unit Quantity must be greater than zero.');
      return;
    }
    if (!unitType) {
      setError('');
      setUnitError('Unit Type is required.');
      return;
    }
    if (!stock || isNaN(stock) || parseInt(stock) <= 0) {
      setError('');
      setStockError('Stock must be greater than zero.');
      return;
    }
    setError('');
    setPriceError('');
    setStockError('');
    setUnitError('');
    onConfirm && onConfirm({ name, image, price, unitMeasurement: { quantity: unitMeasurement, type: unitType }, stock });
    onClose && onClose();
  };

  if (!isOpen) return null;

  const inputBox = "w-full px-6 py-3 rounded-[2rem] border border-[#D1D5DB] focus:border-[#16A34A] focus:ring-2 focus:ring-[#16A34A] text-base bg-white placeholder-[#B7B7B7] font-medium";
  const discardBtn = "flex-1 font-bold rounded-full py-4 text-lg bg-[#F64B4B] text-white hover:bg-[#DD2626] transition";
  const confirmBtn = "flex-1 font-bold rounded-full py-4 text-lg bg-[#159945] text-white hover:bg-green-700 transition";

  return (
    <div className="fixed z-50 inset-0 flex items-center justify-center bg-black bg-opacity-40">
      <div className="relative bg-white w-full max-w-[520px] mx-auto rounded-[2.2rem] shadow-xl p-9 pt-8" style={{ minWidth: 320, border: '1px solid #ececec' }}>
        <button type="button" onClick={onClose} className="absolute right-7 top-7 text-gray-400 hover:text-gray-700 rounded-full focus:outline-none text-2xl" aria-label="Close">
          <svg width={26} height={26} fill="none" viewBox="0 0 24 24">
            <path stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" d="M6 6l12 12M6 18L18 6" />
          </svg>
        </button>
        <h2 className="text-[1.6rem] font-bold text-[#193319] mb-0 leading-tight" style={{ letterSpacing: "-1px" }}>
          Variation {variationNumber}
        </h2>
        <p className="text-base text-gray-600 mb-2">Please enter the details of Variation {variationNumber}.</p>
        <hr className="mb-6 mt-1 border-[#D8D8D8]" />
        <div className="mb-4">
          <label className="font-semibold text-[17px] mb-1 block text-[#222A35]">
            Product Name <span style={{ color: '#FF3B3F' }}>*</span>
          </label>
          <input className={inputBox} value={name} onChange={e => setName(e.target.value)} placeholder="Enter the Equipment" required />
        </div>
        <div className="mb-4">
          <label className="font-semibold text-[17px] mb-1 block text-[#222A35]">
            Product Picture <span style={{ color: '#FF3B3F' }}>*</span>
          </label>
          <div className="flex">
            <label className="flex flex-col items-center justify-center border-2 border-dashed border-[#C1C1C1] rounded-xl w-[85px] h-[85px] text-[#888] text-xs bg-[#fafafa] cursor-pointer hover:border-[#16A34A] transition">
              {image ? (
                <img src={image} alt={`Preview`} className="w-full h-full object-cover rounded-xl" />
              ) : (
                <>
                  <span className="text-2xl font-bold">+</span>
                  <span>Add Image</span>
                </>
              )}
              <input type="file" accept="image/*" className="hidden" onChange={handleImageChange} />
            </label>
          </div>
        </div>
        <div className="mb-4">
          <label className="font-semibold text-[17px] mb-1 block text-[#222A35]">
            Unit Price <span style={{ color: '#FF3B3F' }}>*</span>
          </label>
          <div className="flex items-center relative">
            <span className="absolute left-6 text-gray-500 text-lg font-bold">₱</span>
            <input
              className="w-full pl-10 pr-4 py-3 rounded-[2rem] border border-[#D1D5DB] focus:border-[#16A34A] focus:ring-2 focus:ring-[#16A34A] text-base bg-white placeholder-[#B7B7B7] font-medium"
              value={price}
              onChange={handlePriceChange}
              placeholder="Enter Unit Price"
              inputMode="decimal"
            />
          </div>
          {priceError && <p className="text-red-500 text-sm mt-1">{priceError}</p>}
        </div>
        <div className="mb-4">
          <label className="font-semibold text-[17px] mb-1 block text-[#222A35]">
            Unit Quantity <span style={{ color: '#FF3B3F' }}>*</span>
          </label>
          <input
            className={inputBox}
            type="number"
            min={1}
            step={1}
            value={unitMeasurement}
            onChange={handleUnitMeasurementChange}
            placeholder="e.g. 1, 2, 5"
            required
          />
        </div>
        <div className="mb-4">
          <label className="font-semibold text-[17px] mb-1 block text-[#222A35]">
            Unit Type <span style={{ color: '#FF3B3F' }}>*</span>
          </label>
          <select
            className={inputBox}
            value={unitType || ''}
            onChange={e => setUnitType(e.target.value)}
            required
          >
            <option value="">Select unit</option>
            {MEASUREMENT_OPTIONS.map(opt => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
        </div>
        <div className="mb-8">
          <label className="font-semibold text-[17px] mb-1 block text-[#222A35]">
            Stock <span style={{ color: '#FF3B3F' }}>*</span>
          </label>
          <input
            className={inputBox}
            value={stock}
            onChange={handleStockChange}
            placeholder="0"
            inputMode="numeric"
            min={1}
            required
          />
          {stockError && <p className="text-red-500 text-sm mt-1">{stockError}</p>}
        </div>
        {unitError && <p className="text-red-500 text-sm mt-1">{unitError}</p>}
        {error && <p className="text-red-500 text-sm mt-1">{error}</p>}
        <div className="flex gap-4 mt-4">
          <button type="button" className={discardBtn} onClick={onClose}>Disregard</button>
          <button type="button" className={confirmBtn} onClick={handleConfirm}>Confirm</button>
        </div>
      </div>
    </div>
  );
}

export default function AddProductModal({ isOpen, onClose, onSaveProduct }) {
  const [productName, setProductName] = useState('');
  const [category, setCategory] = useState('');
  const [images, setImages] = useState(Array(5).fill(null));
  const [description, setDescription] = useState('');
  const [association] = useState('Darangan Farmers Association');
  const [farmerCode, setFarmerCode] = useState('');
  const [variants, setVariants] = useState([{}]);
  const [showVariationModal, setShowVariationModal] = useState(false);
  const [editingVariantIndex, setEditingVariantIndex] = useState(null);
  const [error, setError] = useState('');
  const [backendError, setBackendError] = useState('');
  const [categories, setCategories] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/products/categories/');
        if (!response.ok) {
          throw new Error('Failed to fetch categories');
        }
        const data = await response.json();
        setCategories(data);
      } catch (err) {
        console.error('Error fetching categories:', err);
        setError('Failed to load categories. Please try again.');
      }
    };

    if (isOpen) {
      fetchCategories();
    }
  }, [isOpen]);

  const handleImageChange = (e, idx) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      setImages(imgs => imgs.map((img, i) => (i === idx ? reader.result : img)));
    };
    reader.readAsDataURL(file);
  };

  const handleAddVariant = () => {
    setVariants(prev => [...prev, {}]);
  };

  const handleDeleteVariant = (idx) => {
    if (variants.length > 1) {
      setVariants(prev => prev.filter((_, i) => i !== idx));
    }
  };

  function validateProduct(isDraft = false) {
    if (!isDraft) {
      if (!productName.trim()) {
        setError('Product name is required.');
        return false;
      }
      if (!category.trim()) {
        setError('Category is required.');
        return false;
      }
      if (!images.filter(Boolean).length) {
        setError('At least one product image is required.');
        return false;
      }
      for (const v of variants) {
        if (
          !v.name ||
          !v.price ||
          !v.unitMeasurement ||
          !v.unitMeasurement.quantity ||
          !v.unitMeasurement.type ||
          !v.stock
        ) {
          setError('Each variant must have a name, price, unit measurement, unit type, and stock.');
          return false;
        }
        if (isNaN(v.price) || Number(v.price) <= 0) {
          setError('Each variant Unit Price must be greater than zero.');
          return false;
        }
        if (isNaN(v.unitMeasurement.quantity) || Number(v.unitMeasurement.quantity) <= 0) {
          setError('Each variant Unit Quantity must be greater than zero.');
          return false;
        }
        if (!v.unitMeasurement.type) {
          setError('Each variant Unit Type is required.');
          return false;
        }
        if (isNaN(v.stock) || Number(v.stock) <= 0) {
          setError('Each variant Stock must be greater than zero.');
          return false;
        }
      }
      const names = variants.map(v => v.name && v.name.trim().toLowerCase()).filter(Boolean);
      const hasDuplicate = names.some((name, idx) => names.indexOf(name) !== idx);
      if (hasDuplicate) {
        setError('Each variant name must be unique.');
        return false;
      }
      if (!farmerCode.trim()) {
        setError('Farmer code is required.');
        return false;
      }
      if (!description.trim()) {
        setError('Description is required.');
        return false;
      }
    }
    setError('');
    return true;
  }

  // UPDATED handleSaveSubmit
  const handleSaveSubmit = async (e) => {
    if (e) e.preventDefault();
    if (!validateProduct(false)) return;
    try {
      const filledVariants = variants
        .filter(
          v => v && v.name && v.price && v.unitMeasurement && v.unitMeasurement.quantity && v.unitMeasurement.type && v.stock
        )
        .map((v, idx) => ({
          name: v.name,
          unit_price: Number(v.price),
          stock: Number(v.stock),
          unit_measurement: `${v.unitMeasurement.quantity} ${v.unitMeasurement.type}`,
          is_available: true,
          is_default: idx === 0,
          status: "active"
        }));

      // Convert base64 images to File objects
      const imageFiles = await Promise.all(
        images
          .filter(Boolean)
          .map(async (base64Image, index) => {
            const response = await fetch(base64Image);
            const blob = await response.blob();
            return new File([blob], `image-${index}.jpg`, { type: 'image/jpeg' });
          })
      );

      // Defensive check for required fields
      if (
        !productName.trim() ||
        !category ||
        !imageFiles.length ||
        !description.trim() ||
        !farmerCode.trim() ||
        !filledVariants.length
      ) {
        setError('Please fill in all required fields.');
        return;
      }

      // Build the plain object
      const productData = {
        name: productName.trim(),
        description: description.trim(),
        category,
        vendor_id: 'cc9bbb5a-a701-4374-95f9-585857d5b211', // Replace with actual vendor_id logic if needed
        images: imageFiles,
        variations: filledVariants,
        farmer_id: farmerCode.trim(),
      };

      onSaveProduct(productData); // Pass plain object, not FormData
      onClose();
    } catch (error) {
      console.error('Error preparing product data:', error);
      setBackendError(error.message || 'Failed to prepare product data');
    }
  };

  const inputBox = "w-full px-6 py-3 rounded-[2rem] border border-[#D1D5DB] focus:border-[#16A34A] focus:ring-2 focus:ring-[#16A34A] text-base bg-white placeholder-[#B7B7B7] font-medium";
  const labelStyle = "font-semibold text-[17px] mb-1 block text-[#222A35]";
  const discardBtn = "flex-1 font-bold rounded-full py-4 text-lg bg-[#F64B4B] text-white hover:bg-[#DD2626] transition";
  const submitBtn = "flex-1 font-bold rounded-full py-4 text-lg bg-[#159945] text-white hover:bg-green-700 transition";

  return !isOpen ? null : (
    <div className="fixed z-50 inset-0 flex items-center justify-center bg-black bg-opacity-50">
      <form
        className="relative bg-white w-full max-w-[700px] mx-auto rounded-[2.8rem] shadow-2xl p-10 pt-9"
        style={{ border: '1px solid #f0f0f0', minWidth: 370, transition: 'height 0.25s cubic-bezier(.4,2.3,.3,1)' }}
        onSubmit={handleSaveSubmit}
      >
        <button
          type="button"
          onClick={onClose}
          className="absolute right-8 top-8 text-gray-400 hover:text-gray-700 rounded-full focus:outline-none text-2xl"
          aria-label="Close"
        >
          <svg width={26} height={26} fill="none" viewBox="0 0 24 24">
            <path stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" d="M6 6l12 12M6 18L18 6" />
          </svg>
        </button>
        <h2 className="text-[2rem] font-bold text-[#193319] mb-0 leading-tight" style={{ letterSpacing: "-1px" }}>Add Product</h2>
        <p className="text-base text-gray-600 mb-2">Please enter the new product.</p>
        <hr className="mb-6 mt-1 border-[#D8D8D8]" />

        {/* Product Name & Category */}
        <div className="grid grid-cols-2 gap-4 mb-5">
          <div>
            <label className={labelStyle}>Product Name <span style={{ color: '#FF3B3F' }}>*</span></label>
            <input
              className={inputBox}
              value={productName}
              onChange={e => setProductName(e.target.value)}
              placeholder="Enter the Equipment"
              required
            />
          </div>
          <div>
            <label className={labelStyle}>Category <span style={{ color: '#FF3B3F' }}>*</span></label>
            <div className="relative">
              <select
                className={inputBox}
                value={category}
                onChange={e => setCategory(e.target.value)}
                required
                disabled={isLoading}
              >
                <option value="">Please select a category</option>
                {categories.map(cat => (
                  <option key={cat.id} value={cat.id}>{cat.name}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Association & Farmer Code */}
        <div className="grid grid-cols-2 gap-4 mb-5">
          <div>
            <label className={labelStyle}>Association </label>
            <input
              className={inputBox}
              value={association}
              disabled
              style={{ color: "#999", backgroundColor: "#f4f4f4" }}
              placeholder="Macamot Farmers Association"
              readOnly
            />
          </div>
          <div>
            <label className={labelStyle}>
              Farmer Code <span style={{ color: '#FF3B3F' }}>*</span>
            </label>
            <input
              className={inputBox}
              value={farmerCode}
              onChange={e => setFarmerCode(e.target.value)}
              placeholder="Enter Farmer Code"
              required
            />
          </div>
        </div>

        {/* Product Pictures */}
        <div className="mb-2">
          <div className="flex items-end justify-between">
            <label className={labelStyle + " mb-0"}>Product Picture <span style={{ color: '#FF3B3F' }}>*</span></label>
            <span className="text-[#FF3B3F] text-2xl font-bold" style={{ visibility: 'hidden' }}>*</span>
          </div>
          <div className="flex gap-3 mt-1 mb-2">
            {images.map((img, idx) => (
              <label
                key={idx}
                className="flex flex-col items-center justify-center border-2 border-dashed border-[#C1C1C1] rounded-xl w-[85px] h-[85px] text-[#888] text-xs bg-[#fafafa] cursor-pointer hover:border-[#16A34A] transition"
              >
                {img ? (
                  <img src={img} alt={`Preview ${idx}`} className="w-full h-full object-cover rounded-xl" />
                ) : (
                  <>
                    <span className="text-2xl font-bold">+</span>
                    <span>Add Image</span>
                  </>
                )}
                <input
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={e => handleImageChange(e, idx)}
                />
              </label>
            ))}
          </div>
        </div>

        {/* Description */}
        <div className="mb-4">
          <label className={labelStyle}>Description <span style={{ color: '#FF3B3F' }}>*</span></label>
          <textarea
            className="w-full px-6 py-3 rounded-[2rem] border border-[#D1D5DB] focus:border-[#16A34A] focus:ring-2 focus:ring-[#16A34A] text-base bg-white min-h-[90px] resize-none"
            value={description}
            onChange={e => setDescription(e.target.value)}
            placeholder="Description"
            rows={3}
            maxLength={600}
            style={{ fontSize: "15.5px", fontWeight: 500 }}
            required
          />
        </div>

        {/* Variants */}
        <div className="w-full mt-1 mb-1">
          <div className="flex justify-between items-center mb-2">
            <label className={labelStyle}>
              Product Variations <span style={{ color: '#FF3B3F' }}>*</span>
            </label>
            <button
              type="button"
              onClick={handleAddVariant}
              className="flex items-center gap-1 text-[#16A34A] hover:text-green-700 font-medium"
            >
              <PlusIcon className="w-5 h-5" />
              Add Variation
            </button>
          </div>
          <div
            id="variant-row"
            className="grid grid-cols-3 gap-x-4 gap-y-2"
          >
            {variants.map((variant, idx) => (
              <div
                key={idx}
                className="flex flex-col items-center mb-1"
                style={{ minWidth: 120, maxWidth: 210 }}
              >
                {variant?.name ? (
                  <div className="flex items-center border rounded-full px-2 py-2 bg-white w-full justify-between gap-2 shadow"
                    style={{
                      borderColor: "#C1C1C1",
                      minHeight: 44,
                      maxWidth: 210
                    }}
                  >
                    {variant.image ? (
                      <img src={variant.image} alt="variant" className="w-8 h-8 rounded-full object-cover border mr-2" />
                    ) : (
                      <div className="w-8 h-8 rounded-full bg-gray-200 mr-2 flex items-center justify-center" />
                    )}
                    <span className="font-semibold text-[15px] flex-1 truncate" title={variant.name}>
                      {variant.name}
                    </span>
                    <button
                      type="button"
                      className="p-1 hover:bg-gray-100 rounded-full"
                      onClick={() => {
                        setEditingVariantIndex(idx);
                        setShowVariationModal(true);
                      }}
                      aria-label="Edit Variant"
                    >
                      <PencilIcon />
                    </button>
                    {variants.length > 1 && (
                      <button
                        type="button"
                        className="p-1 hover:bg-red-50 rounded-full ml-1"
                        onClick={() => handleDeleteVariant(idx)}
                        aria-label="Delete Variant"
                      >
                        <TrashIcon />
                      </button>
                    )}
                  </div>
                ) : (
                  <button
                    type="button"
                    className="w-full flex items-center justify-center gap-2 py-4 bg-[#888] rounded-full font-semibold text-white text-base border-0"
                    tabIndex={-1}
                    onClick={() => {
                      setEditingVariantIndex(idx);
                      setShowVariationModal(true);
                    }}
                  >
                    <PlusIcon /> Add Variant
                  </button>
                )}
                <div className="text-center text-xs mt-1 text-gray-900 font-bold">
                  {`Variant ${idx + 1}`}
                  {idx === 0 && <span style={{ color: '#FF3B3F' }}>*</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
        {error && (
          <div className="text-red-500 text-base mb-3 text-center">{error}</div>
        )}
        {backendError && (
          <div className="text-red-500 text-base mb-3 text-center">{backendError}</div>
        )}
        <div className="flex gap-4 mt-8">
          <button type="button" className={discardBtn} onClick={onClose}>
            Disregard
          </button>
          <button type="submit" className={submitBtn}>
            Save and Submit
          </button>
        </div>
        <VariationModal
          isOpen={showVariationModal}
          onClose={() => setShowVariationModal(false)}
          onConfirm={(data) => {
            setVariants(prev =>
              prev.map((item, i) =>
                i === editingVariantIndex ? data : item
              )
            );
            setShowVariationModal(false);
          }}
          variationNumber={editingVariantIndex + 1}
          initialValue={variants[editingVariantIndex]}
        />
      </form>
    </div>
  );
} 