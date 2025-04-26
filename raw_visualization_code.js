const FinancialDashboard = () => {
  const { useState } = React;
  const [activeTab, setActiveTab] = useState('overview');
  
  // Format currency values
  const formatCurrency = (value) => {
    if (value === null || value === undefined) return 'N/A';
    return `$${value.toFixed(2)}M`;
  };
  
  // Format percentage values
  const formatPercent = (value) => {
    if (value === null || value === undefined) return 'N/A';
    return `${(value * 100).toFixed(1)}%`;
  };
  
  // Financial data from the analysis
  const financialData = [
    {
      report_date: "2018-08-06",
      fiscal_year: 2019,
      fiscal_quarter: 3,
      ticker: "BIDW",
      company_name: "Company BIDW",
      revenue_m: 2686.18,
      gross_profit_m: 1400.88,
      operating_income_m: 273.77,
      net_income_m: 547.93,
      eps: 0.77,
      cash_and_equivalents_m: 638.66,
      total_assets_m: 16114.19,
      total_liabilities_m: 9488.32,
      equity_m: 6625.87,
      gross_margin: 0.52,
      operating_margin: 0.1,
      net_margin: 0.2,
      debt_to_equity: 1.43
    },
    {
      report_date: "2019-05-08",
      fiscal_year: 2019,
      fiscal_quarter: 2,
      ticker: "BIDW",
      company_name: "Company BIDW",
      revenue_m: 2853.47,
      gross_profit_m: 1639.62,
      operating_income_m: 288.57,
      net_income_m: 348.53,
      eps: 1.36,
      cash_and_equivalents_m: 629.27,
      total_assets_m: 8260.67,
      total_liabilities_m: 9349.3,
      equity_m: -1088.63,
      gross_margin: 0.57,
      operating_margin: 0.1,
      net_margin: 0.12,
      debt_to_equity: -8.59
    },
    {
      report_date: "2020-04-16",
      fiscal_year: 2020,
      fiscal_quarter: 3,
      ticker: "BIDW",
      company_name: "Company BIDW",
      revenue_m: 2155.77,
      gross_profit_m: 955.15,
      operating_income_m: 735.06,
      net_income_m: 507.57,
      eps: 0.9,
      cash_and_equivalents_m: 703.21,
      total_assets_m: 5466.8,
      total_liabilities_m: 4677.02,
      equity_m: 789.78,
      gross_margin: 0.44,
      operating_margin: 0.34,
      net_margin: 0.24,
      debt_to_equity: 5.92
    }
  ];
  
  // Sort data chronologically
  const sortedData = [...financialData].sort((a, b) => 
    new Date(a.report_date) - new Date(b.report_date)
  );
  
  // Key insights from the analysis
  const keyInsights = [
    "Revenue declined by 20% from Q3 2019 to Q3 2020, indicating potential business challenges.",
    "Operating income increased significantly from $273.8M to $735.1M, suggesting successful cost-cutting measures.",
    "Gross margin decreased from 52% to 44%, indicating potential pricing pressure.",
    "Operating margin improved dramatically from 10% to 34%, showing strong operational efficiency gains.",
    "Cash position improved from $638.7M to $703.2M, strengthening liquidity despite revenue challenges.",
    "Total assets decreased significantly from $16.1B to $5.5B, suggesting major divestments.",
    "The company had negative equity in Q2 2019, but this was corrected by Q3 2020.",
    "EPS increased from $0.77 to $0.90 despite revenue decline, likely due to improved efficiency."
  ];
  
  // Calculated metrics
  const calculatedMetrics = {
    average_eps: 0.9,
    average_gross_margin: 0.51,
    average_operating_margin: 0.18,
    average_net_margin: 0.19,
    cash_growth_rate: 0.1,
    revenue_growth_rate_2019_2020: -0.2,
    current_ratio_latest: 1.17,
    quick_ratio_latest: 0.15
  };
  
  // Custom tooltip for charts
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-4 border border-gray-300 rounded shadow-md">
          <p className="font-semibold">{`Period: ${label}`}</p>
          {payload.map((entry, index) => (
            <p key={`item-${index}`} style={{ color: entry.color }}>
              {`${entry.name}: ${entry.value !== null && entry.value !== undefined 
                ? entry.unit === '$' 
                  ? formatCurrency(entry.value) 
                  : entry.unit === '%' 
                    ? formatPercent(entry.value) 
                    : entry.value
                : 'N/A'}`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };
  
  // Format date for display
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return `${date.getFullYear()} Q${date.getMonth() >= 0 && date.getMonth() <= 2 ? 1 : 
                                     date.getMonth() >= 3 && date.getMonth() <= 5 ? 2 :
                                     date.getMonth() >= 6 && date.getMonth() <= 8 ? 3 : 4}`;
  };
  
  // Prepare data for charts with formatted dates
  const chartData = sortedData.map(item => ({
    ...item,
    period: `${item.fiscal_year} Q${item.fiscal_quarter}`,
    formattedDate: formatDate(item.report_date)
  }));
  
  return (
    <div className="bg-gray-50 p-6 rounded-lg shadow-lg">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Company BIDW Financial Dashboard</h1>
        <p className="text-gray-600">Comprehensive financial analysis and visualization</p>
      </div>
      
      {/* Tab Navigation */}
      <div className="mb-6 border-b border-gray-200">
        <nav className="flex space-x-4">
          <button
            onClick={() => setActiveTab('overview')}
            className={`py-2 px-4 font-medium rounded-t-lg ${
              activeTab === 'overview'
                ? 'bg-blue-600 text-white'
                : 'text-gray-600 hover:text-blue-600'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('revenue')}
            className={`py-2 px-4 font-medium rounded-t-lg ${
              activeTab === 'revenue'
                ? 'bg-blue-600 text-white'
                : 'text-gray-600 hover:text-blue-600'
            }`}
          >
            Revenue & Profitability
          </button>
          <button
            onClick={() => setActiveTab('balance')}
            className={`py-2 px-4 font-medium rounded-t-lg ${
              activeTab === 'balance'
                ? 'bg-blue-600 text-white'
                : 'text-gray-600 hover:text-blue-600'
            }`}
          >
            Balance Sheet
          </button>
          <button
            onClick={() => setActiveTab('margins')}
            className={`py-2 px-4 font-medium rounded-t-lg ${
              activeTab === 'margins'
                ? 'bg-blue-600 text-white'
                : 'text-gray-600 hover:text-blue-600'
            }`}
          >
            Margins & Efficiency
          </button>
          <button
            onClick={() => setActiveTab('eps')}
            className={`py-2 px-4 font-medium rounded-t-lg ${
              activeTab === 'eps'
                ? 'bg-blue-600 text-white'
                : 'text-gray-600 hover:text-blue-600'
            }`}
          >
            EPS & Valuation
          </button>
        </nav>
      </div>
      
      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-bold text-gray-800 mb-4">Key Financial Insights</h2>
              <ul className="list-disc pl-5 space-y-2">
                {keyInsights.map((insight, index) => (
                  <li key={index} className="text-gray-700">{insight}</li>
                ))}
              </ul>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-bold text-gray-800 mb-4">Key Performance Indicators</h2>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 p-4 rounded">
                  <p className="text-sm text-gray-500">Average EPS</p>
                  <p className="text-2xl font-bold text-blue-600">${calculatedMetrics.average_eps.toFixed(2)}</p>
                </div>
                <div className="bg-gray-50 p-4 rounded">
                  <p className="text-sm text-gray-500">Avg. Gross Margin</p>
                  <p className="text-2xl font-bold text-blue-600">{formatPercent(calculatedMetrics.average_gross_margin)}</p>
                </div>
                <div className="bg-gray-50 p-4 rounded">
                  <p className="text-sm text-gray-500">Revenue Growth (2019-2020)</p>
                  <p className="text-2xl font-bold text-red-600">{formatPercent(calculatedMetrics.revenue_growth_rate_2019_2020)}</p>
                </div>
                <div className="bg-gray-50 p-4 rounded">
                  <p className="text-sm text-gray-500">Cash Growth Rate</p>
                  <p className="text-2xl font-bold text-green-600">{formatPercent(calculatedMetrics.cash_growth_rate)}</p>
                </div>
                <div className="bg-gray-50 p-4 rounded">
                  <p className="text-sm text-gray-500">Current Ratio</p>
                  <p className="text-2xl font-bold text-blue-600">{calculatedMetrics.current_ratio_latest.toFixed(2)}</p>
                </div>
                <div className="bg-gray-50 p-4 rounded">
                  <p className="text-sm text-gray-500">Quick Ratio</p>
                  <p className="text-2xl font-bold text-blue-600">{calculatedMetrics.quick_ratio_latest.toFixed(2)}</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow mb-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Revenue vs. Profitability Trend</h2>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="period" />
                  <YAxis yAxisId="left" orientation="left" stroke="#8884d8" />
                  <YAxis yAxisId="right" orientation="right" stroke="#82ca9d" />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                  <Line yAxisId="left" type="monotone" dataKey="revenue_m" name="Revenue" stroke="#8884d8" unit="$" />
                  <Line yAxisId="right" type="monotone" dataKey="net_income_m" name="Net Income" stroke="#82ca9d" unit="$" />
                  <ReferenceLine y={0} stroke="red" strokeDasharray="3 3" />
                  <Brush dataKey="period" height={30} stroke="#8884d8" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Financial Health Radar</h2>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart outerRadius={150} data={[
                  {
                    subject: 'Gross Margin',
                    A: calculatedMetrics.average_gross_margin,
                    fullMark: 1,
                  },
                  {
                    subject: 'Operating Margin',
                    A: calculatedMetrics.average_operating_margin,
                    fullMark: 1,
                  },
                  {
                    subject: 'Net Margin',
                    A: calculatedMetrics.average_net_margin,
                    fullMark: 1,
                  },
                  {
                    subject: 'Current Ratio',
                    A: calculatedMetrics.current_ratio_latest / 3, // Normalized for scale
                    fullMark: 1,
                  },
                  {
                    subject: 'Cash Growth',
                    A: calculatedMetrics.cash_growth_rate + 0.5, // Adjusted to 0-1 scale
                    fullMark: 1,
                  },
                ]}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="subject" />
                  <PolarRadiusAxis angle={30} domain={[0, 1]} />
                  <Radar name="Company BIDW" dataKey="A" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                  <Legend />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}
      
      {/* Revenue & Profitability Tab */}
      {activeTab === 'revenue' && (
        <div>
          <div className="bg-white p-6 rounded-lg shadow mb-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Revenue & Profit Metrics</h2>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="period" />
                  <YAxis />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                  <Bar dataKey="revenue_m" name="Revenue" fill="#8884d8" unit="$" />
                  <Bar dataKey="gross_profit_m" name="Gross Profit" fill="#82ca9d" unit="$" />
                  <Bar dataKey="operating_income_m" name="Operating Income" fill="#ffc658" unit="$" />
                  <Bar dataKey="net_income_m" name="Net Income" fill="#ff8042" unit="$" />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <p className="text-blue-800">
                <span className="font-bold">Key Insight:</span> Despite a 20% revenue decline from Q3 2019 to Q3 2020, 
                operating income increased significantly from $273.8M to $735.1M, suggesting successful cost-cutting 
                measures and operational efficiency improvements.
              </p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-bold text-gray-800 mb-4">Revenue Trend</h2>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period" />
                    <YAxis />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend />
                    <Line type="monotone" dataKey="revenue_m" name="Revenue" stroke="#8884d8" unit="$" />
                    <ReferenceLine
                      x="2020 Q3"
                      stroke="red"
                      label={{ value: "20% Decline", position: "top", fill: "red" }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-bold text-gray-800 mb-4">Profit Components</h2>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period" />
                    <YAxis />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend />
                    <Area type="monotone" dataKey="gross_profit_m" name="Gross Profit" stackId="1" fill="#8884d8" stroke="#8884d8" unit="$" />
                    <Area type="monotone" dataKey="operating_income_m" name="Operating Income" stackId="2" fill="#82ca9d" stroke="#82ca9d" unit="$" />
                    <Area type="monotone" dataKey="net_income_m" name="Net Income" stackId="3" fill="#ffc658" stroke="#ffc658" unit="$" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Balance Sheet Tab */}
      {activeTab === 'balance' && (
        <div>
          <div className="bg-white p-6 rounded-lg shadow mb-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Balance Sheet Composition</h2>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="period" />
                  <YAxis />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                  <Area type="monotone" dataKey="total_assets_m" name="Total Assets" stackId="1" fill="#8884d8" stroke="#8884d8" unit="$" />
                  <Area type="monotone" dataKey="total_liabilities_m" name="Total Liabilities" stackId="2" fill="#82ca9d" stroke="#82ca9d" unit="$" />
                  <Area type="monotone" dataKey="equity_m" name="Equity" stackId="3" fill="#ffc658" stroke="#ffc658" unit="$" />
                  <ReferenceLine y={0} stroke="red" strokeDasharray="3 3" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-4 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
              <p className="text-yellow-800">
                <span className="font-bold">Key Insight:</span> Total assets decreased significantly from $16.1B in Q3 2019 to $5.5B in Q3 2020, 
                suggesting major divestments or write-downs. The company had negative equity in Q2 2019, indicating a concerning financial position 
                where liabilities exceeded assets, but this was corrected by Q3 2020.
              </p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-bold text-gray-800 mb-4">Cash Position</h2>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period" />
                    <YAxis />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend />
                    <Line type="monotone" dataKey="cash_and_equivalents_m" name="Cash & Equivalents" stroke="#8884d8" unit="$" />
                    <ReferenceLine
                      y={700}
                      label={{ value: "Target Cash Level", position: "right" }}
                      stroke="green"
                      strokeDasharray="3 3"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-bold text-gray-800 mb-4">Debt to Equity Ratio</h2>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period" />
                    <YAxis />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend />
                    <Bar dataKey="debt_to_equity" name="Debt to Equity" fill="#8884d8" />
                    <ReferenceLine y={0} stroke="red" strokeDasharray="3 3" />
                    <ReferenceLine
                      y={2}
                      label={{ value: "Industry Avg", position: "right" }}
                      stroke="blue"
                      strokeDasharray="3 3"
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Margins & Efficiency Tab */}
      {activeTab === 'margins' && (
        <div>
          <div className="bg-white p-6 rounded-lg shadow mb-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Profitability Margins</h2>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="period" />
                  <YAxis tickFormatter={(value) => `${(value * 100).toFixed(0)}%`} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                  <Line type="monotone" dataKey="gross_margin" name="Gross Margin" stroke="#8884d8" unit="%" />
                  <Line type="monotone" dataKey="operating_margin" name="Operating Margin" stroke="#82ca9d" unit="%" />
                  <Line type="monotone" dataKey="net_margin" name="Net Margin" stroke="#ffc658" unit="%" />
                  <ReferenceLine
                    y={0.3}
                    label={{ value: "Target Operating Margin", position: "right" }}
                    stroke="green"
                    strokeDasharray="3 3"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-4 p-4 bg-green-50 rounded-lg border border-green-200">
              <p className="text-green-800">
                <span className="font-bold">Key Insight:</span> Operating margin improved dramatically from 10% to 34% between Q3 2019 and Q3 2020, 
                showing strong operational efficiency gains. However, gross margin decreased from 52% to 44%, indicating potential pricing pressure 
                or increased cost of goods sold.
              </p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-bold text-gray-800 mb-4">Margin Comparison</h2>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period" />
                    <YAxis tickFormatter={(value) => `${(value * 100).toFixed(0)}%`} />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend />
                    <Bar dataKey="gross_margin" name="Gross Margin" fill="#8884d8" unit="%" />
                    <Bar dataKey="operating_margin" name="Operating Margin" fill="#82ca9d" unit="%" />
                    <Bar dataKey="net_margin" name="Net Margin" fill="#ffc658" unit="%" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-bold text-gray-800 mb-4">Efficiency Metrics</h2>
              <div className="p-4 bg-gray-50 rounded-lg mb-4">
                <h3 className="text-lg font-semibold text-gray-700 mb-2">Average Margins</h3>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Gross Margin</p>
                    <p className="text-xl font-bold text-blue-600">{formatPercent(calculatedMetrics.average_gross_margin)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Operating Margin</p>
                    <p className="text-xl font-bold text-blue-600">{formatPercent(calculatedMetrics.average_operating_margin)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Net Margin</p>
                    <p className="text-xl font-bold text-blue-600">{formatPercent(calculatedMetrics.average_net_margin)}</p>
                  </div>
                </div>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <h3 className="text-lg font-semibold text-gray-700 mb-2">Liquidity Ratios</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Current Ratio</p>
                    <p className="text-xl font-bold text-blue-600">{calculatedMetrics.current_ratio_latest.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Quick Ratio</p>
                    <p className="text-xl font-bold text-blue-600">{calculatedMetrics.quick_ratio_latest.toFixed(2)}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* EPS & Valuation Tab */}
      {activeTab === 'eps' && (
        <div>
          <div className="bg-white p-6 rounded-lg shadow mb-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">EPS vs Revenue Trend</h2>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="period" />
                  