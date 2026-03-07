'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { SkillCard } from '@/components/skills/SkillCard';
import { skillApi, Skill } from '@/lib/api';
import { LoginModal } from '@/components/common/LoginModal';

const features = [
  {
    icon: '🚀',
    title: '快速探索',
    description: '发现数以千计的高质量技能，轻松找到适合你项目的解决方案',
  },
  {
    icon: '🔧',
    title: '即插即用',
    description: '一键安装和部署技能，无需复杂配置，让你专注于开发',
  },
  {
    icon: '👥',
    title: '社区驱动',
    description: '由全球开发者共同维护，持续更新和改进技能生态',
  },
  {
    icon: '⚡',
    title: '高性能',
    description: '所有技能都经过严格测试，确保性能和可靠性',
  },
];

export default function Home() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [showLoginModal, setShowLoginModal] = useState(false);

  useEffect(() => {
    const fetchSkills = async () => {
      try {
        const data = await skillApi.getSkills({ limit: 6 });
        setSkills(data);
      } catch (error) {
        console.error('Failed to fetch skills:', error);
        setSkills([
          {
            id: 1,
            name: 'React 开发助手',
            slug_name: 'react-dev-assistant',
            description: '提供 React 组件开发的最佳实践和代码生成功能',
            version: '2.1.0',
            license: 'MIT',
            category: 'web',
            author_id: 1,
            download_count: 1234,
            rating: 4.8,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          {
            id: 2,
            name: '代码审查工具',
            slug_name: 'code-review-tool',
            description: '自动检测代码质量问题，提供详细的改进建议',
            version: '1.5.3',
            license: 'Apache-2.0',
            category: 'tool',
            author_id: 2,
            download_count: 856,
            rating: 4.5,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          {
            id: 3,
            name: '数据库查询优化',
            slug_name: 'db-query-optimizer',
            description: '智能分析和优化 SQL 查询，提升数据库性能',
            version: '3.0.0',
            license: 'MIT',
            category: 'ai',
            author_id: 3,
            download_count: 2100,
            rating: 4.9,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchSkills();
  }, []);

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden py-24 lg:py-32">
        {/* Background Gradient */}
        <div className="absolute inset-0 bg-gradient-to-b from-slate-50 to-white dark:from-slate-950 dark:to-slate-900" />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-primary-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-0 w-[600px] h-[600px] bg-accent-500/10 rounded-full blur-3xl" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-50 dark:bg-primary-900/20 border border-primary-100 dark:border-primary-800 mb-8">
              <span className="w-2 h-2 bg-accent-500 rounded-full animate-pulse" />
              <span className="text-sm font-medium text-primary-700 dark:text-primary-300">
                全新上线 · 现已开放公测
              </span>
            </div>

            <h1 className="text-5xl md:text-6xl lg:text-7xl font-display font-extrabold tracking-tight mb-6">
              <span className="text-slate-900 dark:text-white">构建更智能的</span>
              <br />
              <span className="gradient-text">AI 应用</span>
            </h1>

            <p className="mt-6 max-w-2xl mx-auto text-xl text-slate-600 dark:text-slate-300">
              SkillHub 是一个社区驱动的开放技能平台，致力于成为 AI 代理技能生态系统的公共基础设施。
            </p>

            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/skills">
                <Button variant="gradient" size="xl" className="w-full sm:w-auto">
                  浏览技能库
                </Button>
              </Link>
              <Link href="/about">
                <Button variant="outline" size="xl" className="w-full sm:w-auto">
                  了解更多
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white dark:bg-slate-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-display font-bold text-slate-900 dark:text-white mb-4">
              为什么选择 SkillHub？
            </h2>
            <p className="text-lg text-slate-600 dark:text-slate-300 max-w-2xl mx-auto">
              我们提供一套完整的工具和服务，帮助你快速构建、部署和分享 AI 技能
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="p-8 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-700 hover:border-primary-200 dark:hover:border-primary-800 transition-all duration-300"
              >
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-slate-600 dark:text-slate-300">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Popular Skills Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-12">
            <div>
              <h2 className="text-3xl md:text-4xl font-display font-bold text-slate-900 dark:text-white mb-2">
                热门技能
              </h2>
              <p className="text-slate-600 dark:text-slate-300">
                发现社区最受欢迎的技能
              </p>
            </div>
            <Link href="/skills">
              <Button variant="outline" className="hidden md:inline-flex">
                查看全部
              </Button>
            </Link>
          </div>

          {loading ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(6)].map((_, index) => (
                <div
                  key={index}
                  className="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-100 dark:border-slate-700"
                >
                  <div className="space-y-4">
                    <div className="h-4 bg-slate-100 dark:bg-slate-700 rounded w-1/3 animate-pulse" />
                    <div className="h-6 bg-slate-100 dark:bg-slate-700 rounded w-3/4 animate-pulse" />
                    <div className="h-4 bg-slate-100 dark:bg-slate-700 rounded w-full animate-pulse" />
                    <div className="h-4 bg-slate-100 dark:bg-slate-700 rounded w-2/3 animate-pulse" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {skills.map((skill, index) => (
                <SkillCard key={skill.id} skill={skill} index={index} />
              ))}
            </div>
          )}

          <div className="mt-10 text-center md:hidden">
            <Link href="/skills">
              <Button variant="outline">查看全部技能</Button>
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="gradient-bg rounded-3xl p-8 md:p-16 text-center relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-full bg-black/10" />
            <div className="absolute top-10 left-10 w-32 h-32 bg-white/10 rounded-full blur-2xl" />
            <div className="absolute bottom-10 right-10 w-40 h-40 bg-white/10 rounded-full blur-2xl" />

            <div className="relative">
              <h2 className="text-3xl md:text-4xl font-display font-bold text-white mb-4">
                准备好开始了吗？
              </h2>
              <p className="text-lg text-white/80 mb-8 max-w-2xl mx-auto">
                加入 SkillHub 社区，与全球开发者一起构建更智能的 AI 应用
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <Button
                  variant="secondary"
                  size="lg"
                  className="w-full sm:w-auto bg-white text-slate-900 hover:bg-slate-100"
                  onClick={() => setShowLoginModal(true)}
                >
                  立即注册
                </Button>
                <Link href="/about">
                  <Button
                    variant="ghost"
                    size="lg"
                    className="w-full sm:w-auto text-white border-2 border-white/30 hover:bg-white/10"
                  >
                    了解详情
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      <LoginModal isOpen={showLoginModal} onClose={() => setShowLoginModal(false)} />
    </div>
  );
}
