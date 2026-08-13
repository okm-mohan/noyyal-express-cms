import Link from 'next/link';
import { ArrowLeft, MessageSquareText, Sparkles } from 'lucide-react';
import { redirect } from 'next/navigation';
import { Pool } from 'pg';
import { PollForm } from '@/components/PollForm';
const pool=new Pool({connectionString:process.env.DATABASE_URL});
async function createPoll(data:FormData){'use server';const question=String(data.get('question')||'').trim(),options=data.getAll('option').map(value=>String(value).trim()).filter(Boolean);if(!question||options.length<2)throw new Error('A question and at least two options are required.');await pool.query('INSERT INTO "Poll" (id,question,options,is_active,updated_at) VALUES ($1,$2,$3::jsonb,$4,NOW())',[crypto.randomUUID(),question,JSON.stringify(options.map(label=>({label,votes:0}))),data.get('isActive')==='on']);redirect('/admin/polls')}
export default function NewPoll(){return <section className="poll-create"><header><Link href="/admin/polls"><ArrowLeft/> POLLS</Link><span><Sparkles/> AUDIENCE PULSE</span><h1>Create Poll</h1><p>Invite readers to share their view on a timely newsroom question.</p></header><div className="poll-create-card"><MessageSquareText/><div><h2>Question builder</h2><p>Keep the question short, neutral, and easy to answer.</p></div><PollForm action={createPoll}/></div></section>}