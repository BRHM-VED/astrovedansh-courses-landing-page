// Astronomy Engine 2.1.19 (MIT), geocentric Moon; approximate Lahiri sidereal offset.
// Reference anchor: https://kerykeion.net/libephemeris/docs/reference/ayanamsha
export const moonSigns=[['मेष','Aries'],['वृषभ','Taurus'],['मिथुन','Gemini'],['कर्क','Cancer'],['सिंह','Leo'],['कन्या','Virgo'],['तुला','Libra'],['वृश्चिक','Scorpio'],['धनु','Sagittarius'],['मकर','Capricorn'],['कुंभ','Aquarius'],['मीन','Pisces']];
function birthSign(date,time,offset,body,engine=globalThis.Astronomy){
 if(!/^\d{4}-\d{2}-\d{2}$/.test(date)||!/^([01]\d|2[0-3]):[0-5]\d$/.test(time)||String(offset).trim()==='')throw Error('birth');
 const [y,m,d]=date.split('-').map(Number),[h,min]=time.split(':').map(Number),tz=Number(offset);
 const local=new Date(Date.UTC(y,m-1,d));
 if(y<1900||local.getUTCFullYear()!==y||local.getUTCMonth()!==m-1||local.getUTCDate()!==d||!Number.isFinite(tz)||tz < -12||tz >14)throw Error('birth');
 const utc=new Date(Date.UTC(y,m-1,d,h,min)-tz*3600000);if(body==='Moon'&&utc>new Date())throw Error('birth');
 if(!engine?.EclipticGeoMoon||!engine?.SunPosition)throw Error('engine');
 const T=(utc.getTime()/86400000+2440587.5-2451545)/36525;
 const ayan=23.857092+(5028.796195*T+1.1054348*T*T)/3600;
 const lon=(((body==='Moon'?engine.EclipticGeoMoon(utc).lon:engine.SunPosition(utc).elon)-ayan)%360+360)%360;
 const index=Math.floor(lon/30),degree=lon%30;
 return{index,sign:moonSigns[index],degree,boundary:degree<0.1||degree>29.9,utc};
}

export function moonSign(date,time,offset,engine=globalThis.Astronomy){return birthSign(date,time,offset,'Moon',engine);}
export function vedicSunSign(date,time,offset,engine=globalThis.Astronomy){
 if(time)return {...birthSign(date,time,offset,'Sun',engine),timed:true};
 const start=birthSign(date,'00:00',offset,'Sun',engine),end=birthSign(date,'23:59',offset,'Sun',engine);
 return {...start,timed:false,changing:start.index!==end.index,endSign:end.sign,boundary:start.boundary||end.boundary};
}
