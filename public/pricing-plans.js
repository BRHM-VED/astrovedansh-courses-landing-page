/* Service category -> plan's existing booking page. No intermediate summary. */
(() => {
  'use strict';
  const root = document.querySelector('[data-guidance-chooser]');
  if (!root) return;
  const start = root.querySelector('#funnel-start');
  const options = root.querySelector('#funnel-options');
  const back = root.querySelector('[data-funnel-back]');
  const sections = [...root.querySelectorAll('[data-option-group]')];
  const groups = new Set(sections.map(e => e.dataset.optionGroup));
  const links = [...root.querySelectorAll('[data-plan-id]')];
  const aliases = {written:'reports', audio:'consultation', live:'consultation', expert:'consultation', vedansh:'consultation', combo:'combos'};
  let group = null;
  function readUrl() {
    const params = new URLSearchParams(location.search);
    const requested = params.get('plan') || location.hash.slice(1);
    const plan = links.find(e => e.dataset.planId === requested);
    if (plan) return plan.closest('[data-option-group]').dataset.optionGroup;
    const legacyAnchors = {'personal-reports':'reports', 'timing-offers':'reports', consultations:'consultation'};
    const value = params.get('guidance');
    const resolved = groups.has(value) ? value : aliases[value] || legacyAnchors[location.hash.slice(1)];
    return groups.has(resolved) ? resolved : null;
  }
  function render(focus = false) {
    start.hidden = !!group;
    options.hidden = !group;
    back.hidden = !group;
    sections.forEach(section => {section.hidden = section.dataset.optionGroup !== group;});
    root.querySelectorAll('[data-guidance]').forEach(link => link.setAttribute('aria-expanded',String(link.dataset.guidance === group)));
    root.querySelectorAll('[data-step]').forEach(step => {
      if (step.dataset.step === (group ? '2' : '1')) step.setAttribute('aria-current','step');
      else step.removeAttribute('aria-current');
    });
    root.dataset.stage = group ? 'plans' : 'service';
    root.querySelector('.chooser-title').hidden = !!group;
    root.querySelector('.chooser-intro').hidden = !!group;
    if (focus) {
      const target = group ? sections.find(section => !section.hidden).querySelector('h2') : root.querySelector('.chooser-title');
      target.focus({preventScroll:true});
      root.scrollIntoView({block:'start',behavior:'instant'});
    }
  }
  function select(value) {
    group = value;
    const url = new URL(location.href);
    url.searchParams.delete('plan');
    url.searchParams.delete('guidance');
    url.hash = 'premium';
    if (group) url.searchParams.set('guidance',group);
    history.pushState(null,'',url.pathname + url.search + url.hash);
    render(true);
  }
  root.querySelectorAll('[data-guidance]').forEach(choice => choice.addEventListener('click', event => {
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const next = choice.dataset.guidance;
    if (!groups.has(next)) return;
    event.preventDefault();
    select(next);
    document.dispatchEvent(new CustomEvent('astrovedansh:plan-filter',{detail:{group:next}}));
  }));
  back.addEventListener('click',() => select(null));
  window.addEventListener('popstate',() => {group=readUrl();render(true);});
  window.addEventListener('hashchange',() => {group=readUrl();render();});
  group=readUrl();render();
})();
