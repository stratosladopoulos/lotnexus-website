/* Progressive enhancement: the content and resource accordions work without JS. */
(() => {
  'use strict';
  document.documentElement.classList.add('js');
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.getElementById('primary-links');
  const closeMenu = () => {
    if (!toggle || !nav) return;
    nav.classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', document.documentElement.lang === 'el' ? 'Άνοιγμα πλοήγησης' : 'Open navigation');
  };
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', document.documentElement.lang === 'el'
        ? (open ? 'Κλείσιμο πλοήγησης' : 'Άνοιγμα πλοήγησης')
        : (open ? 'Close navigation' : 'Open navigation'));
    });
    nav.addEventListener('click', event => {
      if (event.target.closest('a')) closeMenu();
    });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && nav.classList.contains('open')) {
        closeMenu();
        toggle.focus();
      }
    });
    document.addEventListener('click', event => {
      if (!event.target.closest('.nav-row')) closeMenu();
    });
    const desktop = window.matchMedia('(min-width: 801px)');
    if (desktop.addEventListener) desktop.addEventListener('change', closeMenu);
  }
  // Open the matching documentation roadmap card when its sidebar link is used.
  const openResource = hash => {
    if (!hash || !hash.startsWith('#')) return;
    const target = document.getElementById(hash.slice(1));
    if (target && target.tagName === 'DETAILS') target.open = true;
  };
  document.querySelectorAll('.docs-side a').forEach(link => {
    link.addEventListener('click', () => openResource(link.hash));
  });
  window.addEventListener('hashchange', () => openResource(window.location.hash));
  openResource(window.location.hash);
  // Indicate the visible main section without making navigation depend on JS.
  if ('IntersectionObserver' in window && nav) {
    const links = Array.from(nav.querySelectorAll('a[href^="#"]'));
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        links.forEach(link => {
          const current = link.hash === '#' + entry.target.id;
          link.classList.toggle('active', current);
          if (current) link.setAttribute('aria-current', 'location');
          else link.removeAttribute('aria-current');
        });
      });
    }, { rootMargin: '-15% 0px -55% 0px', threshold: 0 });
    links.forEach(link => {
      const section = document.getElementById(link.hash.slice(1));
      if (section) observer.observe(section);
    });
  }
})();
