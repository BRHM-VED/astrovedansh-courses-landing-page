"""Apply the recorded editorial checks to the October 19 teaching sources."""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
for path in sorted((root / 'content').glob('lessons-2026-10-19-*.json')):
    rows = json.loads(path.read_text())
    for row in rows:
        row['body_html'] = row['body_html'].replace('हमने मूल संस्कृत पाठ में भी', 'उपलब्ध संस्कृत पाठ और अनुवाद में')
        row['source_method'] = ('वी. सुब्रह्मण्य शास्त्री के १९५० के फलदीपिका अनुवाद के संबंधित ऑनलाइन अंशों से अध्याय और श्लोक मिलाए गए। '
                                'उपलब्ध पाठ में यंत्र-पाठ की त्रुटियाँ संभव हैं; मूल पृष्ठ-चित्र से मिलान का दावा नहीं है। '
                                'नियमों को शब्दशः उद्धृत नहीं किया गया है।')
        if row['number'] == 122 and 'यहाँ राशि-परिवर्तन भी है' not in row['body_html']:
            extra = ('<p><strong>यहाँ राशि-परिवर्तन भी है:</strong> शनि मंगल की मेष राशि में है और मंगल शनि की मकर राशि में। '
                     'दो ग्रहों का एक-दूसरे की राशि में बैठना परिवर्तन कहलाता है। इसलिए इस उदाहरण में केवल परस्पर दृष्टि नहीं, '
                     'राशि-स्वामियों की आपसी कड़ी भी है। वृषभ लग्न में इससे नवम-दशम के स्वामी शनि और सप्तम-द्वादश के स्वामी मंगल '
                     'के विषय जुड़ते हैं। काम, सहयोग और व्यय को साथ पढ़ना होगा। इस संबंध का नाम मिलना शनि की नीच राशि को '
                     'अपने आप मिटा नहीं देता; दोनों ग्रहों के बल, अन्य संबंध और सक्रिय अवधि की जाँच अभी बाकी है।</p>\n')
            marker = '<h2>वर्ग कुंडली और समय की सावधानी</h2>'
            assert marker in row['body_html']
            row['body_html'] = row['body_html'].replace(marker, extra + marker)
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
