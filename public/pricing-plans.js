/* Progressive guidance: format -> relevant service -> existing booking flow. */
(() => {
  'use strict';
  const groups = {
    written: ['astrology_report', 'name', 'report_combo'],
    audio: ['audio', 'audio_combo'],
    live: ['expert', 'personal', 'detailed', 'personal_combo', 'complete_combo']
  };
  const starts = document.querySelector('#funnel-start');
  if (!starts) return;
  const options = document.querySelector('#funnel-options');
  const result = document.querySelector('#funnel-result');
  const summaries = [...document.querySelectorAll('[data-plan-summary]')];
  const validPlans = new Set(summaries.map(e => e.dataset.planSummary));
  const groupFor = plan => Object.keys(groups).find(group => groups[group].includes(plan));
  let state = {group:null, plan:null};
  function readUrl() {
    const params = new URLSearchParams(location.search);
    const requested = params.get('plan') || location.hash.slice(1);
    if (validPlans.has(requested)) return {group:groupFor(requested),plan:requested};
    let group = params.get('guidance');
    if (group === 'expert' || group === 'vedansh') group = 'live';
    if (!Object.hasOwn(groups, group)) group = null;
    return {group,plan:group === 'audio' ? 'audio' : null};
  }
  function render(focus = false) {
    starts.hidden = Boolean(state.group);
    options.hidden = !state.group || Boolean(state.plan);
    result.hidden = !state.plan;
    document.querySelectorAll('[data-option-group]').forEach(section => section.hidden = section.dataset.optionGroup !== state.group);
    summaries.forEach(card => card.hidden = card.dataset.planSummary !== state.plan);
    document.querySelectorAll('[data-step]').forEach(step => {
      if (step.dataset.step === (state.group ? '2' : '1')) step.setAttribute('aria-current','step');
      else step.removeAttribute('aria-current');
    });
    document.body.dataset.funnelStage = state.plan ? 'result' : state.group ? 'options' : 'start';
    if (focus) {
      const target = state.plan ? result.querySelector('[data-plan-summary]:not([hidden]) h2') : state.group ? options.querySelector('[data-option-group]:not([hidden]) h2') : document.querySelector('h1');
      if (target) {target.setAttribute('tabindex','-1');target.focus({preventScroll:true});target.scrollIntoView({block:'nearest',behavior:'auto'});}
    }
  }
  function select(next) {
    state = next;
    const url = new URL(location.href);
    url.searchParams.delete('guidance');url.searchParams.delete('plan');url.hash = '';
    if (state.group) url.searchParams.set('guidance',state.group);
    if (state.plan) url.searchParams.set('plan',state.plan);
    history.pushState(null,'',url.pathname + url.search);
    render(true);
  }
  document.querySelectorAll('[data-guidance]').forEach(choice => choice.addEventListener('click', event => {
    event.preventDefault();
    const group = choice.dataset.guidance;
    if (!Object.hasOwn(groups,group)) return;
    select({group,plan:group === 'audio' ? 'audio' : null});
    document.dispatchEvent(new CustomEvent('astrovedansh:plan-filter',{detail:{group}}));
  }));
  document.querySelectorAll('[data-pick-plan]').forEach(choice => choice.addEventListener('click', event => {
    event.preventDefault();
    const plan = choice.dataset.pickPlan;
    if (validPlans.has(plan)) select({group:groupFor(plan),plan});
  }));
  document.querySelectorAll('[data-funnel-back]').forEach(button => button.addEventListener('click', () => {
    select(state.plan && state.group !== 'audio' ? {group:state.group,plan:null} : {group:null,plan:null});
  }));
  window.addEventListener('popstate', () => {state=readUrl();render(true);});
  window.addEventListener('hashchange', () => {state=readUrl();render(true);});
  state = readUrl();render();
})();
