import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AI Ads Studio',
  description: 'AI-powered marketing studio for businesses',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen flex flex-col font-sans antialiased text-slate-50 bg-slate-950">
        <nav className="glass sticky top-0 z-50 p-4 border-b border-white/10">
          <div className="container mx-auto flex items-center justify-between">
            <a href="/" className="text-xl font-bold bg-gradient-to-r from-violet-400 to-blue-400 bg-clip-text text-transparent">AI Ads Studio</a>
            <div className="space-x-4">
              <a href="/" className="hover:text-violet-400 transition-colors">Dashboard</a>
            </div>
          </div>
        </nav>
        <main className="container mx-auto p-4 md:p-8 flex-grow">
          {children}
        </main>
      </body>
    </html>
  );
}
