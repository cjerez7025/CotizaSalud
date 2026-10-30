/* Medicion de conversiones (Google Analytics 4).
 * Envia eventos solo si gtag esta cargado; si el visitante bloquea Analytics, no pasa nada.
 * Eventos: whatsapp_click, phone_click, cta_click. El envio de formularios (generate_lead)
 * se dispara desde el codigo del formulario en index_13.html. No se envian datos personales.
 * Los clics en WhatsApp y telefono tambien se envian a Google Ads como conversiones
 * secundarias (no influyen en la optimizacion de las campanas).
 */
(function () {
  var ADS_CONVERSIONS = {
    whatsapp_click: 'AW-18535491182/bSC5CPaA-a4dEO7MtIZF',
    phone_click: 'AW-18535491182/5_PjCPmA-a4dEO7MtIZF'
  };

  function send(name, params) {
    try {
      if (typeof window.gtag === 'function') {
        window.gtag('event', name, params || {});
        if (ADS_CONVERSIONS[name]) window.gtag('event', 'conversion', { send_to: ADS_CONVERSIONS[name] });
      }
    } catch (e) { /* la medicion nunca debe romper el sitio */ }
  }

  function where(el) {
    if (el.closest('.wsp-float')) return 'boton_flotante';
    var s = el.closest('#welcomeModal, header, footer, section, .mobile-menu, .cta-band, .facts');
    if (!s) return 'pagina';
    if (s.id) return s.id;
    return s.tagName === 'SECTION' ? (s.className || 'seccion').split(' ')[0] : s.tagName.toLowerCase();
  }

  document.addEventListener('click', function (ev) {
    var el = ev.target && ev.target.closest ? ev.target.closest('a,button') : null;
    if (!el) return;
    var href = el.getAttribute('href') || '';
    var loc = where(el);
    if (el.classList.contains('js-wsp-link') || href.indexOf('wa.me') !== -1) {
      send('whatsapp_click', { link_location: loc });
    } else if (href.indexOf('tel:') === 0 || el.classList.contains('js-phone-tel')) {
      send('phone_click', { link_location: loc });
    } else if (el.classList.contains('btn') && (href === '#contacto' || href === '/#contacto')) {
      send('cta_click', {
        link_text: (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 60),
        link_location: loc
      });
    }
  }, true);
})();
