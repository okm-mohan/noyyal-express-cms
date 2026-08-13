import Link from 'next/link';
import type { Article } from '@/lib/news';

export function PublicNewsGrid({ articles }: { articles: Article[] }) {
  return <div className="public-news-grid">{articles.map((article, index) => <Link href={`/news/${article.slug}`} key={article.id} className="public-news-card"><img src={article.imageUrl || `/images/latest-${(index % 3) + 1}.png`} alt=""/><div><span>{article.categoryName}</span><h2>{article.title}</h2><p>{article.excerpt}</p><small>{article.publishedAt ? new Date(article.publishedAt).toLocaleDateString('en-IN', { dateStyle: 'medium' }) : ''}</small></div></Link>)}</div>;
}
