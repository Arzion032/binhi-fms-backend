import React, { useState, useRef, useEffect, useCallback } from 'react';
import { FaFilePdf, FaFileExcel } from 'react-icons/fa6';
import { Search, SlidersHorizontal, X, RefreshCw } from 'lucide-react';
import StatisticsChart from './StatisticsChart';
import TransactionModal from './TransactionModal';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function Financial() {
  // ─── TAB STATE & INDICATOR ───────────────────────────────────────────────────
  const [activeTab, setActiveTab] = useState('overview');
  const overviewRef = useRef();
  const historyRef = useRef();
  const tabsRef = useRef();
  const [indicator, setIndicator] = useState({ left: 0, width: 0 });
  const updateIndicator = useCallback(() => {
    const container = tabsRef.current;
    const btn = activeTab === 'overview' ? overviewRef.current : historyRef.current;
    if (container && btn) {
      const c = container.getBoundingClientRect();
      const b = btn.getBoundingClientRect();
      setIndicator({
        left: b.left - c.left + container.scrollLeft,
        width: b.width,
      });
    }
  }, [activeTab]);
  useEffect(() => {
    updateIndicator();
    window.addEventListener('resize', updateIndicator);
    return () => window.removeEventListener('resize', updateIndicator);
  }, [updateIndicator]);

  // ─── MODALS & ACTIONS ───────────────────────────────────────────────
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [downloadDropdownOpen, setDownloadDropdownOpen] = useState(false);
  const [historyDownloadOpen, setHistoryDownloadOpen] = useState(false);
  const [incomeModalOpen, setIncomeModalOpen] = useState(false);
  const [expenseModalOpen, setExpenseModalOpen] = useState(false);
  const dropdownRef = useRef();
  const downloadRef = useRef();
  const historyDownloadRef = useRef();
  const handleAddTransaction = (type) => {
    setDropdownOpen(false);
    if (type === 'income') setIncomeModalOpen(true);
    else setExpenseModalOpen(true);
  };
  const handleOverviewDownload = (type) => {
    console.log(`Downloading ${type}`);
    setDownloadDropdownOpen(false);
  };

  // ─── DATA STATES ───────────────────────────────────────────────────
  const [balance, setBalance] = useState(0);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [statisticsTrigger, setStatisticsTrigger] = useState(0);

  // ─── FETCH DATA ───────────────────────────────────────────────────
  const fetchBalance = async () => {
    console.log("Financial.jsx: Attempting to fetch balance...");
    try {
      const response = await axios.get(`${API_URL}/financials/federation_balance/`);
      console.log("Financial.jsx: Balance fetched successfully:", response.data.balance);
      setBalance(response.data.balance);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Financial.jsx: Error fetching balance:', error);
      setError('Failed to fetch balance');
    }
  };

  const fetchTransactions = async () => {
    console.log("Financial.jsx: Attempting to fetch transactions...");
    try {
      const response = await axios.get(`${API_URL}/financials/transactions`);
      console.log("Financial.jsx: Transactions fetched successfully:", response.data);
      setTransactions(response.data);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Financial.jsx: Error fetching transactions:', error);
      setError('Failed to fetch transactions');
    } finally {
      setLoading(false);
      console.log("Financial.jsx: Finished fetching transactions.");
    }
  };

  // Initial data fetch
  useEffect(() => {
    fetchBalance();
    fetchTransactions();
  }, []);

  // Auto-refresh every 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      fetchBalance();
      fetchTransactions();
    }, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  // ─── HISTORY DATA & HANDLERS ────────────────────────────────────────────────
  const itemsPerPage = 5;
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedRows, setSelectedRows] = useState([]);

  // --- Filter states and search ---
  const [showFilters, setShowFilters] = useState(false);
  const [selectedRole, setSelectedRole] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [selectedSource, setSelectedSource] = useState('');
  const [searchTransaction, setSearchTransaction] = useState('');

  // Filtering the transactions based on filters & search
  const filteredTransactions = transactions.filter(t => {
    const matchesRole = selectedRole ? (selectedRole === 'Income' ? true : true) : true;
    const matchesType = selectedType ? t.type === selectedType : true;
    const matchesSource = selectedSource ? t.source === selectedSource : true;
    const matchesSearch = searchTransaction.trim() === '' || t.admin.username.toLowerCase().includes(searchTransaction.trim().toLowerCase());
    return matchesRole && matchesType && matchesSource && matchesSearch;
  });

  const filteredTotalPages = Math.ceil(filteredTransactions.length / itemsPerPage);

  const paginatedTransactions = filteredTransactions.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  useEffect(() => {
    setCurrentPage(1);
    setSelectedRows([]);
  }, [searchTransaction, selectedRole, selectedType, selectedSource]);

  const handleDeleteTransaction = async (id) => {
    try {
      await axios.post(`${API_URL}/financials/del_transaction`, { id });
      await fetchTransactions();
      await fetchBalance();
    } catch (error) {
      console.error('Error deleting transaction:', error);
      setError('Failed to delete transaction');
    }
  };

  const handleTransactionSuccess = async () => {
    console.log("Financial.jsx: handleTransactionSuccess called!");
    await fetchTransactions();
    await fetchBalance();
    setStatisticsTrigger(prev => prev + 1);
    console.log("Financial.jsx: Data refetched after transaction success.");
  };

  const handlePageChange = (page) => {
    if (page >= 1 && page <= filteredTotalPages) {
      setCurrentPage(page);
      setSelectedRows([]);
    }
  };

  // ─── CLICK‐OUTSIDE DROPDOWNS ─────────────────────────────────────────────────
  useEffect(() => {
    function onClick(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) setDropdownOpen(false);
      if (downloadRef.current && !downloadRef.current.contains(e.target)) setDownloadDropdownOpen(false);
      if (historyDownloadRef.current && !historyDownloadRef.current.contains(e.target)) setHistoryDownloadOpen(false);
    }
    document.addEventListener('mousedown', onClick);
    return () => document.removeEventListener('mousedown', onClick);
  }, []);

  const handleHistoryDownload = (type) => {
    console.log(`Downloading ${type}`);
    setHistoryDownloadOpen(false);
  };

  // ─── HEADER ROWS (UPDATED DESIGN) ─────────────────────────────
  // Overview Tab: Balance Info + Buttons
  const headerRowOverview = (
    <div className="flex flex-wrap items-center justify-between my-4 gap-2">
      <div className="flex items-center gap-2 text-base font-medium">
        <RefreshCw size={20} stroke="#3b82f6" />
        <span className="font-medium text-lg" style={{ color: '#3b82f6' }}>Current Federation Balance:</span>
        <span className="text-blue-700 font-bold text-lg">₱{balance.toLocaleString()}</span>
        {lastUpdated && (
          <span className="text-gray-400 text-lg ml-2 opacity-60">
            Last Updated {lastUpdated.toLocaleTimeString()}
          </span>
        )}
      </div>
      <div className="flex gap-2">
        {/* Add Transaction Button */}
        <div className="relative z-20" ref={dropdownRef}>
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
              padding: "0.5rem 1.2rem",
              backgroundColor: "#16A34A",
              color: "#fff",
              border: "none",
              borderRadius: "9999px",
              fontWeight: 600,
              fontSize: "1rem",
              cursor: "pointer",
              boxShadow: "0 2px 8px 0 rgba(36,185,111,0.05)",
            }}
            className="font-semibold"
          >
            + Add Transaction
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={`w-4 h-4 ml-1 ${dropdownOpen ? 'rotate-180' : ''} transition-transform duration-200`}>
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </button>
          {dropdownOpen && (
            <ul className="absolute left-1/2 transform -translate-x-1/2 mt-2 menu p-2 shadow bg-white border border-black rounded-box w-52">
              <li><a onClick={() => handleAddTransaction('income')}>Income</a></li>
              <li><a onClick={() => handleAddTransaction('expense')}>Expense</a></li>
            </ul>
          )}
        </div>
        {/* Download Button */}
        <div className="relative z-20" ref={downloadRef}>
          <button
            onClick={() => setDownloadDropdownOpen(!downloadDropdownOpen)}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
              padding: "0.5rem 1.2rem",
              backgroundColor: "#fff",
              color: "#16A34A",
              border: "1.5px solid #16A34A",
              borderRadius: "9999px",
              fontWeight: 600,
              fontSize: "1rem",
              cursor: "pointer",
              boxShadow: "0 2px 8px 0 rgba(36,185,111,0.05)",
            }}
          >
            Download
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={`w-4 h-4 ml-1 ${downloadDropdownOpen ? 'rotate-180' : ''} transition-transform duration-200`}>
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </button>
          {downloadDropdownOpen && (
            <ul className="absolute left-1/2 transform -translate-x-1/2 mt-2 menu p-2 shadow bg-white border border-black rounded-box w-60">
              <li>
                <a onClick={() => handleOverviewDownload('PDF')} className="flex items-center gap-2">
                  <FaFilePdf className="text-red-500" /> Download PDF
                </a>
              </li>
              <li>
                <a onClick={() => handleOverviewDownload('Excel')} className="flex items-center gap-2">
                  <FaFileExcel className="text-green-600" /> Download Excel
                </a>
              </li>
              <div className="border-t my-2" />
              <li><a onClick={() => handleOverviewDownload('Custom Range')}>Custom Date Range</a></li>
            </ul>
          )}
        </div>
      </div>
    </div>
  );

  // Transaction History Tab: Balance left, Search+Download right, NO divider below
  const headerRowHistory = (
    <div className="flex flex-wrap items-center justify-between my-4 gap-2">
      <div className="flex items-center gap-2 text-base font-medium">
        <RefreshCw size={20} stroke="#3b82f6" />
        <span className="font-medium text-lg" style={{ color: '#3b82f6' }}>Current Federation Balance:</span>
        <span className="text-blue-700 font-bold text-lg">₱{balance.toLocaleString()}</span>
        {lastUpdated && (
          <span className="text-gray-400 text-lg ml-2 opacity-60">
            Last Updated {lastUpdated.toLocaleTimeString()}
          </span>
        )}
      </div>
      <div className="flex items-center gap-4 relative">
        {/* Search Bar */}
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
            placeholder="Search Transaction"
            className="flex-1 outline-none bg-white"
            value={searchTransaction}
            onChange={e => setSearchTransaction(e.target.value)}
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
            onClick={() => setShowFilters(!showFilters)}
            style={{
              position: "absolute",
              right: "0.75rem",
              top: "50%",
              transform: "translateY(-50%)",
              color: "#6B7280",
              cursor: "pointer",
            }}
          />
        </div>
        {/* Download */}
        <div className="dropdown dropdown-end" ref={historyDownloadRef} style={{ zIndex: 9999 }}>
          <button
            onClick={() => setHistoryDownloadOpen(!historyDownloadOpen)}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
              padding: "0.5rem 1.2rem",
              backgroundColor: "#fff",
              color: "#16A34A",
              border: "1.5px solid #16A34A",
              borderRadius: "9999px",
              fontWeight: 600,
              fontSize: "1rem",
              cursor: "pointer",
              boxShadow: "0 2px 8px 0 rgba(36,185,111,0.05)",
            }}
            className="relative"
          >
            Download
            <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          {historyDownloadOpen && (
            <ul tabIndex={0} className="dropdown-content menu p-2 shadow bg-base-100 border w-52 rounded-box z-50 absolute right-0 mt-2">
              <li><a onClick={() => handleHistoryDownload('PDF')}><FaFilePdf className="text-red-500" /> PDF</a></li>
              <li><a onClick={() => handleHistoryDownload('Excel')}><FaFileExcel className="text-green-600" /> Excel</a></li>
              <li><a onClick={() => handleHistoryDownload('Custom Range')}>Custom Range</a></li>
            </ul>
          )}
        </div>
      </div>
    </div>
  );

  console.log("Transactions data for rendering:", transactions);
  console.log("Paginated Transactions data for rendering:", paginatedTransactions);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-white">
        <div className="flex flex-col items-center gap-4">
          <img 
            src="/BINHI-LOADING-unscreen.gif" 
            alt="Loading..." 
            className="w-32 h-32 object-contain"
          />
          <p className="text-gray-600 font-medium">Loading financial data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-500 text-center p-4">
        Error: {error}
        <button 
          onClick={() => {
            setError(null);
            fetchTransactions();
          }}
          className="ml-4 px-4 py-2 bg-red-100 text-red-600 rounded-lg hover:bg-red-200"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="p-0">
      {/* Sticky Header & Tabs */}
      <div className="sticky top-0 z-30 w-full bg-[#f9fbf8] shadow-sm">
        <div className="flex items-center justify-between px-6 py-3">
          <div className="text-sm breadcrumbs font-inter text-base">
            <ul className="flex gap-1">
              <li><a className="text-green-600 underline">Dashboard</a></li>
              <li><a className="text-green-600 underline">Financial Tracker</a></li>
              <li className="text-gray-400">
                {activeTab === 'overview' ? 'Financial Overview' : 'Transaction History'}
              </li>
            </ul>
          </div>
          <button className="btn btn-square btn-binhi ml-4" aria-label="More options">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" className="w-5 h-5">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 12h.01M12 12h.01M19 12h.01" />
            </svg>
          </button>
        </div>
        <div className="px-6 pb-4 h-5 flex items-center">
          <h1 className="text-[40px] font-bold text-gray-800">
            Financial Tracker
          </h1>
        </div>
        <div className="mb-4 border-b border-gray-200 relative">
          <ul
            ref={tabsRef}
            className="flex flex-wrap -mb-px text-sm font-medium text-center"
            role="tablist"
          >
            <li className="mr-10" role="presentation">
              <button
                ref={overviewRef}
                className={`inline-block p-4 ${activeTab === 'overview' ? 'text-green-600' : 'text-gray-500 hover:text-gray-600'}`}
                onClick={() => setActiveTab('overview')}
                role="tabpanel"
                aria-selected={activeTab === 'overview'}
              >
                Financial Overview
              </button>
            </li>
            <li className="mr-10" role="presentation">
              <button
                ref={historyRef}
                className={`inline-block p-4 ${activeTab === 'history' ? 'text-green-600' : 'text-gray-500 hover:text-gray-600'}`}
                onClick={() => setActiveTab('history')}
                role="tabpanel"
                aria-selected={activeTab === 'history'}
              >
                Transaction History
              </button>
            </li>
          </ul>
          <div
            className="absolute bottom-0 h-0.5 bg-green-600 transition-all duration-300"
            style={{ left: indicator.left, width: indicator.width }}
          />
        </div>
      </div>

      {/* Header Row */}
      <div className="px-6">
        {activeTab === 'overview' ? headerRowOverview : headerRowHistory}
      </div>

      {/* Content */}
      {activeTab === 'overview' ? (
        <>
          {/* Overview Charts & Cards */}
          <div className="flex flex-col lg:flex-row gap-4 items-stretch mt-2 px-6">
            <div className="flex-1 flex flex-col gap-4">
              <div className="flex flex-col md:flex-row gap-4">
                {/* Income Card */}
                <div className="relative flex-1 bg-white rounded-2xl border border-gray-300 flex flex-col justify-between h-[170px] shadow-sm group">
                  <div className="absolute left-0 top-0 h-full w-3 rounded-tl-2xl rounded-bl-2xl bg-[#4caf50]" />
                  <div className="absolute top-4 right-4 z-20 group">
                    <button
                      onClick={() => setIncomeModalOpen(true)}
                      className="flex items-center gap-2 px-3 py-1 text-green-600 border border-green-600 rounded-full transition-all duration-200 group-hover:px-4 hover:bg-green-600 hover:text-white"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
                        <circle cx="12" cy="12" r="10" />
                        <line x1="12" y1="8" x2="12" y2="16" />
                        <line x1="8" y1="12" x2="16" y2="12" />
                      </svg>
                      <span className="text-sm font-semibold">Add Income</span>
                    </button>
                  </div>
                  <div className="flex flex-col justify-between h-full p-5">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-semibold text-gray-700">Total Income</span>
                        <span className="text-yellow-400 text-base">🔔</span>
                      </div>
                      <div className="text-3xl font-bold text-black mb-1">
                        ₱{transactions
                          .filter(t => t.type === 'income')
                          .reduce((sum, t) => sum + parseFloat(t.amount), 0)
                          .toLocaleString()}
                      </div>
                    </div>
                    <div className="flex items-end justify-between">
                      <div className="text-xs text-gray-500 flex items-center gap-1">
                        from last week <span className="text-xs">▼</span>
                      </div>
                      <div className="flex flex-col items-end">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 20 20" className="w-5 h-5 text-green-500">
                          <path d="M2 17h16M6 13l4-4 4 4M6 9l4-4 4 4" />
                        </svg>
                        <span className="text-green-600 text-base font-semibold">↑ 8.69%</span>
                      </div>
                    </div>
                  </div>
                </div>
                {/* Expense Card */}
                <div className="relative flex-1 bg-white rounded-2xl border border-gray-300 flex flex-col justify-between h-[170px] shadow-sm group">
                  <div className="absolute left-0 top-0 h-full w-3 rounded-tl-2xl rounded-bl-2xl bg-[#ff4d4f]" />
                  <div className="absolute top-4 right-4 z-20 group">
                    <button
                      onClick={() => setExpenseModalOpen(true)}
                      className="flex items-center gap-2 px-3 py-1 text-[#ff4d4f] border border-[#ff4d4f] rounded-full transition-all duration-200 group-hover:px-4 hover:bg-[#ff4d4f] hover:text-white"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
                        <circle cx="12" cy="12" r="10" />
                        <line x1="12" y1="8" x2="12" y2="16" />
                        <line x1="8" y1="12" x2="16" y2="12" />
                      </svg>
                      <span className="text-sm font-semibold">Add Expense</span>
                    </button>
                  </div>
                  <div className="flex flex-col justify-between h-full p-5">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-semibold text-gray-700">Total Expenses</span>
                        <span className="text-yellow-400 text-base">🔔</span>
                      </div>
                      <div className="text-3xl font-bold text-black mb-1">
                        ₱{transactions
                          .filter(t => t.type === 'expense')
                          .reduce((sum, t) => sum + parseFloat(t.amount), 0)
                          .toLocaleString()}
                      </div>
                    </div>
                    <div className="flex items-end justify-between">
                      <div className="text-xs text-gray-500 flex items-center gap-1">
                        from last week <span className="text-xs">▼</span>
                      </div>
                      <div className="flex flex-col items-end">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 20 20" className="w-5 h-5" style={{ color: '#ff4d4f' }}>
                          <path d="M10 3c-3.866 0-7 1.343-7 3s3.134 3 7 3 7-1.343 7-3-3.134-3-7-3z" />
                        </svg>
                        <span className="text-base font-semibold" style={{ color: '#ff4d4f' }}>↑ 8.69%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              {/* Chart */}
              <div className="flex-1 bg-white rounded-2xl border border-gray-300 p-6 shadow-sm w-full h-full min-h-[550px] overflow-visible relative">
                <StatisticsChart statisticsTrigger={statisticsTrigger} />
              </div>
            </div>
            {/* History Preview aside */}
            <div className="w-full lg:max-w-[340px] min-w-[300px] bg-white rounded-2xl border border-gray-300 p-6 shadow-sm flex flex-col h-full min-h-[750px]">
              <div className="flex justify-between items-center mb-2">
                <h3 className="text-xl font-bold text-black">History</h3>
                <button
                  onClick={() => setActiveTab('history')}
                  className="text-sm text-gray-500 hover:underline flex items-center gap-1"
                >
                  View All <span className="ml-1">→</span>
                </button>
              </div>
              <div className="flex-1 overflow-y-auto">
                <table className="w-full text-sm">
                  <thead className="text-gray-500 text-xs border-b">
                    <tr>
                      <th className="py-1 text-left">Date</th>
                      <th className="py-1 text-left">Name</th>
                      <th className="py-1 text-left">Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.slice(0, 5).map((transaction) => (
                      <tr key={transaction.id}>
                        <td className="py-1">
                          <div className="flex items-center gap-2">
                            <span 
                              className="w-2 h-2 rounded-full" 
                              style={{ backgroundColor: transaction.type === 'income' ? '#4caf50' : '#ff4d4f' }} 
                            />
                            {new Date(transaction.created_at).toLocaleDateString()}
                          </div>
                        </td>
                        <td className="py-1">{transaction.name || 'N/A'}</td>
                        <td className="py-1">₱{parseFloat(transaction.amount).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </>
      ) : (
        <>
          {/* Transaction History Tab Controls and Table */}
          {showFilters && (
            <div className="flex items-center space-x-1 p-2 rounded-lg w-fit px-6">
              <div className="flex items-center space-x-1 border rounded-l-3xl px-3 py-1 cursor-pointer bg-white border-[#858585] h-[35px]">
                <SlidersHorizontal className="w-4 h-4 text-[#3b82f6]" />
                <span className="mr-2 p-2 text-sm text-[#3b82f6] font-medium">Active Filters</span>
              </div>
              <select value={selectedRole} onChange={e => setSelectedRole(e.target.value)} className="border border-[#858585] h-[35px] text-sm bg-white text-[#858585] pl-2 pr-6">
                <option value="">Role</option>
                <option value="Income">Member</option>
              </select>
              <select value={selectedType} onChange={e => setSelectedType(e.target.value)} className="border border-[#858585] h-[35px] text-sm bg-white text-[#858585] pl-2 pr-6">
                <option value="">Type</option>
                <option value="income">Income</option>
                <option value="expense">Expense</option>
              </select>
              <select value={selectedSource} onChange={e => setSelectedSource(e.target.value)} className="border border-[#858585] h-[35px] text-sm	bg-white text-[#858585] pl-2 pr-6">
                <option value="">Source</option>
                <option value="Marketplace">Marketplace</option>
                <option value="-">-</option>
              </select>
              <button onClick={() => {
                setSelectedRole('');
                setSelectedType('');
                setSelectedSource('');
                setShowFilters(false);
                setSearchTransaction('');
              }} className="flex items-center space-x-1 border rounded-r-3xl px-3 py-1 text-sm border-[#858585] h-[35px] bg-white text-[#858585]">
                <X className="w-4 h-4 text-[#858585]" />
                <span>Clear</span>
              </button>
            </div>
          )}

          {/* Transaction Table */}
          <div className="w-full overflow-x-auto rounded-xl px-6">
            <h2 className="text-xl font-bold mb-4 px-4 pt-2">Transaction History</h2>
            <table className="table w-full">
              <thead className="bg-[#f7f7fb] text-sm text-gray-600 font-semibold">
                <tr>
                  <th>
                    <input type="checkbox" className="checkbox checkbox-sm rounded" checked={selectedRows.length === paginatedTransactions.length && paginatedTransactions.length > 0} onChange={e => {
                      if (e.target.checked) setSelectedRows(paginatedTransactions.map((_, i) => i));
                      else setSelectedRows([]);
                    }} />
                  </th>
                  <th>Name</th>
                  <th>Type</th>
                  <th>Source</th>
                  <th>Description</th>
                  <th>Amount</th>
                  <th>Date Added</th>
                </tr>
              </thead>
              <tbody>
                {paginatedTransactions.map((transaction, idx) => (
                  <tr key={transaction.id} className={selectedRows.includes(idx) ? 'bg-[#f0fdfa]' : ''}>
                    <td>
                      <input type="checkbox" className="checkbox checkbox-sm rounded" checked={selectedRows.includes(idx)} onChange={e => {
                        if (e.target.checked) setSelectedRows([...selectedRows, idx]);
                        else setSelectedRows(selectedRows.filter(i => i !== idx));
                      }} />
                    </td>
                    <td>
                      <div className="flex items-center gap-3">
                        <div className="avatar">
                          <div className="w-8 h-8 mask mask-squircle">
                            <img src="/sampleproduct.png" alt={transaction.name || 'N/A'} />
                          </div>
                        </div>
                        <div>
                          <div className="font-semibold">{transaction.name || 'N/A'}</div>
                          <div className="text-sm text-gray-500">{transaction.admin.email}</div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span className="px-3 py-1 rounded-full text-xs font-medium" style={{
                        color: transaction.type === 'income' ? '#15803d' : '#dc2626',
                        backgroundColor: transaction.type === 'income' ? '#d1fae5' : '#fee2e2',
                        border: `1px solid ${transaction.type === 'income' ? '#15803d' : '#dc2626'}`,
                        display: 'inline-block'
                      }}>
                        {transaction.type}
                      </span>
                    </td>
                    <td>{transaction.source}</td>
                    <td>{transaction.description}</td>
                    <td className="font-medium text-left">₱{parseFloat(transaction.amount).toLocaleString()}</td>
                    <td>
                      <div>{new Date(transaction.created_at).toLocaleDateString()}</div>
                      <div className="text-xs text-gray-500">
                        {new Date(transaction.created_at).toLocaleTimeString()}
                      </div>
                    </td>
                  </tr>
                ))}
                {paginatedTransactions.length === 0 && (
                  <tr>
                    <td colSpan={7} className="text-center text-gray-500 p-6">
                      No transactions found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>

            {/* Pagination */}
            <div className="flex justify-center my-6">
              <div className="flex items-center gap-1">
                <button onClick={() => handlePageChange(currentPage - 1)} className="btn btn-sm" disabled={currentPage === 1} aria-label="Previous page">«</button>
                {[...Array(filteredTotalPages)].map((_, i) => {
                  const page = i + 1;
                  return (
                    <button key={page} onClick={() => handlePageChange(page)} className={`btn btn-sm ${page === currentPage ? 'bg-gray-300 text-black' : 'btn-ghost text-gray-600'}`} aria-current={page === currentPage ? 'page' : undefined}>
                      {page}
                    </button>
                  );
                })}
                <button onClick={() => handlePageChange(currentPage + 1)} className="btn btn-sm" disabled={currentPage === filteredTotalPages} aria-label="Next page">»</button>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Modals */}
      <TransactionModal 
        isOpen={incomeModalOpen} 
        onClose={() => setIncomeModalOpen(false)} 
        type="Income"
        onSuccess={() => {
          fetchBalance();
          fetchTransactions();
        }}
      />
      <TransactionModal 
        isOpen={expenseModalOpen} 
        onClose={() => setExpenseModalOpen(false)} 
        type="Expense"
        onSuccess={() => {
          fetchBalance();
          fetchTransactions();
        }}
      />
    </div>
  );
} 