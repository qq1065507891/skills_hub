'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { publishApi, SkillCreate, Skill } from '@/lib/api';
import { useAuth } from '@/lib/auth';
import { formatErrorMessage } from '@/lib/errorUtils';

interface PublishSkillModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (skill: Skill) => void;
}

const initialFormData: SkillCreate = {
  name: '',
  slug_name: '',
  description: '',
  version: '1.0.0',
  license: 'MIT',
  category: '开发工具',
  tags: '',
};

export function PublishSkillModal({ isOpen, onClose, onSuccess }: PublishSkillModalProps) {
  const { user } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [formData, setFormData] = useState<SkillCreate>(initialFormData);

  // 当模态框打开时，重置表单数据
  useEffect(() => {
    if (isOpen) {
      setFormData(initialFormData);
      setSelectedFile(null);
      setError('');
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    if (!user) {
      setError('请先登录');
      setLoading(false);
      return;
    }
    
    try {
      // 添加 author_id 到表单数据
      const skillDataWithAuthor = {
        ...formData,
        author_id: user.id,
      };
      
      const newSkill = await publishApi.createSkill(skillDataWithAuthor);
      
      try {
        if (selectedFile) {
          await publishApi.uploadSkillPackage(newSkill.id, selectedFile);
        }
        await publishApi.submitPublication(newSkill.id, '首次发布');
      } catch (postActionErr: any) {
        console.warn('技能包上传或发布申请失败:', postActionErr);
        // 不阻断跳转，但通过 alert 告知用户
        alert(`技能创建成功，但${selectedFile ? '上传技能包或' : ''}提交发布申请失败: ${formatErrorMessage(postActionErr)}`);
      }

      if (onSuccess) {
        onSuccess(newSkill);
      }
      onClose();
      router.push(`/skills/${newSkill.id}`);
    } catch (err: any) {
      setError(formatErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const categories = [
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
  const licenses = ['MIT', 'Apache-2.0', 'GPL-3.0', 'BSD-3-Clause'];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white dark:bg-slate-800 rounded-2xl p-8 w-full max-w-2xl shadow-xl border border-slate-200 dark:border-slate-700 max-h-[90vh] overflow-y-auto">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-6">
          发布新技能
        </h2>

        {error && (
          <div className="mb-4 p-3 bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-lg text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              技能名称 *
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="请输入技能名称"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              英文名称 *
            </label>
            <input
              type="text"
              required
              pattern="^[a-z0-9-]+$"
              value={formData.slug_name}
              onChange={(e) => setFormData({ ...formData, slug_name: e.target.value.toLowerCase() })}
              className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500 font-mono"
              placeholder="例如: my-skill-name"
            />
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              用于安装命令: npm install {formData.slug_name || 'my-skill-name'} --foreground-scripts (只能包含小写字母、数字和连字符)
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              描述
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
              rows={3}
              placeholder="请输入技能描述"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                版本 *
              </label>
              <input
                type="text"
                required
                value={formData.version}
                onChange={(e) => setFormData({ ...formData, version: e.target.value })}
                className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="1.0.0"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                许可证
              </label>
              <select
                value={formData.license}
                onChange={(e) => setFormData({ ...formData, license: e.target.value })}
                className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {licenses.map((license) => (
                  <option key={license} value={license}>
                    {license}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                分类
              </label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {categories.map((category) => (
                  <option key={category.value} value={category.value}>
                    {category.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                标签 (逗号分隔)
              </label>
              <input
                type="text"
                value={formData.tags}
                onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="tag1, tag2, tag3"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              技能包文件 (可选)
            </label>
            <div className="border-2 border-dashed border-slate-200 dark:border-slate-600 rounded-xl p-6 text-center">
              <input
                type="file"
                accept=".zip,.tar.gz,.tgz"
                onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                className="hidden"
                id="skill-file"
              />
              <label
                htmlFor="skill-file"
                className="cursor-pointer"
              >
                {selectedFile ? (
                  <div className="text-slate-600 dark:text-slate-300">
                    <svg className="w-10 h-10 mx-auto mb-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p className="font-medium">{selectedFile.name}</p>
                    <p className="text-sm text-slate-400">点击更换文件</p>
                  </div>
                ) : (
                  <div className="text-slate-400 dark:text-slate-500">
                    <svg className="w-10 h-10 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <p className="font-medium">点击选择文件或拖拽到此处</p>
                    <p className="text-sm">支持 .zip, .tar.gz, .tgz 格式</p>
                  </div>
                )}
              </label>
            </div>
          </div>

          <div className="flex gap-4 pt-4">
            <Button type="button" variant="outline" className="flex-1" onClick={onClose}>
              取消
            </Button>
            <Button type="submit" className="flex-1" disabled={loading}>
              {loading ? '发布中...' : '发布技能'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
