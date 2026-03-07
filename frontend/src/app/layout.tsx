import type { Metadata } from 'next';
import './globals.css';
import { Header } from '@/components/common/Header';
import { AuthProvider } from '@/lib/auth';
import { ScrollToTop } from '@/components/common/ScrollToTop';

export const metadata: Metadata = {
  title: 'SkillHub - 社区驱动的开放技能平台',
  description: 'SkillHub 是一个社区驱动的开放技能平台，致力于成为 AI 代理技能生态系统的公共基础设施。',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN" className="scroll-smooth">
      <body className="bg-slate-50 dark:bg-slate-950 min-h-screen">
        <AuthProvider>
          <ScrollToTop />
          <Header />
          <main className="pt-16">
            {children}
          </main>
        </AuthProvider>
      </body>
    </html>
  );
}
