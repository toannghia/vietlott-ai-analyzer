import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { User, Lock, Mail, Key, CheckCircle } from 'lucide-react';
import axios from 'axios';
import { Layout } from '../../components/layout/Layout';

export function Profile() {
    const [user, setUser] = useState<any>(null);
    const [fullName, setFullName] = useState('');
    const [passwords, setPasswords] = useState({ current: '', next: '', confirm: '' });
    const [message, setMessage] = useState({ text: '', type: '' });
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchProfile();
    }, []);

    const fetchProfile = async () => {
        try {
            const token = localStorage.getItem('access_token');
            const res = await axios.get('/api/v1/users/me', {
                headers: { Authorization: `Bearer ${token}` }
            });
            setUser(res.data);
            setFullName(res.data.full_name || '');
        } catch (err) {
            console.error(err);
        }
    }

    const handleUpdateProfile = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            const token = localStorage.getItem('access_token');
            await axios.patch('/api/v1/users/me', { full_name: fullName }, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setMessage({ text: 'Cập nhật thông tin thành công!', type: 'success' });
            fetchProfile();
        } catch (err) {
            setMessage({ text: 'Lỗi cập nhật thông tin.', type: 'error' });
        }
        setLoading(false);
    }

    const handleChangePassword = async (e: React.FormEvent) => {
        e.preventDefault();
        if (passwords.next !== passwords.confirm) {
            setMessage({ text: 'Mật khẩu mới không khớp!', type: 'error' });
            return;
        }
        setLoading(true);
        try {
            const token = localStorage.getItem('access_token');
            await axios.post('/api/v1/users/me/change-password', {
                current_password: passwords.current,
                new_password: passwords.next
            }, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setMessage({ text: 'Đổi mật khẩu thành công!', type: 'success' });
            setPasswords({ current: '', next: '', confirm: '' });
        } catch (err: any) {
            setMessage({ text: err.response?.data?.detail || 'Lỗi đổi mật khẩu.', type: 'error' });
        }
        setLoading(false);
    }

    return (
        <Layout>
            <div className="p-4 md:p-8 max-w-4xl mx-auto space-y-8">
                <div className="flex items-center gap-4 mb-2">
                    <div className="bg-[var(--color-vietlott-red)] p-3 rounded-full text-white">
                        <User size={28} />
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold text-gray-800">Thông tin cá nhân</h2>
                        <p className="text-sm text-gray-500">Quản lý tài khoản và cài đặt bảo mật của bạn</p>
                    </div>
                </div>

                {message.text && (
                    <div className={`p-4 rounded-lg flex items-center gap-3 ${message.type === 'success' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-red-50 text-red-700 border border-red-200'}`}>
                        {message.type === 'success' ? <CheckCircle size={20} /> : <Lock size={20} />}
                        <span className="font-medium">{message.text}</span>
                    </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {/* Profile Info */}
                    <Card className="shadow-md">
                        <CardHeader className="border-b border-gray-100 bg-gray-50/50">
                            <CardTitle className="text-lg flex items-center gap-2">
                                <User size={18} className="text-[var(--color-vietlott-red)]" />
                                Cập nhật thông tin
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="p-6">
                            <form onSubmit={handleUpdateProfile} className="space-y-5">
                                <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-1.5 flex items-center gap-2">
                                        <Mail size={14} /> Email (Không thể đổi)
                                    </label>
                                    <input
                                        type="text"
                                        value={user?.email || ''}
                                        disabled
                                        className="w-full bg-gray-50 border border-gray-200 text-gray-500 rounded-lg px-4 py-2.5 text-sm cursor-not-allowed"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                                        Họ và tên
                                    </label>
                                    <input
                                        type="text"
                                        value={fullName}
                                        onChange={(e) => setFullName(e.target.value)}
                                        placeholder="Nhập họ và tên của bạn"
                                        className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-red-100 focus:border-[var(--color-vietlott-red)] transition-all"
                                    />
                                </div>
                                <Button variant="primary" type="submit" className="w-full font-bold h-11" disabled={loading}>
                                    {loading ? 'ĐANG LƯU...' : 'LƯU THÔNG TIN'}
                                </Button>
                            </form>
                        </CardContent>
                    </Card>

                    {/* Change Password */}
                    <Card className="shadow-md">
                        <CardHeader className="border-b border-gray-100 bg-gray-50/50">
                            <CardTitle className="text-lg flex items-center gap-2">
                                <Key size={18} className="text-amber-500" />
                                Đổi mật khẩu
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="p-6">
                            <form onSubmit={handleChangePassword} className="space-y-5">
                                <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                                        Mật khẩu hiện tại
                                    </label>
                                    <input
                                        type="password"
                                        value={passwords.current}
                                        onChange={(e) => setPasswords({ ...passwords, current: e.target.value })}
                                        className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-red-100 focus:border-[var(--color-vietlott-red)] transition-all"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                                        Mật khẩu mới
                                    </label>
                                    <input
                                        type="password"
                                        value={passwords.next}
                                        onChange={(e) => setPasswords({ ...passwords, next: e.target.value })}
                                        className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-red-100 focus:border-[var(--color-vietlott-red)] transition-all"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-semibold text-gray-700 mb-1.5">
                                        Xác nhận mật khẩu mới
                                    </label>
                                    <input
                                        type="password"
                                        value={passwords.confirm}
                                        onChange={(e) => setPasswords({ ...passwords, confirm: e.target.value })}
                                        className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-red-100 focus:border-[var(--color-vietlott-red)] transition-all"
                                        required
                                    />
                                </div>
                                <Button variant="outline" type="submit" className="w-full font-bold h-11 border-2 border-amber-500 text-amber-600 hover:bg-amber-50" disabled={loading}>
                                    {loading ? 'ĐANG XỬ LÝ...' : 'ĐỔI MẬT KHẨU'}
                                </Button>
                            </form>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </Layout>
    );
}
