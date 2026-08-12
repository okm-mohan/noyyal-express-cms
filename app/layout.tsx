import type { Metadata } from 'next';
import './globals.css';
import './real-images.css';
export const metadata: Metadata = { title: 'Noyyal Express', description: 'Coimbatore digital news' };
export default function RootLayout({ children }: Readonly<{children: React.ReactNode}>) { return <html lang="ta"><body>{children}</body></html>; }
