/**
 * Smooth scroll-linked gradient: blue emphasis at top → purple mid → fades with scroll.
 */
(function () {
  const root = document.querySelector(".landing-page");
  const ambient = document.querySelector(".landing-ambient");
  if (!root || !ambient) return;

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  let target = 0;
  let current = 0;
  let raf = 0;

  function measure() {
    const max = Math.max(
      1,
      document.documentElement.scrollHeight - window.innerHeight
    );
    target = Math.min(1, Math.max(0, window.scrollY / max));
  }

  function tick() {
    current += (target - current) * 0.08;
    if (Math.abs(target - current) < 0.0008) current = target;
    ambient.style.setProperty("--scroll", current.toFixed(4));
    if (Math.abs(target - current) > 0.0008) {
      raf = requestAnimationFrame(tick);
    } else {
      raf = 0;
    }
  }

  function onScroll() {
    measure();
    if (!raf) raf = requestAnimationFrame(tick);
  }

  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll, { passive: true });
  measure();
  ambient.style.setProperty("--scroll", "0");
})();
