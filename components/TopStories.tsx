import {topStories} from '@/data/topStories';
export function TopStories(){return <section className="card top-stories"><h2>TOP STORIES</h2>{topStories.map((s,i)=><article className="top-item" key={s.title}><span>{i+1}</span><img src={`/images/${s.image}`} alt=""/><div><h3>{s.title}</h3><small>{s.time}</small></div></article>)}</section>}
