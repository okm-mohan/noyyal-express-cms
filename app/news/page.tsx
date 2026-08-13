import { Header } from '@/components/Header';
import { MainNavigation } from '@/components/MainNavigation';
import { MegaFooter } from '@/components/LowerSections';
import { PublicNewsGrid } from '@/components/PublicNewsGrid';
import { getHomepageData } from '@/lib/home';
export default async function LatestNewsPage(){const {articles}=await getHomepageData();return <main><Header breakingHeadline={articles.find(article=>article.isBreaking)?.title}/><MainNavigation/><section className="public-list-page"><p className="article-eyebrow">NOYYAL EXPRESS NEWSROOM</p><h1>Latest News</h1><p>Latest verified news reports from our database-powered newsroom.</p><PublicNewsGrid articles={articles}/></section><MegaFooter/></main>}
