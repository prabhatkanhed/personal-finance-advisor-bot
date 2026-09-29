/**
 * Main application client-side scripts
 * Personal Finance Advisor Bot
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Initialize Bootstrap Toasts
  const toastElList = [].slice.call(document.querySelectorAll('.toast'));
  toastElList.map(function (toastEl) {
    const toast = new bootstrap.Toast(toastEl, { delay: 4500 });
    toast.show();
  });

  // 2. Responsive Sidebar Toggle for mobile devices
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', function () {
      sidebar.classList.toggle('show');
    });
  }

  // 3. AI Advisor Loading Overlay triggers
  const aiForms = document.querySelectorAll('.ai-trigger-form');
  const loadingOverlay = document.getElementById('ai-loading-overlay');
  if (aiForms.length && loadingOverlay) {
    aiForms.forEach(form => {
      form.addEventListener('submit', function () {
        loadingOverlay.style.display = 'flex';
      });
    });
  }

  // 4. Auto-hide alerts after 5 seconds if not dismissed
  setTimeout(function () {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
      const bsAlert = bootstrap.Alert.getInstance(alert);
      if (bsAlert) {
        bsAlert.close();
      }
    });
  }, 5000);
});
