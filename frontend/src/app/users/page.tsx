
'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/auth';
import { contributionApi, ContributionSummary, RankingItem } from '@/lib/api';

const actionTypeLabels: Record<string, string> = {
  'create_skill': '创建技能',
  'update_skill': '更新技能',
  'write_review': '撰写评价',
  'report_issue': '报告问题',
  'fix_issue': '修复问题',
  'documentation': '文档贡献',
  'other': '其他贡献',
};

export default function UsersPage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'ranking' | 'my'>('ranking');
  const [ranking, setRanking] = useState<RankingItem[]>([]);
  const [mySummary, setMySummary] = useState<ContributionSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (activeTab === 'ranking') {
      fetchRanking();
    } else if (user) {
      fetchMySummary();
    } else {
      setError('请先登录');
      setLoading(false);
    }
  }, [activeTab, user]);

  const fetchRanking = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await contributionApi.getRanking();
      setRanking(response.items || []);
    } catch (err) {
      console.error('获取排行榜失败:', err);
      setError('获取排行榜失败，请稍后重试');
      setRanking([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchMySummary = async () => {
    if (!user) return;
    
    try {
      setLoading(true);
      setError(null);
      const summary = await contributionApi.getUserSummary(user.id);
      setMySummary(summary);
    } catch (err) {
      console.error('获取用户贡献度失败:', err);
      setError('获取用户贡献度失败，请稍后重试');
      setMySummary(null);
    } finally {
      setLoading(false);
    }
  };

  const getRankColor = (rank: number) => {
    switch (rank) {
      case 1:
        return 'text-yellow-500';
      case 2:
        return 'text-slate-400';
      case 3:
        return 'text-amber-600';
      default:
        return 'text-slate-600 dark:text-slate-400';
    }
  };

  const getRankBadge = (rank: number) => {
    switch (rank) {
      case 1:
        return (
          <span className="flex items-center justify-center w-8 h-8 rounded-full bg-yellow-100 dark:bg-yellow-900/30">
            <svg className="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          </span>
        );
      case 2:
        return (
          <span className="flex items-center justify-center w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-700">
            <svg className="w-5 h-5 text-slate-400" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          </span>
        );
      case 3:
        return (
          <span className="flex items-center justify-center w-8 h-8 rounded-full bg-amber-100 dark:bg-amber-900/30">
            <svg className="w-5 h-5 text-amber-600" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          </span>
        );
      default:
        return (
          <span className={`flex items-center justify-center w-8 h-8 rounded-full bg-slate-50 dark:bg-slate-800 font-bold ${getRankColor(rank)}`}>
            {rank}
          </span>
        );
    }
  };

  const StatCard = ({ title, value, icon: Icon, color }: { title: string; value: number | string; icon: any; color: string }) => (
    <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-100 dark:border-slate-700 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{title}</p>
          <p className="text-3xl font-bold text-slate-900 dark:text-white mt-2">{value}</p>
        </div>
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-4">
            社区贡献
          </h1>
          <p className="text-slate-600 dark:text-slate-400">
            查看社区贡献排行榜和个人贡献记录
          </p>
        </div>

        <div className="flex gap-4 mb-8 border-b border-slate-200 dark:border-slate-700">
          <button
            onClick={() => setActiveTab('ranking')}
            className={`pb-4 px-2 border-b-2 font-medium transition-colors ${
              activeTab === 'ranking'
                ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                : 'border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300'
            }`}
          >
            贡献排行榜
          </button>
          {user && (
            <button
              onClick={() => setActiveTab('my')}
              className={`pb-4 px-2 border-b-2 font-medium transition-colors ${
                activeTab === 'my'
                  ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300'
              }`}
            >
              我的贡献
            </button>
          )}
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-slate-200 dark:border-slate-700 border-t-primary-500"></div>
          </div>
        ) : error ? (
          <div className="text-center py-16">
            <div className="w-20 h-20 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg className="w-10 h-10 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
              {error}
            </h3>
            {error === '请先登录' && (
              <p className="text-slate-600 dark:text-slate-400 mb-6">
                登录后可查看您的个人贡献记录
              </p>
            )}
            <button
              onClick={activeTab === 'ranking' ? fetchRanking : (user ? fetchMySummary : undefined)}
              className="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
            >
              重试
            </button>
          </div>
        ) : activeTab === 'ranking' ? (
          <div>
            {ranking.length > 0 ? (
              <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 shadow-sm overflow-hidden">
                <div className="divide-y divide-slate-100 dark:divide-slate-700">
                  {ranking.map((user, index) => (
                    <div key={user.user_id} className="p-6 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
                      <div className="flex items-center gap-6">
                        <div className="flex-shrink-0">
                          {getRankBadge(user.rank)}
                        </div>
                        <div className="flex-shrink-0">
                          {user.avatar_url ? (
                            <img
                              src={user.avatar_url}
                              alt={user.username}
                              className="w-12 h-12 rounded-full"
                            />
                          ) : (
                            <div className="w-12 h-12 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
                              <span className="text-primary-600 dark:text-primary-400 font-semibold">
                                {user.username.charAt(0).toUpperCase()}
                              </span>
                            </div>
                          )}
                        </div>
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
                            {user.username}
                          </h3>
                        </div>
                        <div className="text-right">
                          <p className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                            {user.total_points}
                          </p>
                          <p className="text-sm text-slate-500 dark:text-slate-400">贡献积分</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-center py-16">
                <div className="w-20 h-20 bg-slate-100 dark:bg-slate-700 rounded-full flex items-center justify-center mx-auto mb-6">
                  <svg className="w-10 h-10 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
                  暂无贡献记录
                </h3>
                <p className="text-slate-600 dark:text-slate-400">
                  成为第一个贡献者吧！
                </p>
              </div>
            )}
          </div>
        ) : activeTab === 'my' && !user ? (
          <div className="text-center py-16">
            <div className="w-20 h-20 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg className="w-10 h-10 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
              请先登录
            </h3>
            <p className="text-slate-600 dark:text-slate-400 mb-6">
              登录后可查看您的个人贡献记录
            </p>
          </div>
        ) : (
          <div>
            {mySummary && (
              <>
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                  <StatCard
                    title="总贡献积分"
                    value={mySummary.total_points}
                    icon={(props: any) => (
                      <svg {...props} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    )}
                    color="bg-primary-500"
                  />
                  <StatCard
                    title="总贡献次数"
                    value={mySummary.total_actions}
                    icon={(props: any) => (
                      <svg {...props} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    )}
                    color="bg-emerald-500"
                  />
                  <StatCard
                    title="社区排名"
                    value={mySummary.rank || '-'}
                    icon={(props: any) => (
                      <svg {...props} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.879 16.121A3 3 0 1012.015 11L11 14H9c0 .768.293 1.536.879 2.121z" />
                      </svg>
                    )}
                    color="bg-amber-500"
                  />
                  <Link href="/users/skills" className="block">
                    <StatCard
                      title="创建技能"
                      value={mySummary.create_skill_count}
                      icon={(props: any) => (
                        <svg {...props} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                        </svg>
                      )}
                      color="bg-violet-500"
                    />
                  </Link>
                </div>

                <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 shadow-sm p-6">
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-6">
                    贡献明细
                  </h3>
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {[
                      { key: 'create_skill_count', label: '创建技能', icon: '➕' },
                      { key: 'update_skill_count', label: '更新技能', icon: '✏️' },
                      { key: 'write_review_count', label: '撰写评价', icon: '⭐' },
                      { key: 'report_issue_count', label: '报告问题', icon: '🐛' },
                      { key: 'fix_issue_count', label: '修复问题', icon: '🔧' },
                      { key: 'documentation_count', label: '文档贡献', icon: '📝' },
                      { key: 'other_count', label: '其他贡献', icon: '📦' },
                    ].map((item) => (
                      <div key={item.key} className="flex items-center gap-3 p-4 bg-slate-50 dark:bg-slate-700/50 rounded-xl">
                        <span className="text-2xl">{item.icon}</span>
                        <div>
                          <p className="text-sm text-slate-500 dark:text-slate-400">{item.label}</p>
                          <p className="text-xl font-bold text-slate-900 dark:text-white">
                            {String(mySummary[item.key as keyof ContributionSummary] ?? 0)}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

