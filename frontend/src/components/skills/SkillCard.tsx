'use client';

import { Skill } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/Button';
import Link from 'next/link';
import { useState, useEffect } from 'react';

interface SkillCardProps {
  skill: Skill;
  index?: number;
  showInstallCommand?: boolean;
}

const detectOS = (): 'unix' | 'windows' => {
  if (typeof window === 'undefined') return 'unix';
  const platform = navigator.platform.toLowerCase();
  const userAgent = navigator.userAgent.toLowerCase();
  
  if (platform.includes('win') || userAgent.includes('windows')) {
    return 'windows';
  }
  return 'unix';
};

export const SkillCard = ({ skill, index = 0, showInstallCommand = false }: SkillCardProps) => {
  const [copied, setCopied] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState<'unix' | 'windows'>('unix');
  const [baseUrl, setBaseUrl] = useState('http://localhost:8000');
  const [isClient, setIsClient] = useState(false);
  
  useEffect(() => {
    setSelectedPlatform(detectOS());
    setIsClient(true);
    const envApiUrl = process.env.NEXT_PUBLIC_API_URL || '';
    if (envApiUrl && !envApiUrl.includes('localhost') && !envApiUrl.includes('127.0.0.1')) {
      setBaseUrl(envApiUrl.replace('/api/v1', '').replace('/api', ''));
    } else {
      setBaseUrl(`${window.location.protocol}//${window.location.hostname}:8000`);
    }
  }, []);
  
  const categoryColors: Record<string, string> = {
    '开发工具': 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
    '机器学习': 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
    '数据分析': 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400',
    'Web 开发': 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
    '移动开发': 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400',
    '测试': 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    'DevOps': 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400',
    '文档': 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
    '设计': 'bg-pink-100 text-pink-700 dark:bg-pink-900/30 dark:text-pink-400',
    '安全': 'bg-teal-100 text-teal-700 dark:bg-teal-900/30 dark:text-teal-400',
    '其他': 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300',
  };

  const getCategoryColor = (category?: string) => {
    if (!category) return 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300';
    return categoryColors[category] || categoryColors['其他'];
  };

  const renderStars = (rating: number) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;

    for (let i = 0; i < fullStars; i++) {
      stars.push(
        <span key={i} className="text-yellow-400">★</span>
      );
    }

    if (hasHalfStar) {
      stars.push(
        <span key="half" className="text-yellow-400">☆</span>
      );
    }

    const emptyStars = 5 - Math.ceil(rating);
    for (let i = 0; i < emptyStars; i++) {
      stars.push(
        <span key={`empty-${i}`} className="text-slate-300 dark:text-slate-600">☆</span>
      );
    }

    return stars;
  };
  
  const getInstallCommand = () => {
    const defaultApiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const serverBaseUrl = defaultApiUrl.replace('/api/v1', '').replace('/api', '');
    const activeBaseUrl = isClient ? baseUrl : serverBaseUrl;
    
    const downloadUrl = `${activeBaseUrl}/api/v1/install/${skill.id}/download-file`;
    switch (selectedPlatform) {
      case 'unix':
        return `curl -L -o ${skill.name}.zip "${downloadUrl}"`;
      case 'windows':
        return `iwr -Uri "${downloadUrl}" -OutFile ${skill.name}.zip`;
      default:
        return `curl -L -o ${skill.name}.zip "${downloadUrl}"`;
    }
  };
  
  const installCommand = getInstallCommand();
  
  const handleCopyCommand = () => {
    navigator.clipboard.writeText(installCommand);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  
  const handleDownload = () => {
    const defaultApiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const serverBaseUrl = defaultApiUrl.replace('/api/v1', '').replace('/api', '');
    const activeBaseUrl = isClient ? baseUrl : serverBaseUrl;
    window.open(`${activeBaseUrl}/api/v1/install/${skill.id}/download-file`, '_blank');
  };

  return (
    <Link href={`/skills/${skill.id}`}>
      <div 
        className="group bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-100 dark:border-slate-700 shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1 cursor-pointer"
        style={{
          animationDelay: `${index * 0.1}s`,
        }}
      >
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              {skill.category && (
                <span className={cn(
                  'px-2.5 py-0.5 rounded-full text-xs font-medium',
                  getCategoryColor(skill.category)
                )}>
                  {skill.category}
                </span>
              )}
              <span className="text-xs text-slate-400">v{skill.version}</span>
            </div>
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
              {skill.name}
            </h3>
          </div>
        </div>

        <p className="text-slate-600 dark:text-slate-300 text-sm mb-4 line-clamp-2">
          {skill.description || '暂无描述'}
        </p>

        <div className="flex items-center justify-between pt-4 border-t border-slate-100 dark:border-slate-700">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1">
              {renderStars(skill.rating)}
              <span className="text-sm text-slate-500 ml-1">{skill.rating.toFixed(1)}</span>
            </div>
            <div className="flex items-center gap-1 text-sm text-slate-500">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              <span>{skill.download_count}</span>
            </div>
          </div>
          <div className="text-xs text-slate-400">
            {formatDate(skill.created_at)}
          </div>
        </div>

        {showInstallCommand && (
          <div className="mt-4 space-y-2" onClick={(e) => e.preventDefault()}>
            <div className="flex gap-1 mb-2">
              <button
                onClick={() => setSelectedPlatform('unix')}
                className={cn(
                  'px-2 py-1 rounded text-xs font-medium transition-all',
                  selectedPlatform === 'unix'
                    ? 'bg-primary-500 text-white'
                    : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
                )}
              >
                🐧 Linux/macOS
              </button>
              <button
                onClick={() => setSelectedPlatform('windows')}
                className={cn(
                  'px-2 py-1 rounded text-xs font-medium transition-all',
                  selectedPlatform === 'windows'
                    ? 'bg-primary-500 text-white'
                    : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
                )}
              >
                🪟 Windows
              </button>
            </div>
            <div className="flex items-center gap-2 p-2 bg-slate-50 dark:bg-slate-700/50 rounded-lg border border-slate-100 dark:border-slate-600">
              <div className="flex-1 min-w-0 overflow-x-auto pb-1 custom-scrollbar">
                <code className="text-xs text-slate-700 dark:text-slate-300 font-mono whitespace-nowrap select-all px-1">
                  {installCommand}
                </code>
              </div>
              <Button 
                size="sm" 
                variant="outline"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  handleCopyCommand();
                }}
                className="shrink-0 whitespace-nowrap min-w-[64px] bg-white dark:bg-slate-800"
              >
                {copied ? '已复制' : '复制'}
              </Button>
            </div>
            <Button 
              size="sm" 
              className="w-full"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                handleDownload();
              }}
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              下载技能包
            </Button>
          </div>
        )}

        <div className="mt-4">
          <Button className="w-full" variant="outline" size="sm">
            查看详情
          </Button>
        </div>
      </div>
    </Link>
  );
};
