'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {ChevronDown, Home} from 'lucide-react';
const links=[['LATEST NEWS','/news'],['COIMBATORE','/category/coimbatore'],['TAMIL NADU','/category/tamil-nadu'],['INDIA','/category/india'],['BUSINESS','/category/business'],['SPORTS','/category/sports'],['ENTERTAINMENT','/category/entertainment'],['TECHNOLOGY','/category/technology'],['LIFESTYLE','/category/lifestyle']] as const;
export function MainNavigation(){const pathname=usePathname();return <nav className="main-nav" aria-label="Primary navigation"><Link href="/" className={`home ${pathname==='/'?'active':''}`} aria-label="Home"><Home/></Link>{links.map(([label,href])=><Link href={href} className={pathname===href?'active':''} key={label}><span>{label}</span>{label==='COIMBATORE'&&<ChevronDown/>}</Link>)}<a className="more-nav" href="#footer"><span>MORE</span><ChevronDown/></a></nav>}