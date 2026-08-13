'use server';
import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';
import { Pool } from 'pg';
const pool = new Pool({ connectionString: process.env.DATABASE_URL });
export async function deleteArticle(id:string){await pool.query('DELETE FROM "Article" WHERE id=$1',[id]);revalidatePath('/admin/news');}
export async function updateArticle(id:string,formData:FormData){const title=String(formData.get('title')||'').trim();const categoryId=String(formData.get('categoryId')||'');if(!title||!categoryId)throw new Error('Title and category are required.');await pool.query(`UPDATE "Article" SET title=$1,excerpt=$2,content=$3,status=$4::"ArticleStatus","isBreaking"=$5,"isTrending"=$6,"categoryId"=$7,"publishedAt"=CASE WHEN $4::"ArticleStatus"='PUBLISHED' THEN COALESCE("publishedAt",NOW()) ELSE "publishedAt" END,"updatedAt"=NOW() WHERE id=$8`,[title,String(formData.get('excerpt')||'')||null,String(formData.get('content')||'')||null,String(formData.get('status')||'DRAFT'),formData.get('isBreaking')==='on',formData.get('isTrending')==='on',categoryId,id]);revalidatePath('/admin/news');redirect('/admin/news');}