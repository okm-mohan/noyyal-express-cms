import Link from 'next/link';
import { Activity, CirclePlay, MonitorPlay, Radio, Signal, Sparkles, Tv, Users } from 'lucide-react';
import { Pool } from 'pg';

const pool = new Pool({ connectionString: process.env.DATABASE_URL });

export default async function LiveTV() {
  const { rows } = await pool.query<{ id: string; title: string; stream_url: string; is_live: boolean }>('SELECT id, title, stream_url, is_live FROM "LiveStream" ORDER BY updated_at DESC LIMIT 1');
  const stream = rows[0];
  const onAir = stream?.is_live ?? false;

  return <>
    <header className="live-hero">
      <div><p className="breadcrumbs">Dashboard / Videos &amp; Live / <span>Live TV</span></p><span><Sparkles /> LIVE CONTROL ROOM</span><h1>Live TV</h1><p>Monitor the broadcast, manage the stream, and keep your newsroom on air.</p></div>
      <Link className="live-go" href="/admin/live-tv/setup"><Radio /> {onAir ? 'MANAGE LIVE' : 'SET UP LIVE TV'}</Link>
    </header>
    <section className="live-status-card">
      <div className="live-preview"><Tv /><b>{onAir ? 'LIVE' : 'OFF AIR'}</b><small>{onAir ? 'Broadcasting now' : 'No active live broadcast'}</small><i><CirclePlay /></i></div>
      <div className="live-status-copy"><span className={onAir ? 'on-air' : 'off-air'}><i /> {onAir ? 'ON AIR' : 'OFF AIR'}</span><h2>{stream?.title || 'Noyyal Express Live'}</h2><p>{onAir ? 'Your live feed is available to viewers. Monitor the stream quality and newsroom updates from here.' : 'Configure a live stream URL to start broadcasting breaking updates, bulletins, and special coverage.'}</p><div><article><Users /><p><small>LIVE VIEWERS</small><b>0</b></p></article><article><Signal /><p><small>STREAM HEALTH</small><b>{onAir ? 'Good' : 'Standby'}</b></p></article></div>{stream && <a href={stream.stream_url} target="_blank" rel="noreferrer">OPEN STREAM URL →</a>}</div>
    </section>
    <section className="live-tools"><article><MonitorPlay /><h3>Broadcast console</h3><p>Configure the stream destination and broadcast title.</p><Link href="/admin/live-tv/setup">OPEN CONSOLE →</Link></article><article><Activity /><h3>Stream health</h3><p>Confirm stream readiness before going live.</p><span>{onAir ? 'SIGNAL ACTIVE' : 'WAITING FOR SIGNAL'}</span></article><article><Radio /><h3>Live ticker</h3><p>Publish urgent newsroom updates during broadcasts.</p><span>COMING SOON</span></article></section>
  </>;
}
