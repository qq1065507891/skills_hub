'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/Button';

const advantages = [
  {
    icon: '💯',
    title: '完全免费',
    description: '无付费技能、无订阅、无交易分成，所有技能完全免费使用',
  },
  {
    icon: '📖',
    title: '完全开源',
    description: '代码、文档、治理完全透明，社区参与度高',
  },
  {
    icon: '👥',
    title: '社区所有',
    description: '由用户和贡献者共同拥有和决策，不受单一公司控制',
  },
  {
    icon: '🛡️',
    title: '永久可用',
    description: '不依赖单一公司，抗风险能力强，确保长期稳定运行',
  },
];

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
    icon: '⚡',
    title: '高性能',
    description: '所有技能都经过严格测试，确保性能和可靠性',
  },
  {
    icon: '📦',
    title: '版本管理',
    description: '完善的版本控制机制，确保技能的稳定性和可追溯性',
  },
  {
    icon: '🔍',
    title: '智能搜索',
    description: '强大的搜索功能，快速定位你需要的技能',
  },
  {
    icon: '⭐',
    title: '评价体系',
    description: '基于用户反馈的评分和评价，帮助你选择最优质的技能',
  },
  {
    icon: '🔒',
    title: '安全扫描',
    description: '所有技能都经过安全扫描，确保代码安全可靠',
  },
  {
    icon: '🤝',
    title: '贡献机制',
    description: '完善的贡献者体系，鼓励开发者分享和改进技能',
  },
];

const comparisons = [
  {
    feature: '费用模式',
    skillhub: '完全免费',
    others: '订阅制或按次付费',
  },
  {
    feature: '所有权',
    skillhub: '社区所有',
    others: '公司专有',
  },
  {
    feature: '开源程度',
    skillhub: '完全开源',
    others: '部分或闭源',
  },
  {
    feature: '治理方式',
    skillhub: '社区治理',
    others: '公司决策',
  },
  {
    feature: '长期可用性',
    skillhub: '永久可用',
    others: '依赖公司存续',
  },
];

export default function AboutPage() {
  return (
    <div className="min-h-screen py-20">
      {/* Hero Section */}
      <section className="relative overflow-hidden py-16 lg:py-24">
        <div className="absolute inset-0 bg-gradient-to-b from-slate-50 to-white dark:from-slate-950 dark:to-slate-900" />
        <div className="relative max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-display font-extrabold tracking-tight mb-6">
            关于 <span className="gradient-text">SkillHub</span>
          </h1>
          <p className="text-xl text-slate-600 dark:text-slate-300 max-w-3xl mx-auto">
            社区驱动的开放技能平台，致力于成为 AI 代理技能生态系统的公共基础设施
          </p>
        </div>
      </section>

      {/* Introduction Section */}
      <section className="py-16 bg-white dark:bg-slate-900">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-display font-bold text-slate-900 dark:text-white mb-4">
              我们的使命
            </h2>
          </div>
          <div className="prose prose-lg dark:prose-invert max-w-none">
            <p className="text-lg text-slate-600 dark:text-slate-300 leading-relaxed">
              SkillHub 诞生于一个简单的愿景：让每一个 AI 代理都能轻松获取和使用高质量的技能。
              我们相信，技能不应该被少数公司垄断，而应该成为整个社区共享的公共资源。
            </p>
            <p className="text-lg text-slate-600 dark:text-slate-300 leading-relaxed mt-6">
              作为一个完全开源、社区驱动的平台，SkillHub 旨在建立一个公平、透明、可持续的技能生态系统，
              让每一位开发者都能在这里分享、学习和成长。
            </p>
          </div>
        </div>
      </section>

      {/* Core Advantages Section */}
      <section className="py-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-display font-bold text-slate-900 dark:text-white mb-4">
              核心优势
            </h2>
            <p className="text-lg text-slate-600 dark:text-slate-300">
              与其他平台相比，SkillHub 的独特之处
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {advantages.map((item, index) => (
              <div
                key={index}
                className="p-8 rounded-2xl bg-gradient-to-br from-primary-50 to-white dark:from-slate-800 dark:to-slate-900 border border-primary-100 dark:border-slate-700 hover:border-primary-300 dark:hover:border-primary-700 transition-all duration-300"
              >
                <div className="text-4xl mb-4">{item.icon}</div>
                <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
                  {item.title}
                </h3>
                <p className="text-slate-600 dark:text-slate-300">
                  {item.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Comparison Section */}
      <section className="py-20 bg-white dark:bg-slate-900">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-display font-bold text-slate-900 dark:text-white mb-4">
              竞品对比
            </h2>
            <p className="text-lg text-slate-600 dark:text-slate-300">
              看看 SkillHub 与其他平台的区别
            </p>
          </div>
          <div className="overflow-hidden rounded-2xl border border-slate-200 dark:border-slate-700">
            <table className="w-full">
              <thead>
                <tr className="bg-slate-50 dark:bg-slate-800">
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-900 dark:text-white">
                    特性
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-primary-600 dark:text-primary-400">
                    SkillHub
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-slate-600 dark:text-slate-400">
                    其他平台
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
                {comparisons.map((item, index) => (
                  <tr key={index} className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                    <td className="px-6 py-4 text-sm font-medium text-slate-900 dark:text-white">
                      {item.feature}
                    </td>
                    <td className="px-6 py-4 text-sm text-primary-600 dark:text-primary-400 font-medium">
                      {item.skillhub}
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-600 dark:text-slate-400">
                      {item.others}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-display font-bold text-slate-900 dark:text-white mb-4">
              平台特色
            </h2>
            <p className="text-lg text-slate-600 dark:text-slate-300">
              我们提供的强大功能
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((item, index) => (
              <div
                key={index}
                className="p-6 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 hover:border-primary-200 dark:hover:border-primary-700 transition-all duration-300"
              >
                <div className="text-3xl mb-3">{item.icon}</div>
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
                  {item.title}
                </h3>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  {item.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="gradient-bg rounded-3xl p-8 md:p-12 text-center relative overflow-hidden">
            <div className="absolute inset-0 bg-black/10" />
            <div className="relative">
              <h2 className="text-3xl md:text-4xl font-display font-bold text-white mb-4">
                加入 SkillHub 社区
              </h2>
              <p className="text-lg text-white/80 mb-8 max-w-2xl mx-auto">
                与全球开发者一起构建更智能的 AI 应用
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <Link href="/skills">
                  <Button variant="secondary" size="lg" className="w-full sm:w-auto bg-white text-slate-900 hover:bg-slate-100">
                    浏览技能库
                  </Button>
                </Link>
                <Link href="/">
                  <Button variant="ghost" size="lg" className="w-full sm:w-auto text-white border-2 border-white/30 hover:bg-white/10">
                    返回首页
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
