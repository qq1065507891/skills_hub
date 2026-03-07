'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { SkillCard } from '@/components/skills/SkillCard';
import { skillApi, Skill } from '@/lib/api';
import { cn } from '@/lib/utils';

const categories = [
  { value: '', label: '所有分类' },
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

interface SearchFilters {
  q: string;
  category: string;
  tags: string;
  min_rating: number;
  sort: string;
}

export default function SearchPage() {
  return (
    <Suspense fallback={<div className="min-h-screen py-8 flex items-center justify-center">加载中...</div>}>
      <SearchContent />
    </Suspense>
  );
}

function SearchContent() {
  const searchParams = useSearchParams();
  
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [allTags, setAllTags] = useState<string[]>([]);
  
  const [filters, setFilters] = useState<SearchFilters>({
    q: searchParams.get('q') || '',
    category: searchParams.get('category') || '',
    tags: searchParams.get('tags') || '',
    min_rating: Number(searchParams.get('min_rating')) || 0,
    sort: searchParams.get('sort') || 'relevance',
  });

  useEffect(() => {
    fetchData();
  }, [filters]);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      const params: Record<string, any> = {};
      if (filters.q) params.q = filters.q;
      if (filters.category) params.category = filters.category;
      if (filters.tags) params.tags = filters.tags;
      if (filters.min_rating > 0) params.min_rating = filters.min_rating;
      if (filters.sort) params.sort = filters.sort;

      const response = await skillApi.searchSkills(params);
      const skillsData = Array.isArray(response) ? response : (response as any).items || [];
      setSkills(skillsData);
      
      const allTagsList = skillsData
        .map((s: any) => s.tags?.split(',').map((t: string) => t.trim()).filter(Boolean))
        .flat()
        .filter(Boolean) as string[];
      setAllTags(Array.from(new Set(allTagsList)));
      
    } catch (error) {
      console.error('Failed to fetch search results:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFilters(prev => ({ ...prev, q: e.target.value }));
  };

  const handleFilterChange = (key: keyof SearchFilters, value: string | number) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({
      q: '',
      category: '',
      tags: '',
      min_rating: 0,
      sort: 'relevance',
    });
  };

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-4">
            搜索技能
          </h1>
          <p className="text-slate-600 dark:text-slate-400">
            从社区中发现和搜索各种技能
          </p>
        </div>

        <div className="grid lg:grid-cols-4 gap-8">
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-100 dark:border-slate-700 shadow-sm sticky top-8">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
                  筛选条件
                </h3>
                <Button variant="ghost" size="sm" onClick={clearFilters}>
                  重置
                </Button>
              </div>

              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    分类
                  </label>
                  <select
                    value={filters.category}
                    onChange={(e) => handleFilterChange('category', e.target.value)}
                    className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    {categories.map(category => (
                      <option key={category.value} value={category.value}>
                        {category.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    最低评分
                  </label>
                  <select
                    value={filters.min_rating}
                    onChange={(e) => handleFilterChange('min_rating', Number(e.target.value))}
                    className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value={0}>无限制</option>
                    <option value={5}>5星及以上</option>
                    <option value={4}>4星及以上</option>
                    <option value={3}>3星及以上</option>
                    <option value={2}>2星及以上</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    排序方式
                  </label>
                  <select
                    value={filters.sort}
                    onChange={(e) => handleFilterChange('sort', e.target.value)}
                    className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="relevance">相关性</option>
                    <option value="downloads">下载量</option>
                    <option value="rating">评分</option>
                    <option value="newest">最新发布</option>
                  </select>
                </div>

                {allTags.length > 0 && (
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                      热门标签
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {allTags.slice(0, 10).map(tag => (
                        <button
                          key={tag}
                          onClick={() => handleFilterChange('tags', tag)}
                          className={cn(
                            'px-3 py-1 rounded-full text-sm transition-colors',
                            filters.tags === tag
                              ? 'bg-primary-500 text-white'
                              : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
                          )}
                        >
                          {tag}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="lg:col-span-3">
            <div className="bg-white dark:bg-slate-800 rounded-2xl p-4 border border-slate-100 dark:border-slate-700 shadow-sm mb-6">
              <div className="flex gap-4">
                <div className="flex-1 relative">
                  <svg className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  <input
                    type="text"
                    value={filters.q}
                    onChange={handleSearch}
                    placeholder="搜索技能名称或描述..."
                    className="w-full pl-12 pr-4 py-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <Button onClick={fetchData}>
                  搜索
                </Button>
              </div>
            </div>

            {loading ? (
              <div className="grid md:grid-cols-2 lg:grid-cols-2 gap-6">
                {[...Array(4)].map((_, index) => (
                  <div key={index} className="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-100 dark:border-slate-700 shadow-sm animate-pulse">
                    <div className="h-6 bg-slate-200 dark:bg-slate-700 rounded w-3/4 mb-3" />
                    <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-full mb-2" />
                    <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-2/3" />
                  </div>
                ))}
              </div>
            ) : skills.length > 0 ? (
              <>
                <div className="flex items-center justify-between mb-6">
                  <p className="text-slate-600 dark:text-slate-400">
                    找到 <span className="font-semibold text-slate-900 dark:text-white">{skills.length}</span> 个技能
                  </p>
                </div>
                <div className="grid md:grid-cols-2 lg:grid-cols-2 gap-6">
                  {skills.map(skill => (
                    <SkillCard key={skill.id} skill={skill} />
                  ))}
                </div>
              </>
            ) : (
              <div className="text-center py-16">
                <div className="w-20 h-20 bg-slate-100 dark:bg-slate-700 rounded-full flex items-center justify-center mx-auto mb-6">
                  <svg className="w-10 h-10 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
                  未找到匹配的技能
                </h3>
                <p className="text-slate-600 dark:text-slate-400 mb-6">
                  尝试调整筛选条件或搜索关键词
                </p>
                <Button onClick={clearFilters}>
                  清除筛选条件
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
