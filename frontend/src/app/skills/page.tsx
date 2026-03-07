'use client';

import { useState, useEffect, useMemo } from 'react';
import { Button } from '@/components/ui/Button';
import { SkillCard } from '@/components/skills/SkillCard';
import { skillApi, Skill } from '@/lib/api';
import { cn } from '@/lib/utils';

const categories = [
  { value: 'all', label: '全部' },
  { value: '开发工具', label: '开发工具' },
  { value: '机器学习', label: '机器学习' },
  { value: '数据分析', label: '数据分析' },
  { value: 'Web 开发', label: 'Web 开发' },
  { value: '移动开发', label: '移动开发' },
  { value: '测试', label: '测试' },
  { value: 'DevOps', label: 'DevOps' },
  { value: '文档', label: '文档' },
  { value: '设计', label: '设计' },
  { value: '安全', label: '安全' },
  { value: '其他', label: '其他' },
];

const sortOptions = [
  { value: 'downloads', label: '下载量' },
  { value: 'rating', label: '评分' },
  { value: 'newest', label: '最新' },
  { value: 'name', label: '名称' },
];

export default function SkillsPage() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [sortBy, setSortBy] = useState('downloads');

  useEffect(() => {
    const fetchSkills = async () => {
      try {
        const data = await skillApi.getSkills({ limit: 100 });
        setSkills(data || []);
      } catch (error) {
        console.error('Failed to fetch skills:', error);
        setSkills([]);
      } finally {
        setLoading(false);
      }
    };

    fetchSkills();
  }, []);

  const filteredSkills = useMemo(() => {
    let result = [...skills];

    // Filter by category
    if (selectedCategory !== 'all') {
      result = result.filter((skill) => skill.category === selectedCategory);
    }

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(
        (skill) =>
          skill.name.toLowerCase().includes(query) ||
          (skill.description && skill.description.toLowerCase().includes(query))
      );
    }

    // Sort
    result.sort((a, b) => {
      switch (sortBy) {
        case 'downloads':
          return b.download_count - a.download_count;
        case 'rating':
          return b.rating - a.rating;
        case 'newest':
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        case 'name':
          return a.name.localeCompare(b.name);
        default:
          return 0;
      }
    });

    return result;
  }, [skills, selectedCategory, searchQuery, sortBy]);

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Page Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-display font-bold text-slate-900 dark:text-white mb-4">
            技能库
          </h1>
          <p className="text-lg text-slate-600 dark:text-slate-300 max-w-2xl mx-auto">
            发现并使用数千个高质量的 AI 代理技能
          </p>
        </div>

        {/* Search and Filters */}
        <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-100 dark:border-slate-700 shadow-sm mb-8">
          <div className="flex flex-col lg:flex-row gap-6">
            {/* Search Input */}
            <div className="flex-1">
              <div className="relative">
                <svg
                  className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
                <input
                  type="text"
                  placeholder="搜索技能..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                />
              </div>
            </div>

            {/* Sort Dropdown */}
            <div className="w-full lg:w-48">
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                排序
              </label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              >
                {sortOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Categories */}
          <div className="mt-6">
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">
              分类
            </label>
            <div className="flex flex-wrap gap-2">
              {categories.map((category) => (
                <button
                  key={category.value}
                  onClick={() => setSelectedCategory(category.value)}
                  className={cn(
                    'px-4 py-2 rounded-full text-sm font-medium transition-all duration-200',
                    selectedCategory === category.value
                      ? 'gradient-bg text-white shadow-lg'
                      : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
                  )}
                >
                  {category.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Results Count */}
        <div className="flex items-center justify-between mb-6">
          <p className="text-slate-600 dark:text-slate-300">
            找到 <span className="font-semibold text-slate-900 dark:text-white">{filteredSkills.length}</span> 个技能
          </p>
        </div>

        {/* Skills Grid */}
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
        ) : filteredSkills.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredSkills.map((skill, index) => (
              <SkillCard key={skill.id} skill={skill} index={index} showInstallCommand={true} />
            ))}
          </div>
        ) : (
          <div className="text-center py-20">
            <div className="w-20 h-20 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg
                className="w-10 h-10 text-slate-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
              没有找到技能
            </h3>
            <p className="text-slate-600 dark:text-slate-300">
              尝试调整搜索条件或分类
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
