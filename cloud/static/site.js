/* svgslid.es: CTA attribution, campaign banner, analytics events.
 * 1. Every "Add to Chrome" link carries data-cta="<position>" and static UTMs.
 *    Inbound UTMs (e.g. from an ad) persist for the browser session (sessionStorage, no cookie)
 *    and pass through to the Chrome Web Store.
 * 2. Campaign banner: shown only to visitors whose utm_campaign is listed in CAMPAIGNS. Dismissible.
 * 3. Clicks fire `cws_click` (dataLayer + gtag). Banner links also fire `banner_click`.
 */
(function () {
  var KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term'];
  var here = new URLSearchParams(location.search);
  var page = location.pathname.replace(/^\/|\/$/g, '') || 'home';

  var CAMPAIGNS = {
    'slides-13': {
      text: 'New in SVG to Slides 1.3: draw with a pen, mask images with any shape and combine shapes inside Google Slides™. Free.',
      cta: 'See what’s new',
      href: '/whats-new'
    }
  };

  var saved = {};
  try { saved = JSON.parse(sessionStorage.getItem('svgs_utm') || '{}') || {}; } catch (e) {}
  if (here.get('utm_source') && here.get('utm_campaign')) {
    saved = {};
    KEYS.forEach(function (k) { if (here.get(k)) saved[k] = here.get(k); });
    try { sessionStorage.setItem('svgs_utm', JSON.stringify(saved)); } catch (e) {}
  }
  var inbound = saved.utm_source && saved.utm_campaign;

  function track(name, params) {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push(Object.assign({ event: name }, params));
    if (typeof window.gtag === 'function') {
      window.gtag('event', name, Object.assign({ transport_type: 'beacon' }, params));
    }
  }

  function banner() {
    var c = inbound && CAMPAIGNS[saved.utm_campaign];
    if (!c || !document.body) return;
    try { if (sessionStorage.getItem('svgs_banner_off')) return; } catch (e) {}
    var onNews = page === 'whats-new';
    var nav = document.querySelector('a[data-cta="nav"]');
    var href = onNews && nav ? nav.href : c.href;
    var label = onNews ? 'Add to Chrome, free' : c.cta;

    var css = document.createElement('style');
    css.textContent =
      '.svgs-bn{position:relative;display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:8px 16px;padding:10px 48px 10px 16px;background:#0A56CF;color:#fff;font:600 15px/1.4 var(--display,system-ui,sans-serif);text-align:center}' +
      '.svgs-bn a{background:#fff;color:#0A56CF;border-radius:999px;padding:6px 14px;font-weight:800;text-decoration:none;white-space:nowrap}' +
      '.svgs-bn a:focus-visible,.svgs-bn button:focus-visible{outline:2px solid #fff;outline-offset:2px}' +
      '.svgs-bn button{position:absolute;right:10px;top:50%;transform:translateY(-50%);width:32px;height:32px;border:0;border-radius:50%;background:transparent;color:#fff;font:400 22px/1 system-ui,sans-serif;cursor:pointer}' +
      '.svgs-bn button:hover{background:rgba(255,255,255,.18)}';
    document.head.appendChild(css);

    var el = document.createElement('div');
    el.className = 'svgs-bn';
    el.setAttribute('role', 'region');
    el.setAttribute('aria-label', 'Announcement');
    var msg = document.createElement('span');
    msg.textContent = c.text;
    var a = document.createElement('a');
    a.href = href;
    a.textContent = label;
    if (onNews) a.setAttribute('data-cta', 'banner');
    var x = document.createElement('button');
    x.type = 'button';
    x.setAttribute('aria-label', 'Dismiss');
    x.textContent = '×';
    x.addEventListener('click', function () {
      try { sessionStorage.setItem('svgs_banner_off', '1'); } catch (e) {}
      el.remove();
    });
    a.addEventListener('click', function () { track('banner_click', { campaign: saved.utm_campaign, cta_page: page }); });
    el.appendChild(msg); el.appendChild(a); el.appendChild(x);
    document.body.insertBefore(el, document.body.firstChild);
  }

  banner();

  document.querySelectorAll('a[data-cta]').forEach(function (a) {
    if (!inbound) return;
    try {
      var u = new URL(a.href);
      KEYS.forEach(function (k) { if (saved[k]) u.searchParams.set(k, saved[k]); });
      u.searchParams.set('utm_content', page + '-' + a.dataset.cta);
      a.href = u.toString();
    } catch (e) {}
  });

  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[data-cta]');
    if (!a) return;
    track('cws_click', { cta_position: a.dataset.cta, cta_page: page, link_url: a.href });
  }, true);
})();
