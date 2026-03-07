'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { skillApi, Skill, Review, ReviewCreate } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import { cn } from '@/lib/utils';
import { useAuth } from '@/lib/auth';
import { PublishSkillModal } from '@/components/common/PublishSkillModal';

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

const detectOS = (): 'unix' | 'windows' => {
  if (typeof window === 'undefined') return 'unix';
  const platform = navigator.platform.toLowerCase();
  const userAgent = navigator.userAgent.toLowerCase();
  
  if (platform.includes('win') || userAgent.includes('windows')) {
    return 'windows';
  }
  return 'unix';
};

// 渲染星级
const renderStars = (rating: number, interactive = false, onChange?: (rating: number) => void) => {
  const stars = [];
  
  for (let i = 1; i <= 5; i++) {
    const isFilled = i <= rating;
    const starClass = interactive ? 'cursor-pointer hover:scale-110 transition-transform' : '';
    
    stars.push(
      <span
        key={i}
        className={cn(
          'text-2xl',
          isFilled ? 'text-yellow-400' : 'text-slate-300 dark:text-slate-600',
          starClass
        )}
        onClick={() => interactive && onChange?.(i)}
      >
        ★
      </span>
    );
  }
  
  return stars;
};

export default function SkillDetailPage() {
  const params = useParams();
  const router = useRouter();
  const skillId = Number(params.id);

  const [skill, setSkill] = useState<Skill | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [versions, setVersions] = useState<Skill[]>([]);
  const [selectedVersionId, setSelectedVersionId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [reviewsLoading, setReviewsLoading] = useState(true);
  const [submittingReview, setSubmittingReview] = useState(false);
  const [copied, setCopied] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState<'unix' | 'windows' | 'python'>('unix');
  const [isUpdateModalOpen, setIsUpdateModalOpen] = useState(false);
  const [baseUrl, setBaseUrl] = useState('http://localhost:8000');
  const [isClient, setIsClient] = useState(false);
  const { user } = useAuth();
  
  // 当前展示的技能元数据（动态基于选择的版本）
  const displaySkill = selectedVersionId 
    ? versions.find(v => v.id === selectedVersionId) || skill 
    : skill;

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
  
  // 评价表单状态
  const [newRating, setNewRating] = useState(5);
  const [newComment, setNewComment] = useState('');

  useEffect(() => {
    if (!skillId) return;

    const fetchData = async () => {
      try {
        setLoading(true);
        const skillData = await skillApi.getSkill(skillId);
        setSkill(skillData);
        
        try {
          const versionsData = await skillApi.getSkillVersions(skillId);
          setVersions(versionsData);
        } catch (e) {
          console.warn('Failed to fetch versions', e);
        }
        
        setReviewsLoading(true);
        const reviewsData = await skillApi.getReviews(skillId);
        setReviews(reviewsData);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setLoading(false);
        setReviewsLoading(false);
      }
    };

    fetchData();
  }, [skillId]);

  const handleDownload = () => {
    if (!displaySkill) return;
    const defaultApiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const serverBaseUrl = defaultApiUrl.replace('/api/v1', '').replace('/api', '');
    const activeBaseUrl = isClient ? baseUrl : serverBaseUrl;

    let targetDownloadUrl = `${activeBaseUrl}/api/v1/install/${skillId}/download-file`;
    if (selectedVersionId) {
      targetDownloadUrl += `?version=${selectedVersionId}`;
    }
    window.open(targetDownloadUrl, '_blank');
  };
  
  const getInstallCommand = () => {
    if (!displaySkill) return '';
    
    const defaultApiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const serverBaseUrl = defaultApiUrl.replace('/api/v1', '').replace('/api', '');
    const activeBaseUrl = isClient ? baseUrl : serverBaseUrl;
    
    let downloadUrl = `${activeBaseUrl}/api/v1/install/${skillId}/download-file`;
    if (selectedVersionId) {
      downloadUrl += `?version=${selectedVersionId}`;
    }

    switch (selectedPlatform) {
      case 'unix':
        return `curl -L -o ${displaySkill.name}.zip "${downloadUrl}"`;
      case 'windows':
        return `iwr -Uri "${downloadUrl}" -OutFile ${displaySkill.name}.zip`;
      case 'python':
        return `pip install ${displaySkill.name}==${displaySkill.version}`;
      default:
        return `curl -L -o ${displaySkill.name}.zip "${downloadUrl}"`;
    }
  };
  
  const installCommand = getInstallCommand();
  
  const handleCopyCommand = () => {
    if (!installCommand) return;
    navigator.clipboard.writeText(installCommand);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // 处理提交评价
  const handleSubmitReview = async () => {
    if (!skill) return;
    
    try {
      setSubmittingReview(true);
      const reviewData: ReviewCreate = {
        rating: newRating,
        comment: newComment || undefined,
      };
      const newReview = await skillApi.submitReview(skill.id, reviewData);
      setReviews([newReview, ...reviews]);
      setNewRating(5);
      setNewComment('');
      alert('评价提交成功！');
    } catch (error) {
      console.error('Failed to submit review:', error);
      alert('提交评价失败，请稍后重试');
    } finally {
      setSubmittingReview(false);
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

  if (!skill || !displaySkill) {
    return (
      <div className="min-h-screen py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="bg-white dark:bg-slate-800 rounded-2xl p-8 border border-slate-100 dark:border-slate-700 shadow-sm">
            <h2 className="text-2xl font-semibold text-slate-900 dark:text-white mb-4">
              技能未找到
            </h2>
            <p className="text-slate-600 dark:text-slate-300 mb-6">
              该技能可能已被删除或不存在
            </p>
            <Button onClick={() => router.push('/skills')}>
              返回技能库
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 返回按钮 */}
        <div className="mb-6">
          <Link href="/skills">
            <Button variant="outline" size="sm">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              返回技能库
            </Button>
          </Link>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* 左侧 - 技能详情 */}
          <div className="lg:col-span-2 space-y-6">
            {/* 技能基本信息卡片 */}
            <div className="bg-white dark:bg-slate-800 rounded-2xl p-8 border border-slate-100 dark:border-slate-700 shadow-sm">
              <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-6">
                <div className="flex-1">
                  <div className="flex flex-wrap items-center gap-3 mb-3">
                    {displaySkill.category && (
                      <span className={cn(
                        'px-3 py-1 rounded-full text-sm font-medium',
                        getCategoryColor(displaySkill.category)
                      )}>
                        {displaySkill.category}
                      </span>
                    )}
                    {versions.length > 0 ? (
                      <select 
                        className="bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 text-sm rounded-lg px-2 py-1 focus:ring-primary-500 focus:border-primary-500"
                        value={selectedVersionId || ''}
                        onChange={(e) => setSelectedVersionId(e.target.value ? Number(e.target.value) : null)}
                      >
                        <option value="">v{skill.version} (最新版)</option>
                        {versions.map(v => (
                          <option key={v.id} value={v.id}>v{v.version} ({formatDate(v.created_at).split(' ')[0]})</option>
                        ))}
                      </select>
                    ) : (
                      <span className="text-sm text-slate-500 dark:text-slate-400">
                        v{displaySkill.version}
                      </span>
                    )}
                    <span className="text-sm text-slate-500 dark:text-slate-400">
                      {displaySkill.license}
                    </span>
                  </div>
                  <h1 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-3">
                    {displaySkill.name}
                  </h1>
                  
                  {/* 平台选择器 */}
                  <div className="flex gap-2 mb-4">
                    <button
                      onClick={() => setSelectedPlatform('unix')}
                      className={cn(
                        'px-4 py-2 rounded-lg text-sm font-medium transition-all',
                        selectedPlatform === 'unix'
                          ? 'bg-primary-500 text-white shadow-md'
                          : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
                      )}
                    >
                      🐧 Linux/macOS
                    </button>
                    <button
                      onClick={() => setSelectedPlatform('windows')}
                      className={cn(
                        'px-4 py-2 rounded-lg text-sm font-medium transition-all',
                        selectedPlatform === 'windows'
                          ? 'bg-primary-500 text-white shadow-md'
                          : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
                      )}
                    >
                      🪟 Windows
                    </button>
                    <button
                      onClick={() => setSelectedPlatform('python')}
                      className={cn(
                        'px-4 py-2 rounded-lg text-sm font-medium transition-all',
                        selectedPlatform === 'python'
                          ? 'bg-primary-500 text-white shadow-md'
                          : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
                      )}
                    >
                      🐍 Python
                    </button>
                  </div>
                </div>
                {user && user?.id === skill.author_id && (
                  <Button 
                    variant="outline"
                    className="shrink-0"
                    onClick={() => setIsUpdateModalOpen(true)}
                  >
                    发布新版本
                  </Button>
                )}
              </div>
              
              {/* 安装命令和下载按钮 */}
              <div className="mt-6 p-6 bg-slate-50 dark:bg-slate-700/50 rounded-xl space-y-3">
                <div className="flex items-center gap-2 p-3 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-600">
                  <div className="flex-1 min-w-0 overflow-x-auto pb-1 custom-scrollbar">
                    <code className="text-sm text-slate-700 dark:text-slate-300 font-mono whitespace-nowrap select-all px-1">
                      {installCommand}
                    </code>
                  </div>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={handleCopyCommand}
                    className="shrink-0 whitespace-nowrap min-w-[64px]"
                  >
                    {copied ? (
                      <>
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        已复制
                      </>
                    ) : (
                      <>
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                        复制
                      </>
                    )}
                  </Button>
                </div>
                <Button 
                  size="sm" 
                  className="w-full"
                  onClick={handleDownload}
                >
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  下载技能包（ZIP）
                </Button>
              </div>

              {/* 技能描述 */}
              <div className="mb-6 mt-6">
                <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-3">
                  技能描述
                </h2>
                <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
                  {displaySkill.description || '暂无描述'}
                </p>
              </div>

              {/* 统计信息 */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-6 border-t border-slate-100 dark:border-slate-700">
                <div className="text-center">
                  <div className="text-2xl font-bold text-slate-900 dark:text-white">
                    {displaySkill.download_count}
                  </div>
                  <div className="text-sm text-slate-500 dark:text-slate-400">
                    下载次数
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-slate-900 dark:text-white flex items-center justify-center gap-1">
                    {displaySkill.rating.toFixed(1)}
                    <span className="text-yellow-400 text-lg">★</span>
                  </div>
                  <div className="text-sm text-slate-500 dark:text-slate-400">
                    平均评分
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-slate-900 dark:text-white">
                    {reviews.length}
                  </div>
                  <div className="text-sm text-slate-500 dark:text-slate-400">
                    用户评价
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-sm font-medium text-slate-900 dark:text-white">
                    {formatDate(displaySkill.created_at)}
                  </div>
                  <div className="text-sm text-slate-500 dark:text-slate-400">
                    创建时间
                  </div>
                </div>
              </div>
            </div>

            {/* 评价区域 */}
            <div className="bg-white dark:bg-slate-800 rounded-2xl p-8 border border-slate-100 dark:border-slate-700 shadow-sm">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-6">
                用户评价
              </h2>

              {/* 提交评价表单 */}
              <div className="mb-8 p-6 bg-slate-50 dark:bg-slate-700/50 rounded-xl">
                <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-4">
                  分享你的评价
                </h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                      评分
                    </label>
                    <div className="flex items-center gap-2">
                      {renderStars(newRating, true, setNewRating)}
                      <span className="ml-2 text-sm text-slate-500 dark:text-slate-400">
                        {newRating} 星
                      </span>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                      评论（可选）
                    </label>
                    <textarea
                      value={newComment}
                      onChange={(e) => setNewComment(e.target.value)}
                      placeholder="分享你使用这个技能的体验..."
                      className="w-full px-4 py-3 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all resize-none"
                      rows={3}
                    />
                  </div>
                  <div className="flex justify-end">
                    <Button
                      onClick={handleSubmitReview}
                      disabled={submittingReview}
                    >
                      {submittingReview ? (
                        <>
                          <svg className="w-4 h-4 mr-2 animate-spin" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                          </svg>
                          提交中...
                        </>
                      ) : (
                        '提交评价'
                      )}
                    </Button>
                  </div>
                </div>
              </div>

              {/* 评价列表 */}
              {reviewsLoading ? (
                <div className="space-y-4">
                  {[...Array(3)].map((_, index) => (
                    <div key={index} className="p-4 bg-slate-50 dark:bg-slate-700/50 rounded-xl animate-pulse">
                      <div className="h-4 bg-slate-200 dark:bg-slate-600 rounded w-1/4 mb-3" />
                      <div className="h-4 bg-slate-200 dark:bg-slate-600 rounded w-3/4" />
                    </div>
                  ))}
                </div>
              ) : reviews.length > 0 ? (
                <div className="space-y-4">
                  {reviews.map((review) => (
                    <div key={review.id} className="p-4 bg-slate-50 dark:bg-slate-700/50 rounded-xl">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold">
                            {review.user?.name?.[0] || 'U'}
                          </div>
                          <div>
                            <div className="font-medium text-slate-900 dark:text-white">
                              {review.user?.name || '匿名用户'}
                            </div>
                            <div className="text-sm text-slate-500 dark:text-slate-400">
                              {formatDate(review.created_at)}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center">
                          {renderStars(review.rating)}
                        </div>
                      </div>
                      {review.comment && (
                        <p className="text-slate-600 dark:text-slate-300 mt-2">
                          {review.comment}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-slate-100 dark:bg-slate-700 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                  </div>
                  <p className="text-slate-500 dark:text-slate-400">
                    暂无评价，成为第一个评价者吧！
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* 右侧 - 侧边栏 */}
          <div className="space-y-6">
            {/* 快速信息 */}
            <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-100 dark:border-slate-700 shadow-sm">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
                技能信息
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-slate-500 dark:text-slate-400">版本</span>
                  <span className="font-medium text-slate-900 dark:text-white">
                    v{displaySkill.version}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500 dark:text-slate-400">许可证</span>
                  <span className="font-medium text-slate-900 dark:text-white">
                    {displaySkill.license}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500 dark:text-slate-400">作者ID</span>
                  <span className="font-medium text-slate-900 dark:text-white">
                    {displaySkill.author_id}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500 dark:text-slate-400">更新时间</span>
                  <span className="font-medium text-slate-900 dark:text-white text-sm">
                    {formatDate(displaySkill.updated_at)}
                  </span>
                </div>
              </div>
            </div>

            {/* 标签 */}
            {displaySkill.tags && (
              <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-100 dark:border-slate-700 shadow-sm">
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
                  标签
                </h3>
                <div className="flex flex-wrap gap-2">
                  {displaySkill.tags.split(',').map((tag, index) => (
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
      </div>
      
      {/* 更新技能弹窗 (复用 PublishSkillModal) */}
      <PublishSkillModal 
        isOpen={isUpdateModalOpen}
        onClose={() => setIsUpdateModalOpen(false)}
        onSuccess={() => {
          setIsUpdateModalOpen(false);
          // 局部重载或硬刷新页面以获取最新数据
          window.location.reload();
        }}
      />
    </div>
  );
}
