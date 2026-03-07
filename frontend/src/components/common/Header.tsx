'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/Button';
import { useAuth } from '@/lib/auth';
import { LoginModal } from '@/components/common/LoginModal';
import { PublishSkillModal } from '@/components/common/PublishSkillModal';

const navItems = [
  { name: '首页', href: '/' },
  { name: '关于', href: '/about' },
  { name: '技能', href: '/skills' },
  { name: '搜索', href: '/search' },
  { name: '用户', href: '/users' },
];

export const Header = () => {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showPublishModal, setShowPublishModal] = useState(false);

  const handlePublishClick = () => {
    if (!user) {
      setShowLoginModal(true);
    } else {
      setShowPublishModal(true);
    }
  };

  const handleLoginClick = () => {
    setShowLoginModal(true);
  };

  const handleLogout = () => {
    logout();
  };

  return (
    <>
      <header className="fixed top-0 left-0 right-0 z-50 glass border-b border-slate-200/50 dark:border-slate-700/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-8 h-8 gradient-bg rounded-xl flex items-center justify-center">
                <span className="text-white font-bold text-lg">S</span>
              </div>
              <span className="font-display font-bold text-xl bg-clip-text gradient-text">
                SkillHub
              </span>
            </Link>

            <nav className="hidden md:flex items-center gap-8">
              {navItems.map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    'text-sm font-medium transition-colors hover:text-primary-500',
                    pathname === item.href
                      ? 'text-primary-600 dark:text-primary-400'
                      : 'text-slate-600 dark:text-slate-300'
                  )}
                >
                  {item.name}
                </Link>
              ))}
            </nav>

            <div className="flex items-center gap-3">
              {user ? (
                <>
                  <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
                    <div className="w-8 h-8 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center">
                      <span className="text-primary-600 dark:text-primary-400 font-semibold">
                        {user.username.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <span>{user.username}</span>
                  </div>
                  <Button variant="outline" size="sm" onClick={handleLogout}>
                    退出
                  </Button>
                  <Button variant="gradient" size="sm" onClick={() => setShowPublishModal(true)}>
                    发布技能
                  </Button>
                </>
              ) : (
                <>
                  <Button variant="outline" size="sm" onClick={handleLoginClick}>
                    登录
                  </Button>
                  <Button variant="gradient" size="sm" onClick={handlePublishClick}>
                    发布技能
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      <LoginModal isOpen={showLoginModal} onClose={() => setShowLoginModal(false)} />
      <PublishSkillModal isOpen={showPublishModal} onClose={() => setShowPublishModal(false)} />
    </>
  );
};
