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
import { AINewsCenter, AppPromotion, BusinessTechnology, CitizenReporter, CoimbatoreNews, CoimbatoreNow, DailyPoll, FeaturedVideo, JobsEducation, MegaFooter, PhotoStories, SportsEntertainment, TamilNaduNews, TempleEvents, TrendingNews } from '@/components/LowerSections';
import { getArticles } from '@/lib/news';

export default async function Home() {
  const articles = await getArticles();
  const heroArticles = articles.filter((article) => article.isBreaking);
  return <main><Header /><MainNavigation /><div className="page"><div className="hero-grid"><HeroStory articles={(heroArticles.length ? heroArticles : articles).slice(0, 3)} /><TopStories articles={(articles.filter((article) => article.isTrending).length ? articles.filter((article) => article.isTrending) : articles).slice(0, 4)} /><LiveTVCard /></div><div className="content-grid"><LatestNews articles={articles.slice(0, 6)} /><VideoNews /><aside><ShortsReels /><div className="small-cards"><FollowUs /><Newsletter /></div></aside></div><ServiceBar /><div className="lower-page"><TrendingNews /><CoimbatoreNews /><CoimbatoreNow /><FeaturedVideo /><TamilNaduNews /><SportsEntertainment /><BusinessTechnology /><PhotoStories /><TempleEvents /><JobsEducation /><AINewsCenter /><CitizenReporter /><DailyPoll /><AppPromotion /></div></div><MegaFooter /></main>;
}
