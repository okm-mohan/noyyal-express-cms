import { NextResponse } from 'next/server';
import { randomUUID } from 'crypto';
import { Pool } from 'pg';
import { ensureArticleInteractions } from '@/lib/article-detail';
let pool: Pool | undefined;
function databasePool() { if (!pool) pool = new Pool({ connectionString: process.env.DATABASE_URL }); return pool; }
export async function POST(request: Request, { params }: { params: Promise<{ id: string }> }) { const { id } = await params; const body = await request.json(); const name = String(body.name || '').trim(); const message = String(body.message || '').trim(); if (!name || !message || name.length > 60 || message.length > 600) return NextResponse.json({ error: 'Please provide a valid name and comment.' }, { status: 400 }); await ensureArticleInteractions(); const comment = await databasePool().query('INSERT INTO "ArticleComment" (id,"articleId",name,message) VALUES ($1,$2,$3,$4) RETURNING id,name,message,"createdAt"', [randomUUID(), id, name, message]); return NextResponse.json(comment.rows[0], { status: 201 }); }
