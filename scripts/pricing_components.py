"""Approved service plans: one catalog for cards, booking summaries and fulfilment."""
import json
from html import escape

SERVICE_IDS = ['astrology_report', 'name', 'audio', 'expert', 'personal', 'detailed']

# Editorial recommendations only; popularity claims need verified sales data.
SERVICE_BADGES = {
    'astrology_report': ('Must Try', 'ज़रूर आज़माएँ', 'try'),
    'audio': ('Must Try', 'ज़रूर आज़माएँ', 'try'),
    'detailed': ('Recommended', 'हमारी सलाह', 'recommended'),
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
    # Old anchors still resolve without repeating the purchase decision.
    return '<a id="consultations" class="funnel-browse-link" href="/pricing.html?guidance=consultation">'+bi('span','View consultation plans →','परामर्श के विकल्प देखें →')+'</a>'

def progress(step=1):
    out='<ol class="funnel-progress" aria-label="Booking steps">'
    for i,en,hi in [(1,'Choose service','सेवा चुनें'),(2,'Choose plan','प्लान चुनें'),(3,'Your details','विवरण भरें')]:
        out+=f'<li data-step="{i}"'+(' aria-current="step"' if i==step else '')+f'><span>{i}</span>'+bi('small',en,hi)+'</li>'
    return out+'</ol>'

PLAN_COPY={
    'astrology_report':(('Understand your birth chart','अपनी कुंडली समझें'),('Personalized written astrology analysis.','कुंडली पर आधारित व्यक्तिगत लिखित विश्लेषण।')),
    'name':(('Understand your name','अपने नाम का विश्लेषण'),('Numerology analysis and name suggestions.','अंकज्योतिषीय विश्लेषण और नाम-संबंधी सुझाव।')),
    'audio':(('Vedansh’s recorded answer','वेदांश जी का रिकॉर्डेड जवाब'),('Send your question. Receive a personal voice note.','अपना सवाल भेजें। व्यक्तिगत वॉइस नोट पाएँ।')),
    'expert':(('Talk to a team astrologer','टीम के ज्योतिषी से बात करें'),('Explain your situation and ask follow-up questions.','अपनी बात समझाएँ और फॉलो-अप सवाल पूछें।')),
    'personal':(('Talk to Vedansh · 30 min','वेदांश जी से बात करें · 30 मिनट'),('One-to-one live guidance for your main questions.','अपने मुख्य सवालों पर व्यक्तिगत लाइव बातचीत।')),
    'detailed':(('Talk to Vedansh · 60 min','वेदांश जी से बात करें · 60 मिनट'),('More time for several topics and follow-up questions.','कई विषयों और फॉलो-अप के लिए अधिक समय।')),
    'report_combo':(('Two personal reports','दो व्यक्तिगत रिपोर्ट'),('Understand your birth chart and your name together.','कुंडली और नाम, दोनों का व्यक्तिगत विश्लेषण।')),
    'audio_combo':(('Audio answer + report','ऑडियो जवाब + रिपोर्ट'),('A recorded answer from Vedansh, plus a written report.','वेदांश जी का रिकॉर्डेड जवाब और एक लिखित रिपोर्ट।')),
    'personal_combo':(('30-min live + two reports','30 मिनट लाइव + दो रिपोर्ट'),('Talk personally with Vedansh and receive both reports.','वेदांश जी से लाइव बात करें और दोनों रिपोर्ट पाएँ।')),
    'complete_combo':(('60-min live + two reports','60 मिनट लाइव + दो रिपोर्ट'),('More time with Vedansh, along with both reports.','वेदांश जी से अधिक समय तक बातचीत और दोनों रिपोर्ट।')),
}

def selection_card(plan):
    key=plan['id']; title,description=PLAN_COPY[key]
    label=('Written report','लिखित रिपोर्ट') if plan['mode']=='written' else (('Recorded audio · not live','रिकॉर्डेड ऑडियो · लाइव नहीं') if plan['mode']=='audio' else ('Live conversation','लाइव बातचीत'))
    if len(plan['items'])>1: label=('Combo · '+label[0],'कॉम्बो · '+label[1])
    out=f'<article class="selection-card{" selection-card--recommended" if key=="detailed" else ""}" id="plan-{key}">'
    out+='<div class="selection-card-label">'+bi('small',*label)+service_badge(key)+'</div>'
    out+=bi('h3',*title)+bi('p',*description,'class="selection-description"')
    out+='<ul class="selection-inclusions">'
    if len(plan['items'])>1:
        for item in plan['lineItems']:
            out+=bi('li',item['title']['en'],item['title']['hi'])
    else:
        out+=bi('li',plan['title']['en'],plan['title']['hi'])
    if plan['minutes']:
        out+=bi('li',f"{plan['minutes']} min · {plan['astrologer']['en']}",f"{plan['minutes']} मिनट · {plan['astrologer']['hi']}")
    if plan['mode']=='audio':out+=bi('li','Voice note delivered on WhatsApp','WhatsApp पर वॉइस नोट की डिलीवरी')
    out+='</ul><div class="selection-action"><div class="selection-price"><strong>'+money(plan['amount'])+'</strong>'
    if plan['saving']:
        out+='<s aria-label="Individual total">'+money(plan['individualTotal'])+'</s>'+bi('small',f"Save {money(plan['saving'])}",f"{money(plan['saving'])} बचाएँ")
    out+='</div>'
    cta=('Get this combo →','यह कॉम्बो लें →') if len(plan['items'])>1 else (('Get this report →','यह रिपोर्ट लें →') if plan['mode']=='written' else (('Get audio analysis →','ऑडियो विश्लेषण लें →') if plan['mode']=='audio' else ('Book this session →','यह सेशन बुक करें →')))
    out+=f'<a class="selection-cta" data-plan-id="{key}" href="{escape(plan["url"],quote=True)}">'+bi('span',*cta)+'</a></div></article>'
    return out

def question_reports(products):
    # Keep specialist reports and their existing external journeys discoverable.
    out='<div class="question-reports">'+bi('h3','Looking for a specific answer?','किसी खास सवाल की रिपोर्ट चाहिए?')
    for key,title,description in [
        ('timing',('Perfect Timing · When?','Perfect Timing · कब?'),('Marriage, job or promotion timing','शादी, नौकरी या प्रमोशन का समय')),
        ('career',('Perfect Career · Which direction?','Perfect Career · कौन-सी दिशा?'),('Career options, professions and skills','करियर विकल्प, प्रोफेशन और कौशल')),
        ('milan',('Perfect Milan · Compatibility','Perfect Milan · कुंडली मिलान'),('Traditional analysis of two birth charts','दो जन्म कुंडलियों का पारंपरिक मिलान'))]:
        product=products[key]
        price=bi('small','View current price','मौजूदा कीमत देखें') if product['status']=='price_conflict' else '<b>'+money(product['amount'])+'</b>'
        out+=f'<a href="{escape(product["url"],quote=True)}" data-product="{key}"><span>'+bi('strong',*title)+bi('small',*description)+'</span><span class="question-report-price">'+price+'<span aria-hidden="true">→</span></span></a>'
    return out+'</div>'

def chooser(data, products):
    plans=data['plans']
    out='<section class="guidance-chooser" id="premium" data-guidance-chooser>'+bi('h2','What would you like to choose?','आप क्या लेना चाहेंगे?','class="chooser-title" tabindex="-1"')
    out+=bi('p','Choose a service on its own, or a combo.','एक सेवा अलग से लें या कॉम्बो चुनें।','class="chooser-intro"')+progress()
    out+='<div id="funnel-start" class="funnel-choices">'
    choices=[('reports',('Reports only','सिर्फ रिपोर्ट'),('Personalized written analysis','व्यक्तिगत लिखित विश्लेषण'),plans['astrology_report']['amount'],'report-editorial.webp'),('consultation',('Consultation only','सिर्फ परामर्श'),('Recorded audio or a live conversation','रिकॉर्डेड ऑडियो या लाइव बातचीत'),plans['audio']['amount'],'vedansh-vallabh.webp'),('combos',('Combo packages','कॉम्बो पैकेज'),('Reports together, or with audio / live guidance','दो रिपोर्ट, या ऑडियो / लाइव के साथ रिपोर्ट'),plans['report_combo']['amount'],'report-editorial.webp')]
    for group,title,description,amount,asset in choices:
        price=bi('b','From '+money(amount),money(amount)+' से')
        if group=='consultation':
            price=bi('b','Audio '+money(amount),'ऑडियो '+money(amount))+bi('small','Live from '+money(plans['expert']['amount']),'लाइव '+money(plans['expert']['amount'])+' से')
        out+=f'<a class="funnel-choice" data-guidance="{group}" href="/pricing.html?guidance={group}#premium" aria-controls="group-{group}" aria-expanded="false"><img src="/assets/{asset}" width="60" height="60" alt="" decoding="async"><span class="funnel-choice-copy">'+bi('strong',*title)+bi('small',*description)+'</span><span class="funnel-choice-end">'+price+'<span aria-hidden="true">→</span></span></a>'
    out+='</div><div id="funnel-options"><button class="funnel-back" type="button" data-funnel-back hidden>'+bi('span','← Change service','← सेवा बदलें')+'</button>'
    groups=[('reports',('Choose your report','अपनी रिपोर्ट चुनें'),('A written analysis to read at your own pace.','लिखित विश्लेषण, जिसे आप आराम से पढ़ सकें।'),['astrology_report','name']),('consultation',('Choose your consultation','अपना परामर्श चुनें'),('Audio is a recorded reply. Live sessions let you ask follow-ups.','ऑडियो रिकॉर्डेड जवाब है। लाइव सेशन में आगे के सवाल भी पूछ सकते हैं।'),['audio','expert','personal','detailed']),('combos',('Choose your combo','अपना कॉम्बो चुनें'),('One package price. Every included service is listed below.','एक पैकेज की कुल कीमत। उसमें शामिल हर सेवा नीचे दी गई है।'),list(data['plans'])[6:])]
    for group,title,description,ids in groups:
        out+=f'<section class="funnel-group" id="group-{group}" data-option-group="{group}">'+bi('h2',*title,'tabindex="-1"')+bi('p',*description,'class="funnel-group-description"')+'<div class="selection-grid">'+''.join(selection_card(plans[key]) for key in ids)+'</div>'
        if group=='reports':out+=question_reports(products)
        out+=bi('p','Next: fill in your details and send your request on WhatsApp. Our team confirms delivery, availability and payment details.','आगे: विवरण भरें और WhatsApp पर अनुरोध भेजें। डिलीवरी, उपलब्धता और भुगतान की पुष्टि टीम करेगी।','class="funnel-note"')+'</section>'
    out+='</div></section>'
    return out

def pricing_page(header, footer, data, products):
    out='<!doctype html><html lang="hi" data-default-language="hi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Choose Your Guidance | AstroVedansh</title><meta name="description" content="Choose a personal report, recorded audio or live consultation on its own, or a combo. Select your plan and continue to the existing booking form."><link rel="canonical" href="https://courses.astrovedansh.org/pricing.html"><link rel="icon" href="/assets/astrovedansh-logo.webp"><link rel="stylesheet" href="/visual-refresh.css?v=20261019d"><link rel="stylesheet" href="/category-refinements.css?v=20261021"><link rel="stylesheet" href="/hub-refinements.css?v=20261020"><link rel="stylesheet" href="/guidance-funnel.css?v=simple-2"><link rel="stylesheet" href="/reference-ui.css?v=20261022"/></head><body class="category-refined pricing-page funnel-page">'+header+'<main class="visual-main"><section class="visual-intro compact">'+bi('p','PERSONAL GUIDANCE, MADE SIMPLE','आपकी ज़रूरत, आपका विकल्प','class="eyebrow"')+bi('h1','Reports, consultations or a combo.','रिपोर्ट, परामर्श या कॉम्बो।')+bi('p','Choose your service and plan. Then send your booking details on WhatsApp.','सेवा और प्लान चुनें। फिर विवरण भरकर WhatsApp पर भेजें।','class="intro-copy"')+'</section>'+chooser(data,products)+'</main>'+footer+'<script defer src="/pricing-plans.js?v=simple-2"></script><script defer src="/visual-refresh.js?v=20261019"></script><script defer src="/hub-navigation.js?v=20261020"></script><script defer src="/conversion-events.js?v=20261021-combos"></script></body></html>'
    return out
