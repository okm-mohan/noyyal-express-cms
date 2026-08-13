'use client';
import { Clock } from 'lucide-react';
import { useEffect, useState } from 'react';
import type { Article } from '@/lib/news';

export function HeroStory({ articles }: { articles: Article[] }) {
  const [active, setActive] = useState(0);
  useEffect(() => {
    if (articles.length < 2) return;
    const interval = setInterval(() => setActive((value) => (value + 1) % articles.length), 5000);
    return () => clearInterval(interval);
  }, [articles.length]);
  if (!articles.length) return null;
  return <article className="hero card">{articles.map((article, index) => <div className={`hero-slide ${index === active ? 'active' : ''}`} style={{ backgroundImage: `linear-gradient(90deg,rgba(3,10,18,.96),rgba(3,10,18,.14)),url(${article.imageUrl || '/images/hero-rain.png'})` }} key={article.id}><div className="hero-content"><b className="red-tag">{article.isBreaking ? 'BREAKING NEWS' : article.categoryName}</b><h1>{article.title}</h1><p>{article.excerpt || article.categoryName}</p><small><Clock /> {article.publishedAt ? new Date(article.publishedAt).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' }) : 'Just now'}</small><button className="red-button">READ FULL STORY</button></div></div>)}<div className="dots">{articles.map((article, index) => <i onClick={() => setActive(index)} className={index === active ? 'active' : ''} key={article.id} />)}</div></article>;
}
