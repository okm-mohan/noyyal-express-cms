import { NextResponse } from 'next/server';
import { randomUUID } from 'crypto';
import { Pool } from 'pg';
import { ensureArticleInteractions } from '@/lib/article-detail';

let pool: Pool | undefined;
function databasePool() { if (!pool) pool = new Pool({ connectionString: process.env.DATABASE_URL }); return pool; }
export async function POST(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params; const { visitorId } = await request.json();
  if (typeof visitorId !== 'string' || visitorId.length > 100) return NextResponse.json({ error: 'Invalid request.' }, { status: 400 });
  await ensureArticleInteractions(); const client = databasePool();
  const existing = await client.query('SELECT id FROM "ArticleLike" WHERE "articleId"=$1 AND "visitorId"=$2', [id, visitorId]); let liked: boolean;
  if (existing.rowCount) { await client.query('DELETE FROM "ArticleLike" WHERE id=$1', [existing.rows[0].id]); liked = false; } else { await client.query('INSERT INTO "ArticleLike" (id,"articleId","visitorId") VALUES ($1,$2,$3)', [randomUUID(), id, visitorId]); liked = true; }
  const count = await client.query<{ count: string }>('SELECT COUNT(*)::text AS count FROM "ArticleLike" WHERE "articleId"=$1', [id]);
  return NextResponse.json({ liked, likes: Number(count.rows[0].count) });
}
