import type {ReactNode} from 'react';
import {AdminSidebar} from '@/components/AdminSidebar';
import '@/app/admin/admin.css';
export default function AdminLayout({children}:{children:ReactNode}){return <div className="admin-shell"><AdminSidebar/><main className="admin-main">{children}</main></div>}
