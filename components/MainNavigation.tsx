import {ChevronDown, Home} from 'lucide-react';
export function MainNavigation(){const links=['LATEST NEWS','COIMBATORE','TAMIL NADU','INDIA','BUSINESS','SPORTS','ENTERTAINMENT','TECHNOLOGY','LIFESTYLE','MORE'];return <nav className="main-nav"><a className="home"><Home/></a>{links.map(x=><a key={x}>{x}{(x==='COIMBATORE'||x==='MORE')&&<ChevronDown/>}</a>)}</nav>}
