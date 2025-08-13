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

  // Resume: collapse details when clicking bottom "Show less"
  document.querySelectorAll('.more-bullets .show-less').forEach((el) => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      const details = el.closest('details.more-bullets');
      if (details) details.open = false;
    });
  });
});
