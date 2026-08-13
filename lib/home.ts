import { Pool } from 'pg';
import type { Article } from '@/lib/news';

export type HomeMedia = {
  id: string;
  url: string;
  title: string;
  thumbnailUrl: string | null;
  createdAt: Date;
};

let pool: Pool | undefined;

function databasePool() {
  if (!pool) {
    if (!process.env.DATABASE_URL) throw new Error('DATABASE_URL is not configured.');
    pool = new Pool({ connectionString: process.env.DATABASE_URL });
  }
  return pool;
}

const articleSelect = `SELECT a.id,a.title,a.slug,a.excerpt,a.status,a."isBreaking",a."isTrending",a.views,a."publishedAt",c.name AS "categoryName",c.slug AS "categorySlug",u.name AS "authorName",m.url AS "imageUrl" FROM "Article" a JOIN "Category" c ON c.id=a."categoryId" JOIN "User" u ON u.id=a."authorId" LEFT JOIN "Media" m ON m.id=a."featuredImageId"`;

export async function getHomepageData() {
  const client = databasePool();
  const [articleResult, videoResult, shortResult] = await Promise.all([
    client.query<Article>(`${articleSelect} WHERE a.status='PUBLISHED' ORDER BY COALESCE(a."publishedAt",a."createdAt") DESC LIMIT 100`),
    client.query<HomeMedia>(`SELECT id,url,COALESCE("altText","fileName") AS title,"thumbnailUrl","createdAt" FROM "Media" WHERE "contentType"='VIDEO' ORDER BY "createdAt" DESC LIMIT 6`),
    client.query<HomeMedia>(`SELECT id,url,COALESCE("altText","fileName") AS title,"thumbnailUrl","createdAt" FROM "Media" WHERE "contentType"='SHORT' ORDER BY "createdAt" DESC LIMIT 6`),
  ]);
  return { articles: articleResult.rows, videos: videoResult.rows, shorts: shortResult.rows };
}
