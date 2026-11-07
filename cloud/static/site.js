/* svgslid.es — CTA attribution + analytics events.
 *
 * 1. Every "Add to Chrome" link carries data-cta="<position>" and static UTMs
 *    (utm_source=svgslid.es, utm_medium=web, utm_campaign=<page>, utm_content=<position>).
 *    If the visitor arrived with their own UTMs (e.g. an ad), those are passed through
 *    to the Chrome Web Store instead, so the install is credited to the original source
 *    in the Web Store's Analytics property.
 * 2. Clicks fire a `cws_click` event to the dataLayer (GTM) and to GA4 via gtag.
 */
(function () {
  var here = new URLSearchParams(location.search);
  var page = location.pathname.replace(/^\/|\/$/g, '') || 'home';
  var inbound = here.get('utm_source') && here.get('utm_campaign');

  document.querySelectorAll('a[data-cta]').forEach(function (a) {
    if (!inbound) return;
    try {
      var u = new URL(a.href);
      ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term'].forEach(function (k) {
        if (here.get(k)) u.searchParams.set(k, here.get(k));
      });
      u.searchParams.set('utm_content', page + '-' + a.dataset.cta);
      a.href = u.toString();
    } catch (e) {}
  });

  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[data-cta]');
    if (!a) return;
    var params = { cta_position: a.dataset.cta, cta_page: page, link_url: a.href };
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push(Object.assign({ event: 'cws_click' }, params));
    if (typeof window.gtag === 'function') {
      window.gtag('event', 'cws_click', Object.assign({ transport_type: 'beacon' }, params));
    }
  }, true);
})();
