import { Header } from '@/components/Header';
import { MainNavigation } from '@/components/MainNavigation';
import { HeroStory } from '@/components/HeroStory';
import { TopStories } from '@/components/TopStories';
import { LiveTVCard } from '@/components/LiveTVCard';
import { LatestNews } from '@/components/LatestNews';
import { VideoNews } from '@/components/VideoNews';
import { ShortsReels } from '@/components/ShortsReels';
import { FollowUs } from '@/components/FollowUs';
import { Newsletter } from '@/components/Newsletter';
import { ServiceBar } from '@/components/ServiceBar';
import { DatabaseNewsSections } from '@/components/DatabaseNewsSections';
import { MegaFooter } from '@/components/LowerSections';
import { getHomepageData } from '@/lib/home';

export default async function Home() {
  const { articles, videos, shorts } = await getHomepageData();
  const breaking = articles.filter((article) => article.isBreaking);
  const trending = articles.filter((article) => article.isTrending);
  const headline = (breaking[0] || articles[0])?.title;
  return <main><Header breakingHeadline={headline}/><MainNavigation/><div className="page"><div className="hero-grid"><HeroStory articles={(breaking.length ? breaking : articles).slice(0, 3)}/><TopStories articles={(trending.length ? trending : articles).slice(0, 4)}/><LiveTVCard/></div><div className="content-grid"><LatestNews articles={articles.slice(0, 6)}/><VideoNews videos={videos}/><aside><ShortsReels shorts={shorts}/><div className="small-cards"><FollowUs/><Newsletter/></div></aside></div><ServiceBar/><DatabaseNewsSections articles={articles}/></div><MegaFooter/></main>;
}