'use server';
import { Pool } from 'pg';
import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';
const pool=new Pool({connectionString:process.env.DATABASE_URL});
export async function createCategory(formData:FormData){const name=String(formData.get('name')||'').trim();if(!name)throw new Error('Category name is required.');const id=crypto.randomUUID(),slug=(String(formData.get('slug')||name).toLowerCase().trim().replace(/[^a-z0-9]+/g,'-').replace(/(^-|-$)/g,''));await pool.query('INSERT INTO "Category" (id,name,slug,"tamilName",description,"isActive","sortOrder","updatedAt") VALUES ($1,$2,$3,$4,$5,$6,$7,NOW())',[id,name,slug,String(formData.get('tamilName')||'')||null,String(formData.get('description')||'')||null,formData.get('isActive')==='on',Number(formData.get('sortOrder')||0)]);revalidatePath('/admin/categories');redirect('/admin/categories')}
export async function toggleCategory(id:string,isActive:boolean){await pool.query('UPDATE "Category" SET "isActive"=$1,"updatedAt"=NOW() WHERE id=$2',[isActive,id]);revalidatePath('/admin/categories')}