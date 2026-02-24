import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Shield, Lock } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            const formData = new FormData();
            formData.append('username', email);
            formData.append('password', password);

            const response = await fetch('/api/v1/auth/login', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('access_token', data.access_token);
                navigate('/dashboard');
            } else {
                alert('Sai thông tin đăng nhập');
            }
        } catch (error) {
            alert('Lỗi kết nối mạng');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden bg-gray-50">
            {/* Vietlott Red Header Accent */}
            <div className="absolute top-0 left-0 right-0 h-64 bg-gradient-to-b from-[var(--color-vietlott-red)] to-red-700 select-none z-0" />

            <Card className="max-w-md w-full z-10 p-2 shadow-vietlott border-none">
                <CardHeader className="text-center pb-6">
                    <div className="mx-auto bg-red-100 rounded-full w-16 h-16 flex items-center justify-center mb-4">
                        <Shield className="text-[var(--color-vietlott-red)]" size={32} />
                    </div>
                    <CardTitle className="text-2xl justify-center font-bold text-[var(--color-text-main)]">
                        Hệ thống Quản trị AI
                    </CardTitle>
                    <CardDescription className="text-[var(--color-text-muted)] mt-2">
                        Đăng nhập để xem dự báo và lịch sử xổ số
                    </CardDescription>
                </CardHeader>

                <CardContent>
                    <form onSubmit={handleLogin} className="space-y-5">
                        <div className="space-y-2">
                            <label className="text-sm font-semibold text-[var(--color-text-main)]">Email</label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full bg-white border border-gray-200 rounded-md p-3 text-[var(--color-text-main)] focus:outline-none focus:border-[var(--color-vietlott-red)] focus:ring-1 focus:ring-[var(--color-vietlott-red)] transition-all"
                                placeholder="admin@vietlott.dev"
                                required
                            />
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-semibold text-[var(--color-text-main)]">Mật khẩu</label>
                            <div className="relative">
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full bg-white border border-gray-200 rounded-md p-3 text-[var(--color-text-main)] focus:outline-none focus:border-[var(--color-vietlott-red)] focus:ring-1 focus:ring-[var(--color-vietlott-red)] pl-10 transition-all"
                                    placeholder="••••••••"
                                    required
                                />
                                <Lock className="absolute left-3 top-3.5 text-gray-400" size={18} />
                            </div>
                        </div>

                        <Button type="submit" variant="primary" className="w-full h-12 text-lg mt-6 shadow-md" disabled={loading}>
                            {loading ? 'Đang xác thực...' : 'Đăng Nhập'}
                        </Button>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}
