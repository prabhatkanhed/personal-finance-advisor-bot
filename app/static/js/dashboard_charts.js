/**
 * Dashboard Chart.js Visualizations
 * Personal Finance Advisor Bot
 */

document.addEventListener('DOMContentLoaded', function () {
  // Common chart styling configuration
  const fontConfig = {
    family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    size: 12
  };

  // 1. Income vs Expense Bar Chart
  const incomeVsExpenseCanvas = document.getElementById('chartIncomeVsExpense');
  if (incomeVsExpenseCanvas) {
    const month = incomeVsExpenseCanvas.dataset.month || '';
    const year = incomeVsExpenseCanvas.dataset.year || '';
    
    fetch(`/api/charts/income-vs-expense?month=${month}&year=${year}`)
      .then(res => res.json())
      .then(data => {
        new Chart(incomeVsExpenseCanvas, {
          type: 'bar',
          data: {
            labels: data.labels,
            datasets: [{
              label: 'Amount ($)',
              data: data.data,
              backgroundColor: ['#10b981', '#ef4444', '#3b82f6'],
              borderRadius: 6,
              borderSkipped: false
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false },
              tooltip: {
                callbacks: {
                  label: function (ctx) {
                    return ` $${ctx.parsed.y.toLocaleString(undefined, { minimumFractionDigits: 2 })}`;
                  }
                }
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  callback: function (val) { return '$' + val.toLocaleString(); },
                  font: fontConfig
                },
                grid: { color: '#f1f5f9' }
              },
              x: {
                ticks: { font: fontConfig },
                grid: { display: false }
              }
            }
          }
        });
      })
      .catch(err => console.error("Error loading income vs expense chart:", err));
  }

  // 2. Monthly Spending Trends (Line Chart)
  const monthlyTrendsCanvas = document.getElementById('chartMonthlyTrends');
  if (monthlyTrendsCanvas) {
    fetch('/api/charts/monthly-trends')
      .then(res => res.json())
      .then(data => {
        new Chart(monthlyTrendsCanvas, {
          type: 'line',
          data: {
            labels: data.labels,
            datasets: [
              {
                label: 'Income',
                data: data.income,
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.35,
                fill: true,
                pointRadius: 4,
                pointHoverRadius: 6
              },
              {
                label: 'Expenses',
                data: data.expense,
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239, 68, 68, 0.08)',
                tension: 0.35,
                fill: true,
                pointRadius: 4,
                pointHoverRadius: 6
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'top',
                labels: { font: fontConfig }
              },
              tooltip: {
                callbacks: {
                  label: function (ctx) {
                    return ` ${ctx.dataset.label}: $${ctx.parsed.y.toLocaleString(undefined, { minimumFractionDigits: 2 })}`;
                  }
                }
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  callback: function (val) { return '$' + val.toLocaleString(); },
                  font: fontConfig
                },
                grid: { color: '#f1f5f9' }
              },
              x: {
                ticks: { font: fontConfig },
                grid: { display: false }
              }
            }
          }
        });
      })
      .catch(err => console.error("Error loading monthly trends chart:", err));
  }

  // 3. Category-wise Expense Distribution (Donut Chart)
  const categoryDistCanvas = document.getElementById('chartCategoryDistribution');
  if (categoryDistCanvas) {
    const month = categoryDistCanvas.dataset.month || '';
    const year = categoryDistCanvas.dataset.year || '';

    fetch(`/api/charts/category-distribution?month=${month}&year=${year}`)
      .then(res => res.json())
      .then(data => {
        new Chart(categoryDistCanvas, {
          type: 'doughnut',
          data: {
            labels: data.labels,
            datasets: [{
              data: data.data,
              backgroundColor: data.colors.length ? data.colors : ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#06b6d4'],
              borderWidth: 2,
              borderColor: '#ffffff'
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'bottom',
                labels: {
                  boxWidth: 12,
                  font: fontConfig
                }
              },
              tooltip: {
                callbacks: {
                  label: function (ctx) {
                    const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                    const pct = total > 0 ? ((ctx.parsed / total) * 100).toFixed(1) : 0;
                    return ` ${ctx.label}: $${ctx.parsed.toLocaleString(undefined, { minimumFractionDigits: 2 })} (${pct}%)`;
                  }
                }
              }
            },
            cutout: '68%'
          }
        });
      })
      .catch(err => console.error("Error loading category distribution chart:", err));
  }

  // 4. Savings Progress (Horizontal Bar Chart)
  const savingsProgressCanvas = document.getElementById('chartSavingsProgress');
  if (savingsProgressCanvas) {
    fetch('/api/charts/savings-progress')
      .then(res => res.json())
      .then(data => {
        new Chart(savingsProgressCanvas, {
          type: 'bar',
          data: {
            labels: data.labels,
            datasets: [
              {
                label: 'Current Saved',
                data: data.current,
                backgroundColor: '#4f46e5',
                borderRadius: 4
              },
              {
                label: 'Target Goal',
                data: data.target,
                backgroundColor: '#e2e8f0',
                borderRadius: 4
              }
            ]
          },
          options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'top',
                labels: { font: fontConfig }
              },
              tooltip: {
                callbacks: {
                  label: function (ctx) {
                    return ` ${ctx.dataset.label}: $${ctx.parsed.x.toLocaleString(undefined, { minimumFractionDigits: 2 })}`;
                  }
                }
              }
            },
            scales: {
              x: {
                beginAtZero: true,
                ticks: {
                  callback: function (val) { return '$' + val.toLocaleString(); },
                  font: fontConfig
                },
                grid: { color: '#f1f5f9' }
              },
              y: {
                ticks: { font: fontConfig },
                grid: { display: false }
              }
            }
          }
        });
      })
      .catch(err => console.error("Error loading savings progress chart:", err));
  }
});
