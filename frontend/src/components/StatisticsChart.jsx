import React, { useState, useEffect, useCallback } from 'react';
import { Bar } from 'react-chartjs-2';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function StatisticsChart({ statisticsTrigger = 0 }) {
  const [tab, setTab] = useState('Income'); // 'Income' or 'Expenses'
  const [year, setYear] = useState(new Date().getFullYear());
  const [range, setRange] = useState('Month'); // 'Month', 'Quarter', 'Year'
  const [chartData, setChartData] = useState({ labels: [], income: [], expenses: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStatistics = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_URL}/financials/statistics/`, {
        params: { year, range },
      });
      setChartData(response.data);
    } catch (err) {
      console.error('Error fetching statistics:', err);
      setError('Error fetching statistics. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [year, range, statisticsTrigger]);

  useEffect(() => {
    fetchStatistics();
  }, [fetchStatistics]);

  const data = {
    labels: chartData.labels,
    datasets: [
      {
        label: tab === 'Income' ? 'Income' : 'Expenses',
        data: tab === 'Income' ? chartData.income : chartData.expenses,
        backgroundColor: tab === 'Income' ? '#22C55E' : '#DC2626', // Updated to #DC2626 for expenses
        borderColor: tab === 'Income' ? '#16A34A' : '#DC2626',     // Updated to #DC2626 for expenses
        borderWidth: 1, // Changed back to 1 for bars
        // Removed fill and tension properties for line chart
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { display: false },
      title: {
        display: true,
        text: `${tab} Statistics for ${year} (${range})`,
        font: { size: 16, weight: 'bold' },
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            if (context.parsed.y !== null) {
              label += `₱${parseFloat(context.parsed.y).toLocaleString()}`;
            }
            return label;
          }
        }
      }
    },
    scales: {
      x: {
        grid: { display: false },
        title: { display: true, text: range === 'Month' ? 'Month' : range === 'Quarter' ? 'Quarter' : 'Year' }
      },
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value) {
            return `₱${parseFloat(value).toLocaleString()}`;
          }
        },
        title: { display: true, text: 'Amount (₱)' }
      },
    },
  };

  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 5 }, (_, i) => currentYear - i); // Last 5 years

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full min-h-[300px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
        <p className="ml-4 text-gray-600">Loading statistics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-500 text-center p-4">
        {error}
        <button 
          onClick={fetchStatistics}
          className="ml-4 px-4 py-2 bg-red-100 text-red-600 rounded-lg hover:bg-red-200"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6 w-full h-full flex flex-col">
      <div className="flex justify-between items-center mb-4">
        <div className="flex gap-4">
          <button
            className={`px-4 py-2 rounded-full font-medium ${tab === 'Income' ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-700'}`}
            onClick={() => setTab('Income')}
          >
            Income
          </button>
          <button
            className={`px-4 py-2 rounded-full font-medium ${tab === 'Expenses' ? 'bg-red-500 text-white' : 'bg-gray-200 text-gray-700'}`}
            onClick={() => setTab('Expenses')}
          >
            Expenses
          </button>
        </div>
        <div className="flex gap-2 items-center">
          <select
            value={year}
            onChange={(e) => setYear(parseInt(e.target.value))}
            className="px-3 py-1 border border-gray-300 rounded-full text-sm focus:outline-none"
          >
            {years.map(y => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
          <select
            value={range}
            onChange={(e) => setRange(e.target.value)}
            className="px-3 py-1 border border-gray-300 rounded-full text-sm focus:outline-none"
          >
            <option value="Month">Monthly</option>
            <option value="Quarter">Quarterly</option>
            <option value="Year">Yearly</option>
          </select>
        </div>
      </div>
      <div className="flex-1">
        <Bar data={data} options={options} />
      </div>
    </div>
  );
} 