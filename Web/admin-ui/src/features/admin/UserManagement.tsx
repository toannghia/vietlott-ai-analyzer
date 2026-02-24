import { useState, useEffect } from 'react';
import { Card, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Users, Edit2, Trash2, Shield, Check, X, Search, Mail, UserPlus, Key } from 'lucide-react';
import axios from 'axios';
import { Layout } from '../../components/layout/Layout';

export function UserManagement() {
    const [users, setUsers] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [filter, setFilter] = useState('');

    // Modal State
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingUser, setEditingUser] = useState<any>(null); // null means "Create Mode"
    const [formUser, setFormUser] = useState({
        email: '',
        password: '',
        full_name: '',
        role: 'free'
    });
    const [formError, setFormError] = useState('');

    useEffect(() => {
        fetchUsers();
    }, []);

    const fetchUsers = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('access_token');
            const res = await axios.get('/api/v1/users/', {
                headers: { Authorization: `Bearer ${token}` }
            });
            setUsers(res.data);
        } catch (err) {
            console.error(err);
        }
        setLoading(false);
    }

    const openCreateModal = () => {
        setEditingUser(null);
        setFormUser({ email: '', password: '', full_name: '', role: 'free' });
        setFormError('');
        setIsModalOpen(true);
    }

    const openEditModal = (user: any) => {
        setEditingUser(user);
        setFormUser({
            email: user.email,
            password: '', // Password is empty for reset
            full_name: user.full_name || '',
            role: user.role
        });
        setFormError('');
        setIsModalOpen(true);
    }

    const handleSaveUser = async (e: React.FormEvent) => {
        e.preventDefault();
        setFormError('');
        try {
            const token = localStorage.getItem('access_token');
            if (editingUser) {
                // UPDATE
                const updateData: any = { ...formUser };
                if (!updateData.password) delete updateData.password; // Don't send empty password

                await axios.patch(`/api/v1/users/${editingUser.id}`, updateData, {
                    headers: { Authorization: `Bearer ${token}` }
                });
            } else {
                // CREATE
                await axios.post('/api/v1/users/', formUser, {
                    headers: { Authorization: `Bearer ${token}` }
                });
            }
            setIsModalOpen(false);
            fetchUsers();
        } catch (err: any) {
            setFormError(err.response?.data?.detail || 'Lỗi khi lưu thông tin');
        }
    }

    const handleToggleStatus = async (user: any) => {
        try {
            const token = localStorage.getItem('access_token');
            await axios.patch(`/api/v1/users/${user.id}`, { is_active: !user.is_active }, {
                headers: { Authorization: `Bearer ${token}` }
            });
            fetchUsers();
        } catch (err) {
            alert('Lỗi cập nhật trạng thái');
        }
    }

    const handleDeleteUser = async (userId: number) => {
        if (!window.confirm('Bạn có chắc chắn muốn xóa người dùng này?')) return;
        try {
            const token = localStorage.getItem('access_token');
            await axios.delete(`/api/v1/users/${userId}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            fetchUsers();
        } catch (err) {
            alert('Lỗi khi xóa người dùng');
        }
    }

    const filteredUsers = users.filter(u =>
        u.email.toLowerCase().includes(filter.toLowerCase()) ||
        (u.full_name && u.full_name.toLowerCase().includes(filter.toLowerCase()))
    );

    return (
        <Layout>
            <div className="p-4 md:p-8 max-w-6xl mx-auto space-y-6">
                {/* Header Section */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-2">
                    <div className="flex items-center gap-4">
                        <div className="bg-blue-600 p-3 rounded-full text-white shadow-lg">
                            <Users size={28} />
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold text-gray-800">Quản lý người dùng</h2>
                            <p className="text-sm text-gray-500">Xem và phân quyền cho các thành viên trong hệ thống</p>
                        </div>
                    </div>

                    <div className="flex flex-col md:flex-row gap-3">
                        <div className="relative w-full md:w-64">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                            <input
                                type="text"
                                placeholder="Tìm kiếm tài khoản..."
                                className="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-full text-sm outline-none focus:ring-2 focus:ring-blue-100 focus:border-blue-400 transition-all shadow-sm"
                                value={filter}
                                onChange={(e) => setFilter(e.target.value)}
                            />
                        </div>
                        <Button
                            onClick={openCreateModal}
                            className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold gap-2 px-6 rounded-full shadow-md"
                        >
                            <UserPlus size={18} /> THÊM MỚI
                        </Button>
                    </div>
                </div>

                {/* Unified User Modal Overlay */}
                {isModalOpen && (
                    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[60] flex items-center justify-center p-4">
                        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in duration-200">
                            <div className={`${editingUser ? 'bg-blue-600' : 'bg-emerald-600'} px-6 py-4 flex justify-between items-center text-white`}>
                                <h3 className="font-bold text-lg flex items-center gap-2">
                                    {editingUser ? <Edit2 size={20} /> : <UserPlus size={20} />}
                                    {editingUser ? 'Chỉnh sửa tài khoản' : 'Tạo tài khoản mới'}
                                </h3>
                                <button onClick={() => setIsModalOpen(false)} className="opacity-80 hover:opacity-100 p-1 rounded-full transition-colors">
                                    <X size={24} />
                                </button>
                            </div>
                            <form onSubmit={handleSaveUser} className="p-6 space-y-4">
                                {formError && (
                                    <div className="p-3 bg-red-50 text-red-600 text-xs font-bold rounded-lg border border-red-100 flex items-center gap-2">
                                        <X size={14} /> {formError}
                                    </div>
                                )}
                                <div>
                                    <label className="block text-xs font-bold text-gray-500 mb-1.5 uppercase tracking-wider">Địa chỉ Email</label>
                                    <div className="relative">
                                        <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
                                        <input
                                            type="email"
                                            required
                                            className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-blue-100 focus:border-blue-500"
                                            placeholder="user@example.com"
                                            value={formUser.email}
                                            onChange={(e) => setFormUser({ ...formUser, email: e.target.value })}
                                        />
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-xs font-bold text-gray-500 mb-1.5 uppercase tracking-wider">
                                        {editingUser ? 'Mật khẩu mới (Bỏ trống nếu không đổi)' : 'Mật khẩu ban đầu'}
                                    </label>
                                    <div className="relative">
                                        <Key className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
                                        <input
                                            type="password"
                                            required={!editingUser}
                                            className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-blue-100 focus:border-blue-500"
                                            placeholder="••••••••"
                                            value={formUser.password}
                                            onChange={(e) => setFormUser({ ...formUser, password: e.target.value })}
                                        />
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-xs font-bold text-gray-500 mb-1.5 uppercase tracking-wider">Họ và Tên</label>
                                    <input
                                        type="text"
                                        className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-blue-100 focus:border-blue-500"
                                        placeholder="Nguyễn Văn A"
                                        value={formUser.full_name}
                                        onChange={(e) => setFormUser({ ...formUser, full_name: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs font-bold text-gray-500 mb-1.5 uppercase tracking-wider">Quyền hạn (Role)</label>
                                    <select
                                        className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-blue-100 focus:border-blue-500 appearance-none bg-no-repeat bg-[right_1rem_center]"
                                        value={formUser.role}
                                        onChange={(e) => setFormUser({ ...formUser, role: e.target.value })}
                                    >
                                        <option value="free">FREE</option>
                                        <option value="premium">PREMIUM</option>
                                        <option value="admin">ADMIN</option>
                                    </select>
                                </div>
                                <div className="pt-2 flex gap-3">
                                    <Button
                                        type="button"
                                        variant="ghost"
                                        className="flex-1 font-bold text-gray-500"
                                        onClick={() => setIsModalOpen(false)}
                                    >
                                        HỦY BỎ
                                    </Button>
                                    <Button
                                        type="submit"
                                        className={`flex-1 ${editingUser ? 'bg-blue-600 hover:bg-blue-700 shadow-blue-200' : 'bg-emerald-600 hover:bg-emerald-700 shadow-emerald-200'} text-white font-bold shadow-lg`}
                                    >
                                        {editingUser ? 'LƯU THAY ĐỔI' : 'TẠO NGAY'}
                                    </Button>
                                </div>
                            </form>
                        </div>
                    </div>
                )}

                <Card className="shadow-xl border-none overflow-hidden">
                    <CardContent className="p-0">
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm text-left">
                                <thead className="bg-gray-50 text-gray-600 font-bold uppercase text-[10px] tracking-wider border-b border-gray-100">
                                    <tr>
                                        <th className="px-6 py-4">Người dùng</th>
                                        <th className="px-6 py-4">Vai trò</th>
                                        <th className="px-6 py-4">Trạng thái</th>
                                        <th className="px-6 py-4">Ngày tham gia</th>
                                        <th className="px-6 py-4 text-right">Thao tác</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-50">
                                    {filteredUsers.map((user) => (
                                        <tr key={user.id} className="hover:bg-blue-50/30 transition-colors">
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-3">
                                                    <div className="w-9 h-9 rounded-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center text-gray-500 font-bold shadow-inner">
                                                        {(user.full_name?.[0] || user.email[0]).toUpperCase()}
                                                    </div>
                                                    <div>
                                                        <div className="font-bold text-gray-800">{user.full_name || 'Chưa cập nhật tên'}</div>
                                                        <div className="text-xs text-gray-500 flex items-center gap-1"><Mail size={12} /> {user.email}</div>
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <span
                                                    onClick={() => openEditModal(user)}
                                                    className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold cursor-pointer hover:opacity-80 transition-all ${user.role === 'admin' ? 'bg-red-100 text-red-700' :
                                                        user.role === 'premium' ? 'bg-amber-100 text-amber-700' :
                                                            'bg-gray-100 text-gray-700'
                                                        }`}
                                                >
                                                    {user.role === 'admin' && <Shield size={10} />}
                                                    {user.role.toUpperCase()}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <button
                                                    onClick={() => handleToggleStatus(user)}
                                                    className={`flex items-center gap-1.5 font-bold text-xs transition-colors ${user.is_active ? 'text-emerald-600 hover:text-emerald-700' : 'text-red-500 hover:text-red-600'}`}
                                                >
                                                    {user.is_active ? <Check size={14} /> : <X size={14} />}
                                                    {user.is_active ? 'Hoạt động' : 'Đã khóa'}
                                                </button>
                                            </td>
                                            <td className="px-6 py-4 text-xs text-gray-500">
                                                {new Date(user.created_at).toLocaleDateString()}
                                            </td>
                                            <td className="px-6 py-4 text-right">
                                                <div className="flex justify-end gap-2">
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        className="h-8 w-8 p-0 text-gray-400 hover:text-blue-600 hover:bg-blue-50"
                                                        onClick={() => openEditModal(user)}
                                                    >
                                                        <Edit2 size={16} />
                                                    </Button>
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        className="h-8 w-8 p-0 text-gray-400 hover:text-red-600 hover:bg-red-50"
                                                        onClick={() => handleDeleteUser(user.id)}
                                                    >
                                                        <Trash2 size={16} />
                                                    </Button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                    {filteredUsers.length === 0 && (
                                        <tr>
                                            <td colSpan={5} className="px-6 py-10 text-center text-gray-400 italic">
                                                {loading ? 'Đang tải danh sách...' : 'Không tìm thấy người dùng nào.'}
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </Layout>
    );
}
