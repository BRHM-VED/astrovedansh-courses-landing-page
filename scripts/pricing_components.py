"""Approved service plans: one catalog for cards, booking summaries and fulfilment."""
import json
from html import escape

SERVICE_IDS = ['astrology_report', 'name', 'audio', 'expert', 'personal', 'detailed']

def money(amount):
    return '₹' + format(amount, ',')

def bi(tag, en, hi, attrs=''):
    return f'<{tag} {attrs} data-en="{escape(en, quote=True)}" data-hi="{escape(hi, quote=True)}">{escape(hi)}</{tag}>'

def booking_data(catalog):
    products = catalog['products']
    plans = {}
    for key in SERVICE_IDS + list(catalog['bundles']):
        p = dict(products[key] if key in products else catalog['bundles'][key])
        items = p.get('items', [key])
        assert len(items) == len(set(items)), f'Duplicate bundle items: {key}'
        assert p['active'] and p['status'] == 'owner_approved' and p['checkout'] == 'whatsapp_request'
        assert isinstance(p['amount'], int) and p['amount'] > 0
        p.update(id=key, items=items, individualTotal=sum(products[i]['amount'] for i in items))
        p['saving'] = p['individualTotal'] - p['amount']
        assert p['saving'] >= 0
        p['lineItems'] = [dict(id=i, quantity=1, title=products[i]['title'], standaloneAmount=products[i]['amount']) for i in items]
        primary = products[items[0]]
        p['minutes'] = primary.get('minutes')
        p['astrologer'] = primary.get('astrologer')
        p['needsBirthTime'] = key != 'name'
        p['needsAvailability'] = p['mode'] != 'written'
        p['includesNameReport'] = 'name' in items
        p['upgrade'] = catalog['upgrades'].get(key)
        plans[key] = p
    return dict(plans=plans, booking=catalog['booking'], aliases={'30':'personal', '60':'detailed'})

def item_list(plan):
    entries = [bi('li', x['title']['en'], x['title']['hi']) for x in plan['lineItems']]
    if plan['mode'] != 'written':
        mode = ('recorded voice note on WhatsApp · not a live call', 'WhatsApp पर रिकॉर्डेड वॉइस नोट · लाइव कॉल नहीं') if plan['mode'] == 'audio' else ('one-to-one live session', 'व्यक्तिगत लाइव सेशन')
        entries.append(bi('li', f"{plan['minutes']} min · {mode[0]}", f"{plan['minutes']} मिनट · {mode[1]}"))
    if plan.get('recommended'):
        entries.append(bi('li', 'Multiple life topics and follow-up questions within the 60-minute session', '60 मिनट के सेशन में कई विषयों और फॉलो-अप सवालों पर चर्चा'))
    return '<ul class="plan-inclusions">' + ''.join(entries) + '</ul>'

def combo_card(plan):
    key = plan['id']
    out = f'<article class="combo-card{" recommended" if plan.get("recommended") else ""}" data-plan-group="{plan["group"]}" id="{key}">'
    if plan.get('recommended'):
        out += bi('span', 'Recommended', 'हमारी सलाह', 'class="plan-badge"')
    out += bi('h3', plan['title']['en'], plan['title']['hi'])
    out += bi('p', plan['description']['en'], plan['description']['hi'], 'class="plan-description"')
    out += f'<div class="plan-price"><strong>{money(plan["amount"])}</strong><span><s>{money(plan["individualTotal"])}</s> '+bi('small','Bought separately','अलग-अलग लेने पर')+'</span></div>'
    out += bi('p', f'Save {money(plan["saving"])}', f'{money(plan["saving"])} की बचत', 'class="plan-saving"')
    out += item_list(plan)
    out += f'<a class="plan-cta" data-plan-id="{key}" href="{escape(plan["url"],quote=True)}">'+bi('span',plan['cta']['en']+' →',plan['cta']['hi']+' →')+'</a></article>'
    return out

def standalone_row(p):
    extra = ''
    if p.get('astrologer'):
        extra = bi('small', p['astrologer']['en'], p['astrologer']['hi'])
    cta = ('Get Report →','रिपोर्ट लें →') if p['mode']=='written' else (('Get Audio →','ऑडियो लें →') if p['mode']=='audio' else ('Book Session →','सेशन बुक करें →'))
    return f'<article class="standalone-plan" data-plan-group="{p["group"]}"><div>'+bi('h3',p['title']['en'],p['title']['hi'])+bi('p',p['description']['en'],p['description']['hi'])+extra+f'</div><div class="standalone-action"><strong>{money(p["amount"])}</strong><a class="plan-cta secondary" data-plan-id="{p["id"]}" href="{escape(p["url"],quote=True)}">'+bi('span',*cta)+'</a></div></article>'

def overview(data):
    return '<section class="hub-section guidance-overview" id="consultations">'+bi('h2','Choose Guidance for Your Needs and Budget','अपनी ज़रूरत और बजट के हिसाब से मार्गदर्शन चुनें')+bi('p','Personalized astrology reports, audio guidance and live consultation with Astro Vedansh.','व्यक्तिगत ज्योतिष रिपोर्ट, ऑडियो मार्गदर्शन और वेदांश जी के साथ लाइव परामर्श।')+'<div class="guidance-range"><div>'+bi('small','Start with a report','रिपोर्ट से शुरुआत')+f'<strong>{money(data["plans"]["astrology_report"]["amount"])}</strong></div><div>'+bi('small','Complete Life Guidance Combo','सम्पूर्ण जीवन मार्गदर्शन कॉम्बो')+f'<strong>{money(data["plans"]["complete_combo"]["amount"])}</strong></div></div><a class="plan-cta" href="/pricing.html">'+bi('span','View All Plans →','सभी प्लान देखें →')+'</a></section>'

def pricing_page(header, footer, data):
    out = '<!doctype html><html lang="hi" data-default-language="hi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Guidance Plans & Combos | AstroVedansh</title><meta name="description" content="Compare personalized astrology reports, recorded audio and live consultation plans. Reports from ₹299; Complete Life Guidance Combo ₹3,499."><link rel="canonical" href="https://courses.astrovedansh.org/pricing.html"><link rel="icon" href="/assets/astrovedansh-logo.webp"><link rel="stylesheet" href="/visual-refresh.css?v=20261019d"><link rel="stylesheet" href="/category-refinements.css?v=20261021"><link rel="stylesheet" href="/hub-refinements.css?v=20261020"><link rel="stylesheet" href="/guidance-plans.css?v=20261021"></head><body class="category-refined pricing-page">'+header+'<main class="visual-main"><section class="visual-intro compact">'+bi('p','CLEAR OPTIONS · PERSONAL GUIDANCE','स्पष्ट विकल्प · व्यक्तिगत मार्गदर्शन','class="eyebrow"')+bi('h1','Your question. Your budget. Your choice.','आपका सवाल। आपका बजट। आपकी पसंद।')+bi('p','Start with a ₹299 report or choose a conversation with an astrologer. Compare standalone services and combos below.','₹299 की रिपोर्ट से शुरुआत करें या ज्योतिषी से बातचीत चुनें। नीचे सेवाओं और कॉम्बो की तुलना करें।','class="intro-copy"')+'</section><section class="plan-selector" aria-labelledby="guidance-heading">'+bi('h2','1. What kind of guidance do you need?','1. किस तरह का मार्गदर्शन चाहिए?','id="guidance-heading"')+'<div class="plan-filters" aria-label="Guidance categories">'
    for key,en,hi in [('all','All plans','सभी प्लान'),('written','Written Astrology Reports','लिखित ज्योतिष रिपोर्ट'),('audio','Audio Analysis','रिकॉर्डेड ऑडियो'),('expert','Live Expert Consultation','एक्सपर्ट लाइव परामर्श'),('vedansh','Live with Astro Vedansh','वेदांश जी से लाइव परामर्श')]:
        out+=bi('button',en,hi,f'type="button" data-guidance="{key}" aria-pressed="{str(key=="all").lower()}"')
    out+='</div></section><section id="plans">'+bi('h2','2. Choose your plan','2. अपना प्लान चुनें')+bi('p','Combos include the listed services at one package price. Standalone options remain available below.','कॉम्बो में बताई गई सभी सेवाएँ एक पैकेज कीमत में शामिल हैं। नीचे अलग-अलग सेवाएँ भी उपलब्ध हैं।','class="plans-note"')+'<a class="standalone-shortcut" href="#standalone-services">'+bi('span','Prefer one service? Standalone options from ₹299 ↓','सिर्फ एक सेवा चाहिए? ₹299 से विकल्प देखें ↓')+'</a><div class="combo-grid">'+''.join(combo_card(p) for p in data['plans'].values() if len(p['items'])>1)+'</div>'+bi('h2','Standalone services','अलग-अलग सेवाएँ','class="standalone-heading" id="standalone-services"')+'<div class="standalone-list">'+''.join(standalone_row(data['plans'][k]) for k in SERVICE_IDS)+'</div></section><section class="booking-explainer">'+bi('h2','3. Share your details. Confirm with our team.','3. विवरण भेजें। टीम से पुष्टि पाएँ।')+bi('p','Select a plan, fill in the relevant details and send your request on WhatsApp. Our team confirms availability, delivery, the final payable amount and any applicable taxes before payment. No payment is collected on this page.','प्लान चुनें, ज़रूरी विवरण भरें और WhatsApp पर अनुरोध भेजें। टीम भुगतान से पहले उपलब्धता, डिलीवरी, अंतिम देय राशि और लागू कर की पुष्टि करेगी। इस पेज पर भुगतान नहीं लिया जाता।')+bi('p','Astrology offers traditional interpretations and possibilities, not guaranteed outcomes.','ज्योतिष पारंपरिक व्याख्याएँ और संभावनाएँ प्रस्तुत करता है; परिणामों की गारंटी नहीं।','class="plans-note"')+'</section></main>'+footer+'<script defer src="/pricing-plans.js?v=20261021"></script><script defer src="/visual-refresh.js?v=20261019"></script><script defer src="/hub-navigation.js?v=20261020"></script><script defer src="/conversion-events.js?v=20261021-combos"></script></body></html>'
    return out.replace('₹299', money(data['plans']['astrology_report']['amount'])).replace('₹3,499', money(data['plans']['complete_combo']['amount']))
