import { env } from 'cloudflare:workers';
import { getChatGPTUser } from '../../../chatgpt-auth';
import { handleCourse } from '../../../../lib/course-service.mjs';
export const dynamic = 'force-dynamic';
export async function GET(request: Request) { return handleCourse(request, env, await getChatGPTUser()); }
export async function POST(request: Request) { return handleCourse(request, env, await getChatGPTUser()); }
