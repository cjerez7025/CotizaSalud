/* Animaciones del sitio (sin librerias). Respeta prefers-reduced-motion y no altera el texto: solo lo anima. */
(function () {
  'use strict';
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = window.matchMedia && window.matchMedia('(pointer:fine)').matches;
  var root = document.documentElement;
  function $(s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); }

  /* Cabecera que cambia, barra de progreso y brillo de scroll */
  var prog = document.getElementById('progress'), ticking = false;
  function onScroll() {
    var y = window.scrollY || 0, h = document.documentElement.scrollHeight - window.innerHeight;
    document.body.classList.toggle('scrolled', y > 24);
    if (prog) prog.style.width = (h > 0 ? (y / h) * 100 : 0) + '%';
    ticking = false;
  }
  window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();

  /* Contadores (el numero real queda en el HTML como respaldo) */
  function fmt(n) { return n.toLocaleString('es-CL'); }
  function runCount(el) {
    var to = parseFloat(el.getAttribute('data-count')), suf = el.getAttribute('data-suffix') || '';
    if (reduce || isNaN(to)) return;
    var t0 = null, dur = 1700;
    function step(t) {
      if (!t0) t0 = t;
      var p = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - p, 4);
      el.textContent = fmt(Math.round(to * e)) + suf;
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  if ('IntersectionObserver' in window) {
    var co = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { runCount(e.target); co.unobserve(e.target); } });
    }, { threshold: 0.6 });
    $('[data-count]').forEach(function (el) { co.observe(el); });
  }

  if (reduce) return;
  root.classList.add('motion');

  /* Titulares que aparecen palabra por palabra (el texto sigue en el HTML) */
  $('[data-words]').forEach(function (el) {
    var out = [], i = 0;
    Array.prototype.forEach.call(el.childNodes, function (n) {
      if (n.nodeType === 3) {
        n.textContent.trim().split(/\s+/).forEach(function (w) {
          if (w) out.push('<span class="w" style="--i:' + (i++) + '"><span>' + w + '</span></span>');
        });
      } else if (n.nodeType === 1) {
        n.textContent.trim().split(/\s+/).forEach(function (w) {
          var c = n.cloneNode(false); c.textContent = w;
          out.push('<span class="w" style="--i:' + (i++) + '"><span>' + c.outerHTML + '</span></span>');
        });
      }
    });
    el.setAttribute('aria-label', el.textContent.trim());
    el.innerHTML = out.join(' ');
    el.classList.add('split');
  });

  /* Aparicion al hacer scroll: se marcan automaticamente los bloques principales */
  var auto = '.sec-head,.plan-card,.stat,.step,.quote-card,.faq-item,.cta-section,.carousel,.big-feats li,.facts,.related-card,.prose>h2,.cta-band,.ph-price,.cmp-table,.hub-group>h2,.marquee';
  $(auto).forEach(function (el) {
    if (el.classList.contains('reveal') || el.closest('.reveal')) return;
    var sib = el.parentNode ? Array.prototype.indexOf.call(el.parentNode.children, el) : 0;
    el.setAttribute('data-rv', '');
    el.style.setProperty('--d', ((sib % 4) * 90) + 'ms');
  });
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        var el = e.target; io.unobserve(el); el.classList.add('in');
        /* al terminar, se quita el atributo para que el hover y la inclinacion usen sus propias transiciones */
        setTimeout(function () { el.removeAttribute('data-rv'); el.classList.remove('in'); el.style.removeProperty('--d'); }, 1300);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -5% 0px' });
    $('[data-rv]').forEach(function (el) { io.observe(el); });
  } else { $('[data-rv]').forEach(function (el) { el.removeAttribute('data-rv'); }); }

  /* Inclinacion 3D con foco de luz y botones magneticos */
  if (fine) {
    $('.plan-card,.related-card,.stat,.facts').forEach(function (el) {
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
        el.style.transform = 'perspective(900px) rotateX(' + (-y * 6).toFixed(2) + 'deg) rotateY(' + (x * 8).toFixed(2) + 'deg) translateY(-5px)';
        el.style.setProperty('--mx', (x + 0.5) * 100 + '%'); el.style.setProperty('--my', (y + 0.5) * 100 + '%');
      });
      el.addEventListener('pointerleave', function () { el.style.transform = ''; });
    });
    $('.hero-ctas .btn,.ph-ctas .btn,.cta-band .btn').forEach(function (el) {
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect();
        el.style.transform = 'translate(' + ((e.clientX - r.left - r.width / 2) * 0.2).toFixed(1) + 'px,' + ((e.clientY - r.top - r.height / 2) * 0.28).toFixed(1) + 'px)';
      });
      el.addEventListener('pointerleave', function () { el.style.transform = ''; });
    });
  }

  /* Cinta de tipos de seguro: se duplica para el bucle infinito */
  $('.marquee .track').forEach(function (t) { t.innerHTML += t.innerHTML; });
})();
