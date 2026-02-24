import React, { useEffect, useState } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { Shield, User, LogOut, LayoutDashboard, Users } from 'lucide-react';
import { Button } from '../ui/Button';
import axios from 'axios';

interface LayoutProps {
    children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
    const navigate = useNavigate();
    const location = useLocation();
    const [user, setUser] = useState<any>(null);

    useEffect(() => {
        fetchUser();
    }, []);

    const fetchUser = async () => {
        try {
            const token = localStorage.getItem('access_token');
            if (!token) return;
            const res = await axios.get('/api/v1/users/me', {
                headers: { Authorization: `Bearer ${token}` }
            });
            setUser(res.data);
        } catch (err) {
            console.error("Failed to fetch user", err);
        }
    }

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        navigate('/login');
    }

    return (
        <div className="min-h-screen bg-[var(--color-bg-light)] text-[var(--color-text-main)] w-full">
            {/* Top Navbar */}
            <header className="flex justify-between items-center bg-[var(--color-vietlott-red)] text-white px-6 py-4 shadow-md sticky top-0 z-50">
                <div className="flex items-center gap-6">
                    <Link to="/dashboard" className="flex items-center gap-3">
                        <div className="bg-white p-2 rounded-full shadow-sm">
                            <Shield className="text-[var(--color-vietlott-red)]" size={24} />
                        </div>
                        <h1 className="text-xl font-sans font-bold tracking-tight hidden md:block">Vietlott AI Analyzer</h1>
                    </Link>

                    <nav className="flex items-center gap-1 ml-4 h-full">
                        <Link to="/dashboard">
                            <Button
                                variant="ghost"
                                className={`text-white hover:bg-red-800 px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2 ${location.pathname === '/dashboard' ? 'bg-red-900 border border-red-400' : ''}`}
                            >
                                <LayoutDashboard size={18} /> DASHBOARD
                            </Button>
                        </Link>

                        <Link to="/profile">
                            <Button
                                variant="ghost"
                                className={`text-white hover:bg-red-800 px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2 ${location.pathname === '/profile' ? 'bg-red-900 border border-red-400' : ''}`}
                            >
                                <User size={18} /> CÁ NHÂN
                            </Button>
                        </Link>

                        {(user?.role === 'admin' || !user) && (
                            <Link to="/admin/users">
                                <Button
                                    variant="ghost"
                                    className={`text-white hover:bg-red-800 px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2 ${location.pathname === '/admin/users' ? 'bg-red-900 border border-red-400' : ''}`}
                                >
                                    <Users size={18} /> QUẢN LÝ NGƯỜI DÙNG
                                </Button>
                            </Link>
                        )}
                    </nav>
                </div>

                <div className="flex items-center gap-4">
                    <div className="hidden md:flex flex-col items-end mr-2">
                        <span className="text-xs font-bold text-white">{user?.full_name || user?.email || 'Đang tải...'}</span>
                        <span className="text-[10px] text-red-200 uppercase">{user?.role || 'Guest'} Account</span>
                    </div>
                    <Button variant="danger" onClick={handleLogout} className="bg-red-800 hover:bg-red-900 border-none px-4 rounded-full h-9 shadow-inner">
                        <LogOut size={16} className="mr-2" /> ĐĂNG XUẤT
                    </Button>
                </div>
            </header>

            <main>
                {children}
            </main>
        </div>
    );
}
