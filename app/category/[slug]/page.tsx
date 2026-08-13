import { notFound } from 'next/navigation';
import { Header } from '@/components/Header';
import { MainNavigation } from '@/components/MainNavigation';
import { MegaFooter } from '@/components/LowerSections';
import { PublicNewsGrid } from '@/components/PublicNewsGrid';
import { getHomepageData } from '@/lib/home';
export default async function PublicCategoryPage({params}:{params:Promise<{slug:string}>}){const {slug}=await params;const {articles}=await getHomepageData();const categoryArticles=articles.filter(article=>article.categorySlug===slug);if(!categoryArticles.length)notFound();const category=categoryArticles[0].categoryName;return <main><Header breakingHeadline={categoryArticles.find(article=>article.isBreaking)?.title}/><MainNavigation/><section className="public-list-page"><p className="article-eyebrow">CATEGORY</p><h1>{category}</h1><p>{categoryArticles.length} latest articles from Noyyal Express.</p><PublicNewsGrid articles={categoryArticles}/></section><MegaFooter/></main>}
