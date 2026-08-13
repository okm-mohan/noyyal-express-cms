import { Pool } from 'pg';
import type { Article } from '@/lib/news';

export type ArticleDetail = Article & { content: string | null };
export type Comment = { id: string; name: string; message: string; createdAt: Date };
let pool: Pool | undefined;
let initialized = false;
function databasePool() { if (!pool) { if (!process.env.DATABASE_URL) throw new Error('DATABASE_URL is not configured.'); pool = new Pool({ connectionString: process.env.DATABASE_URL }); } return pool; }

export async function ensureArticleInteractions() {
  if (initialized) return;
  await databasePool().query(`CREATE TABLE IF NOT EXISTS "ArticleComment" (id text PRIMARY KEY, "articleId" text NOT NULL REFERENCES "Article"(id) ON DELETE CASCADE, name text NOT NULL, message text NOT NULL, "createdAt" timestamp NOT NULL DEFAULT NOW()); CREATE TABLE IF NOT EXISTS "ArticleLike" (id text PRIMARY KEY, "articleId" text NOT NULL REFERENCES "Article"(id) ON DELETE CASCADE, "visitorId" text NOT NULL, "createdAt" timestamp NOT NULL DEFAULT NOW(), UNIQUE("articleId","visitorId")); CREATE INDEX IF NOT EXISTS "ArticleComment_articleId_createdAt_idx" ON "ArticleComment"("articleId","createdAt" DESC);`);
  initialized = true;
}

const select = `SELECT a.id,a.title,a.slug,a.excerpt,a.content,a.status,a."isBreaking",a."isTrending",a.views,a."publishedAt",c.name AS "categoryName",c.slug AS "categorySlug",u.name AS "authorName",m.url AS "imageUrl" FROM "Article" a JOIN "Category" c ON c.id=a."categoryId" JOIN "User" u ON u.id=a."authorId" LEFT JOIN "Media" m ON m.id=a."featuredImageId"`;

export async function getArticleDetail(slug: string) {
  await ensureArticleInteractions();
  const client = databasePool();
  const result = await client.query<ArticleDetail>(`${select} WHERE a.slug=$1 AND a.status='PUBLISHED'`, [slug]);
  const article = result.rows[0];
  if (!article) return null;
  const [comments, likes, related] = await Promise.all([
    client.query<Comment>('SELECT id,name,message,"createdAt" FROM "ArticleComment" WHERE "articleId"=$1 ORDER BY "createdAt" DESC', [article.id]),
    client.query<{ count: string }>('SELECT COUNT(*)::text AS count FROM "ArticleLike" WHERE "articleId"=$1', [article.id]),
    client.query<Article>(`${select} WHERE a.status='PUBLISHED' AND a.id<>$1 AND c.slug=$2 ORDER BY COALESCE(a."publishedAt",a."createdAt") DESC LIMIT 4`, [article.id, article.categorySlug]),
  ]);
  return { article, comments: comments.rows, likes: Number(likes.rows[0].count), related: related.rows };
}
