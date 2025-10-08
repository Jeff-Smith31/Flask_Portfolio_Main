document.addEventListener('DOMContentLoaded', () => {
  // Year in footer
  const y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();

  // Simple mobile nav toggle
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.nav');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const visible = nav.style.display === 'flex';
      nav.style.display = visible ? 'none' : 'flex';
      nav.style.flexDirection = visible ? '' : 'column';
      nav.style.gap = visible ? '' : '12px';
    });
  }

  // PWA install prompt handling
  let deferredPrompt;
  const installBtn = document.getElementById('install-btn');
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    if (installBtn) installBtn.style.display = 'inline-block';
  });
  if (installBtn) {
    installBtn.addEventListener('click', async () => {
      if (!deferredPrompt) return;
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      if (outcome === 'accepted') {
        installBtn.style.display = 'none';
      }
      deferredPrompt = null;
    });
  }
  window.addEventListener('appinstalled', () => {
    if (installBtn) installBtn.style.display = 'none';
    deferredPrompt = null;
  });

  // Resume: collapse details when clicking bottom "Show less"
  document.querySelectorAll('.more-bullets .show-less').forEach((el) => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      const details = el.closest('details.more-bullets');
      if (details) details.open = false;
    });
  });
});
