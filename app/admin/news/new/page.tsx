import Link from 'next/link';
import { redirect } from 'next/navigation';
import { createArticle, getCategories } from '@/lib/news';
import { ScheduleFields } from '@/components/ScheduleFields';

async function saveArticle(formData: FormData) {
  'use server';
  const title = String(formData.get('title') || '').trim();
  const categoryId = String(formData.get('categoryId') || '');
  if (!title || !categoryId) throw new Error('Title and category are required.');
  await createArticle({ title, categoryId, excerpt: String(formData.get('excerpt') || ''), content: String(formData.get('content') || ''), status: String(formData.get('status') || 'DRAFT') as 'DRAFT' | 'SCHEDULED' | 'PUBLISHED' | 'ARCHIVED', isBreaking: formData.get('isBreaking') === 'on', isTrending: formData.get('isTrending') === 'on', scheduledAt: String(formData.get('scheduledAt') || '') });
  redirect('/admin/news');
}
export default async function NewArticlePage() {
 const categories=await getCategories();
 return <section className="admin-card article-form"><p className="breadcrumbs">Dashboard / News Management / <span>Add News</span></p><h1>Add News</h1><p>Create and publish a new article.</p><form action={saveArticle}><label>Title<input name="title" required /></label><label>Category<select name="categoryId" required><option value="">Select a category</option>{categories.map(category=><option value={category.id} key={category.id}>{category.name}</option>)}</select></label><label>Summary<input name="excerpt" /></label><label>Article content<textarea name="content" rows={8} /></label><ScheduleFields /><label><input name="isBreaking" type="checkbox" />Breaking news</label><label><input name="isTrending" type="checkbox" />Trending news</label><div className="article-form-actions"><button className="admin-add" type="submit">SAVE NEWS</button><Link href="/admin/news">CANCEL</Link></div></form></section>;
}