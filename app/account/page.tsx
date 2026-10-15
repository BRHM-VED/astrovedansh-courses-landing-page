import {redirect} from 'next/navigation';
export const dynamic='force-dynamic';
export default async function Account({searchParams}:{searchParams:Promise<{lang?:string}>}){
 const en=(await searchParams).lang==='en';redirect((en?'/numerology-english.html':'/numerology.html')+'#course-coupon');
}
