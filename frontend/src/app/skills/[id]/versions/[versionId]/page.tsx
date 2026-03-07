'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { skillApi, Skill } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import { cn } from '@/lib/utils';
import { useAuth } from '@/lib/auth';

// 分类颜色映射
const categoryColors: Record<string, string> = {
  'web': 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  'ai': 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
  'tool': 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400',
  'testing': 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
  'design': 'bg-pink-100 text-pink-700 dark:bg-pink-900/30 dark:text-pink-400',
  'productivity': 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
};

const getCategoryColor = (category?: string) => {
  if (!category) return 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300';
  const lowerCat = category.toLowerCase();
  return categoryColors[lowerCat] || categoryColors['tool'];
};

export default function SkillVersionPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const skillId = Number(params.id);
  const versionId = Number(params.versionId);

  const [version, setVersion] = useState<Skill | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    if (!skillId || !versionId) return;

    const fetchVersion = async () => {
      try {
        setLoading(true);
        const versionData = await skillApi.getSkillVersion(skillId, versionId);
        setVersion(versionData);
      } catch (err: any) {
        console.error('Failed to fetch version:', err);
        setError('无法加载历史版本信息');
      } finally {
        setLoading(false);
      }
    };

    fetchVersion();
  }, [skillId, versionId]);

  // 安装命令
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
  const registryUrl = typeof window !== 'undefined' ? apiUrl.replace('/api/v1', '/npm') : 'http://localhost:8000/npm';
  const installCommand = version && user ? `npm install ${version.slug_name}@${version.version} --registry=${registryUrl} --foreground-scripts` : '';

  // 复制安装命令
  const handleCopyCommand = () => {
    if (!user) {
      alert('请先登录后查看安装命令');
      return;
    }
    if (!installCommand) return;
    navigator.clipboard.writeText(installCommand);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // 下载历史版本
  const handleDownload = async () => {
    if (!user) {
      alert('请先登录后再下载技能包');
      return;
    }
    if (!version) return;
    
    try {
      setDownloading(true);
      // 增加下载计数
      await skillApi.downloadVersion(skillId, versionId);
      
      // 触发文件下载
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
      const token = localStorage.getItem('auth_token');
      
      const response = await fetch(`${apiUrl}/install/${skillId}/download-file?version=${version.version}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) throw new Error('Download failed');
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${version.slug_name}-${version.version}.tgz`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      // 更新本地下载计数
      setVersion({ ...version, download_count: version.download_count + 1 });
    } catch (err: any) {
      console.error('Download failed:', err);
      alert('下载失败，请稍后重试');
    } finally {
      setDownloading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white dark:bg-slate-800 rounded-2xl p-8 border border-slate-100 dark:border-slate-700 shadow-sm">
            <div className="space-y-6 animate-pulse">
              <div className="h-8 bg-slate-200 dark:bg-slate-700 rounded w-1/3" />
              <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-1/2" />
              <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-2/3" />
              <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-full" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !version) {
    return (
      <div className="min-h-screen py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="bg-white dark:bg-slate-800 rounded-2xl p-8 border border-slate-100 dark:border-slate-700 shadow-sm">
            <h2 className="text-2xl font-semibold text-slate-900 dark:text-white mb-4">
              版本未找到
            </h2>
            <p className="text-slate-600 dark:text-slate-300 mb-6">
              {error || '该历史版本可能已被删除或不存在'}
            </p>
            <Button onClick={() => router.push(`/skills/${skillId}`)}>
              返回技能详情
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 返回按钮 */}
        <div className="mb-6 flex items-center gap-4">
          <Link href={`/skills/${skillId}`}>
            <Button variant="outline" size="sm">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              返回技能详情
            </Button>
          </Link>
          <span className="text-sm text-slate-500 dark:text-slate-400">
            历史版本查看
          </span>
        </div>

        {/* 历史版本提示 */}
        <div className="mb-6 p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl">
          <div className="flex items-center gap-3">
            <svg className="w-6 h-6 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h3 className="font-medium text-amber-800 dark:text-amber-200">
                这是历史版本
              </h3>
              <p className="text-sm text-amber-600 dark:text-amber-400">
                您正在查看该技能的历史版本 v{version.version}，此版本仅供查看，不可编辑
              </p>
            </div>
          </div>
        </div>

        {/* 技能信息卡片 */}
        <div className="bg-white dark:bg-slate-800 rounded-2xl p-8 border border-slate-100 dark:border-slate-700 shadow-sm">
          <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-6">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-3">
                {version.category && (
                  <span className={cn(
                    'px-3 py-1 rounded-full text-sm font-medium',
                    getCategoryColor(version.category)
                  )}>
                    {version.category}
                  </span>
                )}
                <span className="text-sm text-slate-500 dark:text-slate-400">
                  v{version.version}
                </span>
                <span className="text-sm text-slate-500 dark:text-slate-400">
                  {version.license}
                </span>
              </div>
              <h1 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-2">
                {version.name}
              </h1>
              {version.slug_name && (
                <p className="text-lg text-slate-500 dark:text-slate-400 font-mono mb-3">
                  {version.slug_name}
                </p>
              )}
            </div>

            {/* 安装命令和下载按钮 */}
            <div className="flex flex-col sm:flex-row gap-3 sm:w-auto w-full">
              {/* 安装命令 */}
              <div className="flex-1 sm:flex-initial">
                {user ? (
                  <button
                    onClick={handleCopyCommand}
                    className="w-full sm:w-auto px-4 py-2.5 bg-slate-900 dark:bg-slate-700 text-white rounded-lg font-mono text-sm hover:bg-slate-800 dark:hover:bg-slate-600 transition-colors flex items-center justify-center gap-2"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    {copied ? '已复制!' : installCommand}
                  </button>
                ) : (
                  <div className="px-4 py-2.5 bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-400 rounded-lg text-sm text-center">
                    请先登录后查看安装命令
                  </div>
                )}
              </div>

              {/* 下载按钮 */}
              <Button
                onClick={handleDownload}
                disabled={downloading}
                className="flex items-center gap-2"
              >
                {downloading ? (
                  <>
                    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    下载中...
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    下载技能包
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* 技能描述 */}
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-3">
              技能描述
            </h2>
            <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
              {version.description || '暂无描述'}
            </p>
          </div>

          {/* 统计信息 */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-6 border-t border-slate-100 dark:border-slate-700">
            <div className="text-center">
              <div className="text-2xl font-bold text-slate-900 dark:text-white">
                {version.download_count}
              </div>
              <div className="text-sm text-slate-500 dark:text-slate-400">
                下载次数
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-slate-900 dark:text-white flex items-center justify-center gap-1">
                {version.rating.toFixed(1)}
                <span className="text-yellow-400 text-lg">★</span>
              </div>
              <div className="text-sm text-slate-500 dark:text-slate-400">
                平均评分
              </div>
            </div>
            <div className="text-center">
              <div className="text-sm font-medium text-slate-900 dark:text-white">
                {formatDate(version.created_at)}
              </div>
              <div className="text-sm text-slate-500 dark:text-slate-400">
                创建时间
              </div>
            </div>
            <div className="text-center">
              <div className="text-sm font-medium text-slate-900 dark:text-white">
                {formatDate(version.updated_at)}
              </div>
              <div className="text-sm text-slate-500 dark:text-slate-400">
                更新时间
              </div>
            </div>
          </div>
        </div>

        {/* 标签 */}
        {version.tags && (
          <div className="mt-6 bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-100 dark:border-slate-700 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
              标签
            </h3>
            <div className="flex flex-wrap gap-2">
              {version.tags.split(',').map((tag, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-full text-sm"
                >
                  {tag.trim()}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
