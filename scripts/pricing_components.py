"""Approved service plans: one catalog for cards, booking summaries and fulfilment."""
import json
from html import escape

SERVICE_IDS = ['astrology_report', 'name', 'audio', 'expert', 'personal', 'detailed']

# Editorial recommendations only; popularity claims need verified sales data.
SERVICE_BADGES = {
    'astrology_report': ('Must Try', 'ज़रूर आज़माएँ', 'try'),
    'audio': ('Must Try', 'ज़रूर आज़माएँ', 'try'),
    'personal': ('Recommended', 'हमारी सलाह', 'recommended'),
    'complete_combo': ('Recommended', 'हमारी सलाह', 'recommended'),
}

def money(amount):
    return '₹' + format(amount, ',')

def bi(tag, en, hi, attrs=''):
    return f'<{tag} {attrs} data-en="{escape(en, quote=True)}" data-hi="{escape(hi, quote=True)}">{escape(hi)}</{tag}>'

def service_badge(key):
    if key not in SERVICE_BADGES:
        return ''
    en, hi, tone = SERVICE_BADGES[key]
    return bi('span', en, hi, f'class="service-badge service-badge--{tone}"')

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
    return '<section class="hub-section guidance-overview" id="consultations">'+bi('h2','Not sure what to choose?','समझ नहीं आ रहा क्या चुनें?')+bi('p','Tell us how you would like guidance. See only the options that fit.','रिपोर्ट, रिकॉर्डेड ऑडियो या लाइव बातचीत चुनें। आगे सिर्फ उसी के विकल्प देखें।')+'<a class="plan-cta" href="/pricing.html">'+bi('span','Help Me Choose →','मेरे लिए सही विकल्प चुनें →')+'</a></section>'

def funnel_choice(key, title, description, price, href, attr='guidance'):
    return f'<a class="funnel-choice" data-{attr}="{key}" href="{escape(href,quote=True)}"><span class="funnel-choice-copy">'+service_badge(key)+bi('strong',*title)+bi('small',*description)+f'</span><span class="funnel-choice-end"><b>{price}</b><span aria-hidden="true">→</span></span></a>'

def pricing_page(header, footer, data):
    p=data['plans']
    out='<!doctype html><html lang="hi" data-default-language="hi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Choose Your Guidance | AstroVedansh</title><meta name="description" content="Choose a written report, recorded audio answer or live conversation. A simple guide to the right AstroVedansh service for your needs."><link rel="canonical" href="https://courses.astrovedansh.org/pricing.html"><link rel="icon" href="/assets/astrovedansh-logo.webp"><link rel="stylesheet" href="/visual-refresh.css?v=20261019d"><link rel="stylesheet" href="/category-refinements.css?v=20261021"><link rel="stylesheet" href="/hub-refinements.css?v=20261020"><link rel="stylesheet" href="/guidance-plans.css?v=20261021"><link rel="stylesheet" href="/guidance-funnel.css?v=badges-1"></head><body class="category-refined pricing-page funnel-page" data-funnel-stage="start">'+header+'<main class="visual-main"><section class="visual-intro compact">'+bi('p','PERSONAL GUIDANCE, MADE SIMPLE','सही मार्गदर्शन चुनना अब आसान','class="eyebrow"')+bi('h1','How would you like guidance?','आपको किस तरह का मार्गदर्शन चाहिए?')+bi('p','Choose one option. We’ll guide you to the right service.','बस एक विकल्प चुनें। आगे हम सही सेवा चुनने में मदद करेंगे।','class="intro-copy"')+'</section><ol class="funnel-progress" aria-label="Booking steps">'
    for i,en,hi in [(1,'Your need','आपकी ज़रूरत'),(2,'Your plan','आपका विकल्प'),(3,'Booking','बुकिंग')]:
        out+=f'<li data-step="{i}"'+(' aria-current="step"' if i==1 else '')+f'><span>{i}</span>'+bi('small',en,hi)+'</li>'
    out+='</ol><div class="funnel-shell"><section id="funnel-start" aria-label="Choose guidance format"><div class="funnel-choices">'
    out+=funnel_choice('written',('I want a written report','मुझे लिखित रिपोर्ट चाहिए'),('Read your personalized analysis at your own pace.','अपना व्यक्तिगत विश्लेषण आराम से पढ़ें और समझें।'),bi('span','From '+money(p['astrology_report']['amount']),money(p['astrology_report']['amount'])+' से'), '/reports.html')
    out+=funnel_choice('audio',('I want Vedansh’s audio answer','मुझे वेदांश जी का ऑडियो जवाब चाहिए'),('Recorded WhatsApp voice note. Not a live call.','WhatsApp पर रिकॉर्डेड जवाब। लाइव कॉल नहीं।'),money(p['audio']['amount']),p['audio']['url'])
    out+=funnel_choice('live',('I want to talk live','मुझे सीधे बातचीत करनी है'),('Explain your situation and ask follow-up questions.','अपनी बात समझाएँ और फॉलो-अप सवाल पूछें।'),bi('span','From '+money(p['expert']['amount']),money(p['expert']['amount'])+' से'),'/consultation.html')
    out+='</div></section><section id="funnel-options" hidden><button class="funnel-back" type="button" data-funnel-back>'+bi('span','← Change guidance type','← मार्गदर्शन का तरीका बदलें')+'</button>'
    for group,en,hi,ids in [('written','What would you like a report about?','किस विषय की रिपोर्ट चाहिए?',['astrology_report','name']),('live','Who would you like to talk to?','किससे और कितनी देर बात करनी है?',['expert','personal','detailed'])]:
        out+=f'<div data-option-group="{group}" hidden>'+bi('h2',en,hi,'tabindex="-1"')+'<div class="funnel-choices">'
        labels={
          'astrology_report':(('Understand my birth chart','अपनी कुंडली समझनी है'),('Personalized written astrology analysis.','कुंडली पर आधारित व्यक्तिगत लिखित विश्लेषण।')),
          'name':(('Understand my name','अपने नाम का विश्लेषण चाहिए'),('Numerology-based analysis and name suggestions.','अंकज्योतिषीय विश्लेषण और नाम-संबंधी सुझाव।')),
          'expert':(('Team astrologer · 20–25 min','टीम के ज्योतिषी · 20–25 मिनट'),('Live guidance for your questions.','अपने सवालों पर लाइव बातचीत।')),
          'personal':(('Astro Vedansh · 30 min','वेदांश जी · 30 मिनट'),('Discuss your main questions one-to-one.','अपने मुख्य सवालों पर व्यक्तिगत बातचीत।')),
          'detailed':(('Astro Vedansh · 60 min','वेदांश जी · 60 मिनट'),('More time for several topics and follow-ups.','कई विषयों और फॉलो-अप के लिए अधिक समय।'))}
        for key in ids:
            title,description=labels[key]
            out+=funnel_choice(key,title,description,money(p[key]['amount']),p[key]['url'],'pick-plan')
        out+='</div></div>'
    out+='</section><section id="funnel-result" hidden><button class="funnel-back" type="button" data-funnel-back>'+bi('span','← Change selection','← विकल्प बदलें')+'</button>'
    for key,plan in p.items():
        out+=f'<article class="funnel-result-card" data-plan-summary="{key}" hidden>'+bi('p','YOUR SELECTED SERVICE','आपकी चुनी हुई सेवा','class="eyebrow"')+service_badge(key)+bi('h2',plan['title']['en'],plan['title']['hi'],'tabindex="-1"')+bi('p',plan['description']['en'],plan['description']['hi'],'class="plan-description"')+f'<strong class="funnel-price">{money(plan["amount"])}</strong>'
        if plan['saving']:
            out+='<p class="plan-saving"><s>'+money(plan['individualTotal'])+'</s> · '+bi('span',f'Save {money(plan["saving"])}',f'{money(plan["saving"])} की बचत')+'</p>'
        out+=item_list(plan)+f'<a class="plan-cta" data-plan-id="{key}" href="{escape(plan["url"],quote=True)}">'+bi('span','Continue to Booking →','बुकिंग के लिए आगे बढ़ें →')+'</a>'
        out+=bi('p','Next: your details and a WhatsApp request. Our team confirms the booking and final payment details.','आगे: अपना विवरण भरकर WhatsApp पर अनुरोध भेजें। बुकिंग और अंतिम भुगतान की पुष्टि टीम करेगी।','class="funnel-note"')+'</article>'
    out+='</section></div><div class="funnel-footer"><a href="/reports.html">'+bi('span','Browse reports','रिपोर्ट्स देखें')+'</a><span aria-hidden="true"> · </span><a href="/consultation.html">'+bi('span','Browse consultations','परामर्श देखें')+'</a></div><noscript><p>Choose one of the three links above to open its service page. / ऊपर दिए तीन विकल्पों में से अपनी सेवा चुनें।</p></noscript></main>'+footer+'<script defer src="/pricing-plans.js?v=funnel-1"></script><script defer src="/visual-refresh.js?v=20261019"></script><script defer src="/hub-navigation.js?v=20261020"></script><script defer src="/conversion-events.js?v=20261021-combos"></script></body></html>'
    return out
