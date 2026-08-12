'use client';
import {Clock} from 'lucide-react';
import {useEffect, useState} from 'react';
const slides=[
  {image:'hero-rain.png',title:<>கோவையில்<br/>இன்று கனமழைக்கு<br/>வாய்ப்பு!</>,subtitle:'வானிலை ஆய்வு மையம் தகவல்',time:'10:15 PM'},
  {image:'top-story-2.png',title:<>கோவில் திருவிழாவில்<br/>பல்லாயிரம் பக்தர்கள்<br/>பங்கேற்பு!</>,subtitle:'மாவட்டம் முழுவதும் சிறப்பு ஏற்பாடுகள்',time:'09:45 PM'},
  {image:'video-4.png',title:<>அணைகளில் நீர்வரத்து<br/>அதிகரிப்பு; பொதுமக்களுக்கு<br/>எச்சரிக்கை!</>,subtitle:'நீர் வளத்துறை அதிகாரிகள் தகவல்',time:'09:20 PM'},
];
export function HeroStory(){const [active,setActive]=useState(0);useEffect(()=>{const interval=setInterval(()=>setActive(v=>(v+1)%slides.length),5000);return()=>clearInterval(interval)},[]);return <article className="hero card">{slides.map((slide,index)=><div className={`hero-slide ${index===active?'active':''}`} style={{backgroundImage:`linear-gradient(90deg,rgba(3,10,18,.96),rgba(3,10,18,.14)),url('/images/${slide.image}')`}} key={slide.image}><div className="hero-content"><b className="red-tag">BREAKING NEWS</b><h1>{slide.title}</h1><p>{slide.subtitle}</p><small><Clock/> {slide.time}　|　May 19, 2026</small><button className="red-button">READ FULL STORY</button></div></div>)}<div className="dots">{slides.map((_,i)=><i onClick={()=>setActive(i)} className={i===active?'active':''} key={i}/>)}</div></article>}
