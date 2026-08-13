'use client';

import { ChevronDown, ChevronLeft, ChevronRight, Clock3, Edit3, Eye, Filter, MoreHorizontal, Plus, Search, Trash2 } from 'lucide-react';
import { useMemo, useState, useTransition } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { deleteArticle } from '@/app/admin/news/actions';
import type { Article } from '@/lib/news';

type Props = {
  articles: Article[];
  stats: Record<string, number>;
  total: number;
  page: number;
  limit: number;
  filters: { page: number; query: string; category: string; status: string };
};

export function AdminNewsList({ articles, stats, total, page, limit, filters }: Props) {
  const router = useRouter();
  const [pending, startTransition] = useTransition();
  const [query, setQuery] = useState(filters.query);
  const [status, setStatus] = useState(filters.status || 'ALL');
  const [category, setCategory] = useState(filters.category || 'ALL CATEGORIES');
  const categories = [...new Set(articles.map((article) => article.categoryName))].sort();
  const filtered = articles;
  const navigate = (nextPage = 1) => { const params = new URLSearchParams(); if (query) params.set('query', query); if (category !== 'ALL CATEGORIES') params.set('category', category); if (status !== 'ALL') params.set('status', status); params.set('page', String(nextPage)); router.push('/admin/news?' + params.toString()); };
  const totals = [
    ['ALL NEWS', total],
    ['PUBLISHED', stats.PUBLISHED ?? 0],
    ['DRAFTS', stats.DRAFT ?? 0],
    ['SCHEDULED', stats.SCHEDULED ?? 0],
  ];

  return <><header className="admin-top news-top"><div><p className="breadcrumbs">Dashboard / News Management / <span>All News</span></p><h1>All News</h1><p>Manage, publish and organize your news articles.</p></div><Link className="admin-add" href="/admin/news/new"><Plus /> ADD NEWS</Link></header><section className="news-stats">{totals.map(([label, value]) => <article className={label === 'ALL NEWS' ? 'active' : ''} key={label as string}><small>{label as string}</small><b>{value as number}</b></article>)}</section><section className="admin-card news-list"><div className="news-filters"><div className="search-input"><Search /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search news by title..." /></div><select value={category} onChange={(event) => setCategory(event.target.value)}><option>ALL CATEGORIES</option>{categories.map((item) => <option key={item}>{item}</option>)}</select><select value={status} onChange={(event) => setStatus(event.target.value)}><option value="ALL">ALL STATUS</option><option value="PUBLISHED">PUBLISHED</option><option value="DRAFT">DRAFT</option><option value="SCHEDULED">SCHEDULED</option><option value="ARCHIVED">ARCHIVED</option></select><button onClick={() => navigate()}><Filter /> FILTER</button></div><div className="news-list-title"><div><h2>News Articles</h2><p>Showing {filtered.length} of {total} articles</p></div><button><Clock3 /> Last updated today <ChevronDown /></button></div><div className="responsive-table"><table><thead><tr><th><input type="checkbox" /></th><th>ARTICLE</th><th>CATEGORY</th><th>STATUS</th><th>AUTHOR</th><th>PUBLISHED DATE</th><th>VIEWS</th><th>ACTION</th></tr></thead><tbody>{filtered.map((article, index) => <tr key={article.id}><td><input type="checkbox" /></td><td><div className="article-cell"><img src={article.imageUrl || `/images/latest-${(index % 3) + 1}.png`} alt="" /><p>{article.title}<small>Updated {article.publishedAt ? new Date(article.publishedAt).toLocaleDateString('en-IN', { dateStyle: 'medium' }) : 'recently'}</small></p></div></td><td><span className="category-pill">{article.categoryName}</span></td><td><span className={`status-pill ${article.status.toLowerCase()}`}>{article.status}</span></td><td>{article.authorName}</td><td>{article.publishedAt ? new Date(article.publishedAt).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' }) : 'Not published'}</td><td><span className="views"><Eye />{article.views.toLocaleString()}</span></td><td><div className="row-actions"><Link href={`/admin/news/${article.id}`} title="Edit"><Edit3 /></Link><button title="Delete" disabled={pending} onClick={() => { if (confirm(`Delete ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã¢â‚¬Å“${article.title}ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â? This cannot be undone.`)) startTransition(async () => { await deleteArticle(article.id); router.refresh(); }); }}><Trash2 /></button><button title="More"><MoreHorizontal /></button></div></td></tr>)}</tbody></table></div><footer className="news-pagination"><p>Showing <b>{total ? (page - 1) * limit + 1 : 0}-{Math.min(page * limit, total)}</b> of <b>{total}</b> results</p><div><button disabled={page <= 1} onClick={() => navigate(page - 1)}><ChevronLeft /></button><button className="current">{page}</button><button disabled={page * limit >= total} onClick={() => navigate(page + 1)}><ChevronRight /></button></div></footer></section></>;
}
