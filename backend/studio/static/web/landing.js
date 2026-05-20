/**
 * Scroll-linked fade + gentle phase drift for hero color field.
 */
(function () {
  const ambient = document.querySelector(".landing-ambient");
  const hero = document.querySelector(".landing-hero");
  if (!ambient) return;

  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  let scrollTarget = 0;
  let scrollCurrent = 0;
  let scrollRaf = 0;
  let timeRaf = 0;
  const start = performance.now();

  function measureScroll() {
    const max = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
    scrollTarget = Math.min(1, Math.max(0, window.scrollY / max));
  }

  function tickScroll() {
    scrollCurrent += (scrollTarget - scrollCurrent) * 0.07;
    if (Math.abs(scrollTarget - scrollCurrent) < 0.0006) scrollCurrent = scrollTarget;
    ambient.style.setProperty("--scroll", scrollCurrent.toFixed(4));
    if (Math.abs(scrollTarget - scrollCurrent) > 0.0006) {
      scrollRaf = requestAnimationFrame(tickScroll);
    } else {
      scrollRaf = 0;
    }
  }

  function onScroll() {
    measureScroll();
    if (!scrollRaf) scrollRaf = requestAnimationFrame(tickScroll);
  }

  function tickTime(now) {
    if (!reduced && hero) {
      const t = (now - start) * 0.001;
      const phase = (Math.sin(t * 0.35) + 1) * 0.5;
      const phase2 = (Math.sin(t * 0.22 + 1.2) + 1) * 0.5;
      hero.style.setProperty("--wave-a", phase.toFixed(4));
      hero.style.setProperty("--wave-b", phase2.toFixed(4));
    }
    timeRaf = requestAnimationFrame(tickTime);
  }

  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll, { passive: true });
  measureScroll();
  ambient.style.setProperty("--scroll", "0");
  if (!reduced) timeRaf = requestAnimationFrame(tickTime);
})();
