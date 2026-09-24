document.querySelectorAll('.sponsor-comparison').forEach((comparison) => {
  const table = comparison.querySelector('table');
  const tiers = table.querySelector('thead');
  const sections = [...table.querySelectorAll('.sponsor-comparison-section')];
  // A viewport overlay keeps page scrolling sticky even when the source table
  // needs its own horizontal scrollbar. The source remains the accessible table,
  // so the overlay is hidden from assistive technology and its copied links are
  // kept out of the tab order.
  const overlay = document.createElement('div');
  overlay.className = 'sponsor-comparison-sticky';
  overlay.setAttribute('aria-hidden', 'true');
  const removeFromTabOrder = (element) => {
    element
      .querySelectorAll('a')
      .forEach((link) => link.setAttribute('tabindex', '-1'));
  };
  const header = document.createElement('table');
  header.className = 'sponsor-tiers';
  header.append(tiers.cloneNode(true));
  removeFromTabOrder(header);
  const sectionLabel = document.createElement('div');
  sectionLabel.className = 'sponsor-comparison-sticky-section';
  overlay.append(header, sectionLabel);
  document.body.append(overlay);
  let activeSection = null;
  let scheduled = false;

  function update() {
    scheduled = false;
    const bounds = comparison.getBoundingClientRect();
    const tierBounds = tiers.getBoundingClientRect();
    const height = tierBounds.height;
    overlay.hidden = tierBounds.top >= 0 || bounds.bottom <= 0;
    if (overlay.hidden) return;
    overlay.style.left = `${bounds.left}px`;
    overlay.style.width = `${comparison.clientWidth}px`;
    overlay.style.transform = `translateY(${Math.min(0, bounds.bottom - height)}px)`;
    header.style.width = `${table.getBoundingClientRect().width}px`;
    header.style.transform = `translateX(${-comparison.scrollLeft}px)`;
    // The overlay table is transformed, which makes position: sticky stick to
    // the table instead of the viewport, so pin the feature column by hand.
    header.querySelector('th').style.transform =
      `translateX(${comparison.scrollLeft}px)`;
    [...tiers.querySelectorAll('th')].forEach((cell, index) => {
      header.querySelectorAll('th')[index].style.width =
        `${cell.getBoundingClientRect().width}px`;
    });
    let active = null;
    sections.forEach((section) => {
      if (section.getBoundingClientRect().top <= height) active = section;
    });
    if (active !== activeSection) {
      sectionLabel.replaceChildren();
      if (active) {
        const cell = active.querySelector('.sponsor-comparison-heading th');
        [...cell.children].forEach((child) =>
          sectionLabel.append(child.cloneNode(true)),
        );
        removeFromTabOrder(sectionLabel);
      }
      activeSection = active;
    }
    sectionLabel.hidden = !active;
    if (active) {
      const offset = Math.min(
        0,
        active.getBoundingClientRect().bottom -
          height -
          sectionLabel.offsetHeight,
      );
      sectionLabel.style.transform = `translateY(${offset}px)`;
    }
  }
  function schedule() {
    if (!scheduled) {
      scheduled = true;
      requestAnimationFrame(update);
    }
  }
  window.addEventListener('scroll', schedule, { passive: true });
  comparison.addEventListener('scroll', schedule, { passive: true });
  const observer = new ResizeObserver(schedule);
  observer.observe(comparison);
  observer.observe(tiers);
  update();
});
