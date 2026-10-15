import { env } from 'cloudflare:workers';
import { handleEmailCourse } from '../../../../lib/email-course.mjs';
export const dynamic='force-dynamic';
export async function GET(request:Request){return handleEmailCourse(request,env);}
export async function POST(request:Request){return handleEmailCourse(request,env);}
