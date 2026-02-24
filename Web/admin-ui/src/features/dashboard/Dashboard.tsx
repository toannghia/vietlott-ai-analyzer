import { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Shield, RefreshCw, TrendingUp, History, ChevronLeft, ChevronRight } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useSearchParams } from 'react-router-dom';
import { cn } from '../../lib/utils';
import axios from 'axios';
import { Layout } from '../../components/layout/Layout';

// Dữ liệu mẫu ban đầu (sẽ được thay thế bởi accuracyData)
const mockChartData = Array.from({ length: 15 }).map((_, i) => ({
    draw: `Kỳ ${100 - i}`,
    confidence: 50,
    matches: 0
})).reverse();

export function Dashboard() {
    // const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [searchParams, setSearchParams] = useSearchParams();
    const lotteryType = searchParams.get('type') || 'mega645';
    const [prediction, setPrediction] = useState<any>(null);
    const [history, setHistory] = useState<any[]>([]);
    const [accuracyData, setAccuracyData] = useState<any[]>([]);
    const [statsSummary, setStatsSummary] = useState<any>(null);
    const [cooccurrenceStats, setCooccurrenceStats] = useState<any>(null);
    const [currentPage, setCurrentPage] = useState(1);
    const [pastCursor, setPastCursor] = useState(0);
    const [totalCount, setTotalCount] = useState(0);
    const [latestDraw, setLatestDraw] = useState<any>(null);
    const pageSize = 10;
    const [logs, setLogs] = useState<string[]>([
        "[OK] Đã kết nối Hệ thống. Sẵn sàng.",
        "[INFO] Đang chờ đồng bộ dữ liệu AI..."
    ]);

    useEffect(() => {
        fetchData();
    }, [lotteryType]);

    const fetchData = async () => {
        setLoading(true);
        await Promise.all([
            fetchLatestPrediction(),
            fetchHistory(1),
            fetchAccuracy(),
            fetchStatsSummary(),
            fetchCooccurrenceStats()
        ]);
        setLoading(false);
    }

    const fetchLatestPrediction = async () => {
        try {
            const token = localStorage.getItem('access_token');
            const headers = token ? { Authorization: `Bearer ${token}` } : {};

            const res = await axios.get(`/api/v1/predictions/latest?type=${lotteryType}`, { headers });
            setPrediction(res.data);
            addLog(`[OK] Tải dự báo ${lotteryType} kỳ ${res.data.target_period}.`);
        } catch (err: any) {
            setPrediction(null);
            addLog(`[WARN] Không có dữ liệu dự báo cho ${lotteryType}.`);
        }
    };

    const fetchAccuracy = async () => {
        try {
            const token = localStorage.getItem('access_token');
            const headers = token ? { Authorization: `Bearer ${token}` } : {};

            const res = await axios.get(`/api/v1/predictions/accuracy?type=${lotteryType}`, { headers });

            // Raw history is now stored completely for the Past Prediction block, and chart uses it too.
            const historyList = res.data.history || [];

            const chartData = historyList.map((item: any) => ({
                draw: `Kỳ ${item.period}`,
                confidence: item.confidence,
                matches: item.matches,
                actual: item.actual,
                predicted: item.predicted
            })).reverse();

            setAccuracyData(chartData); // Note: chartData is reversed (oldest first for chart). History list is newest first.
            setPastCursor(0);
        } catch (err: any) {
            setAccuracyData([]);
            addLog(`[WARN] Không thể lấy dữ liệu độ chính xác ${lotteryType}.`);
        }
    };

    const fetchStatsSummary = async () => {
        try {
            const token = localStorage.getItem('access_token');
            const headers = token ? { Authorization: `Bearer ${token}` } : {};

            const res = await axios.get(`/api/v1/stats/summary?type=${lotteryType}`, { headers });
            setStatsSummary(res.data);
        } catch (err: any) {
            setStatsSummary(null);
            addLog(`[WARN] Không thể lấy thống kê bóng ${lotteryType}.`);
        }
    };

    const fetchCooccurrenceStats = async () => {
        try {
            const token = localStorage.getItem('access_token');
            const headers = token ? { Authorization: `Bearer ${token}` } : {};

            const res = await axios.get(`/api/v1/stats/cooccurrence?type=${lotteryType}`, { headers });
            setCooccurrenceStats(res.data);
        } catch (err: any) {
            setCooccurrenceStats(null);
        }
    };

    const fetchHistory = async (page: number) => {
        try {
            const token = localStorage.getItem('access_token');
            const headers = token ? { Authorization: `Bearer ${token}` } : {};

            const res = await axios.get(`/api/v1/crawler/history?type=${lotteryType}&page=${page}&limit=${pageSize}`, { headers });
            setHistory(res.data.data || []);
            setTotalCount(res.data.total || 0);
            setLatestDraw(res.data.latest_draw || null);
            setCurrentPage(page);
        } catch (err: any) {
            console.error(err);
            setHistory([]);
            addLog(`[ERROR] Lỗi tải lịch sử ${lotteryType}.`);
        }
    };

    const addLog = (msg: string) => {
        setLogs(prev => [msg, ...prev].slice(0, 5));
    };

    const handleRefresh = async () => {
        if (loading) return;
        setLoading(true);
        addLog(`[INFO] Đang yêu cầu cào dữ liệu ${lotteryType} mới nhất...`);
        try {
            const token = localStorage.getItem('access_token');
            const headers = token ? { Authorization: `Bearer ${token}` } : {};
            await axios.post(`/api/v1/crawler/run?type=${lotteryType}`, {}, { headers });
            addLog(`[OK] Đã gửi lệnh cào ${lotteryType}. Hệ thống đang xử lý ngầm...`);

            // Wait a bit longer for the background task to at least start/finish
            setTimeout(async () => {
                await fetchData();
                addLog(`[OK] Đã đồng bộ dữ liệu ${lotteryType} mới nhất từ máy chủ.`);
                setLoading(false);
            }, 3000);
        } catch (e) {
            addLog(`[WARN] Lỗi không thể gọi Crawler cho ${lotteryType}.`);
            setLoading(false);
        }
    };

    return (
        <Layout>
            <div className="flex flex-col w-full min-h-screen bg-[var(--color-bg-light)]">
                {/* Secondary Header for Lottery Selection */}
                <div className="bg-white border-b border-gray-100 px-6 py-3 flex items-center justify-between sticky top-[72px] z-40 shadow-sm">
                    <div className="flex items-center gap-4">
                        <span className="text-sm font-bold text-gray-500 uppercase tracking-wider">Chế độ xem:</span>
                        <select
                            value={lotteryType}
                            onChange={(e) => {
                                setSearchParams({ type: e.target.value });
                                setPastCursor(0);
                                addLog(`[INFO] Chuyển chế độ xem sang ${e.target.value === 'mega645' ? 'Mega 6/45' : 'Power 6/55'}...`);
                            }}
                            className="bg-gray-50 text-[var(--color-vietlott-red)] text-sm border border-gray-200 rounded-lg px-4 py-2 outline-none font-bold cursor-pointer hover:bg-gray-100 transition-colors"
                        >
                            <option value="mega645">MEGA 6/45 – KỲ 6 SỐ</option>
                            <option value="power655">POWER 6/55 – KỲ 7 SỐ</option>
                        </select>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="text-[11px] text-gray-400 font-sans font-bold uppercase tracking-widest opacity-60">LSTM_V1.2_PRO</span>
                        <div className="h-4 w-[1px] bg-gray-200 mx-2" />
                        <span className="text-xs text-emerald-600 font-bold flex items-center gap-1.5">
                            <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                            CORE CONNECTED
                        </span>
                    </div>
                </div>

                <div className="p-4 md:p-6 lg:p-8 max-w-[1600px] mx-auto w-full">
                    {/* Stats Summary Blocks */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                        <Card className="bg-gradient-to-br from-red-50 to-white shadow-sm border-l-4 border-l-[var(--color-vietlott-red)]">
                            <CardContent className="p-5 flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-gray-500 font-semibold mb-1">TỔNG SỐ KỲ QUAY (CRAWLED)</p>
                                    <h3 className="text-3xl font-bold text-[var(--color-vietlott-red)]">{latestDraw ? latestDraw.draw_period : '...'}</h3>
                                </div>
                                <div className="bg-red-100 p-3 rounded-full text-red-600">
                                    <History size={24} />
                                </div>
                            </CardContent>
                        </Card>
                        <Card className="bg-gradient-to-br from-amber-50 to-white shadow-sm border-l-4 border-l-[var(--color-lucky-gold)]">
                            <CardContent className="p-5 flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-gray-500 font-semibold mb-1">
                                        {lotteryType === 'power655' ? 'JACKPOT 1 MỚI NHẤT' : 'GIÁ TRỊ JACKPOT MỚI NHẤT'}
                                    </p>
                                    <h3 className="text-3xl font-bold text-amber-600">
                                        {latestDraw ? (latestDraw.jackpot_value / 1000000000).toFixed(1) + ' Tỷ' : '...'}
                                    </h3>
                                    {lotteryType === 'power655' && latestDraw && (
                                        <p className="text-xs text-amber-700 font-bold mt-1">
                                            JP2: {(latestDraw.jackpot2_value / 1000000000).toFixed(1)} Tỷ
                                        </p>
                                    )}
                                </div>
                                <div className="bg-amber-100 p-3 rounded-full text-amber-600">
                                    <TrendingUp size={24} />
                                </div>
                            </CardContent>
                        </Card>
                        <Card className="bg-gradient-to-br from-emerald-50 to-white shadow-sm border-l-4 border-l-emerald-500">
                            <CardContent className="p-5 flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-gray-500 font-semibold mb-1">TRẠNG THÁI MODEL LSTM</p>
                                    <h3 className="text-emerald-600 font-bold text-xl flex items-center gap-2 mt-2">
                                        <span className="relative flex h-3 w-3">
                                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                                            <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                                        </span>
                                        ONLINE / ACTIVE
                                    </h3>
                                </div>
                                <div className="bg-emerald-100 p-3 rounded-full text-emerald-600">
                                    <Shield size={24} />
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Optimized Statistics Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-10 gap-4 mb-8">
                        {/* TOP HOT */}
                        <Card className="bg-white shadow-sm border-t-4 border-t-red-500 overflow-hidden lg:col-span-2">
                            <CardHeader className="py-2 px-4 flex flex-row items-center justify-between space-y-0 pb-1">
                                <CardTitle className="text-[11px] font-bold text-red-600 uppercase tracking-tight">6 Bóng Ra Nhiều Nhất</CardTitle>
                                <TrendingUp size={14} className="text-red-500" />
                            </CardHeader>
                            <CardContent className="p-4 pt-1">
                                <div className="flex flex-wrap gap-2 justify-between">
                                    {(statsSummary?.hot || []).slice(0, 6).map((s: any, idx: number) => (
                                        <div key={idx} className="flex flex-col items-center">
                                            <div className="w-8 h-8 rounded-full bg-red-600 text-white text-xs font-bold flex items-center justify-center shadow-sm border border-white">
                                                {String(s.number).padStart(2, '0')}
                                            </div>
                                            <span className="text-[9px] text-gray-500 font-bold mt-1">{s.frequency}L</span>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>

                        {/* TOP COLD */}
                        <Card className="bg-white shadow-sm border-t-4 border-t-blue-500 overflow-hidden lg:col-span-2">
                            <CardHeader className="py-2 px-4 flex flex-row items-center justify-between space-y-0 pb-1">
                                <CardTitle className="text-[11px] font-bold text-blue-600 uppercase tracking-tight">6 Bóng Ra Ít Nhất</CardTitle>
                                <TrendingUp size={14} className="text-blue-500 rotate-180" />
                            </CardHeader>
                            <CardContent className="p-4 pt-1">
                                <div className="flex flex-wrap gap-2 justify-between">
                                    {(statsSummary?.cold || []).slice(0, 6).map((s: any, idx: number) => (
                                        <div key={idx} className="flex flex-col items-center">
                                            <div className="w-8 h-8 rounded-full bg-blue-600 text-white text-xs font-bold flex items-center justify-center shadow-sm border border-white">
                                                {String(s.number).padStart(2, '0')}
                                            </div>
                                            <span className="text-[9px] text-gray-500 font-bold mt-1">{s.frequency}L</span>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>

                        {/* TOP PAIRS */}
                        <Card className="bg-white shadow-sm border-t-4 border-t-purple-500 overflow-hidden lg:col-span-3">
                            <CardHeader className="py-2 px-4 flex flex-row items-center justify-between space-y-0 pb-1">
                                <CardTitle className="text-[11px] font-bold text-purple-700 uppercase tracking-tight">Top 5 Cặp 2 Số Hay Ra Cùng</CardTitle>
                                <TrendingUp size={14} className="text-purple-500" />
                            </CardHeader>
                            <CardContent className="p-3 pt-1">
                                <div className="flex flex-wrap gap-2 justify-center lg:justify-between px-1">
                                    {(cooccurrenceStats?.pairs || []).slice(0, 5).map((p: any, idx: number) => (
                                        <div key={idx} className="flex flex-col items-center bg-purple-50 p-1 rounded border border-purple-100 min-w-[62px]">
                                            <div className="flex gap-0.5">
                                                {p.numbers.map((n: number) => (
                                                    <div key={n} className="w-6 h-6 rounded-full bg-purple-600 text-white text-[10px] font-bold flex items-center justify-center">
                                                        {String(n).padStart(2, '0')}
                                                    </div>
                                                ))}
                                            </div>
                                            <span className="text-[9px] text-purple-700 font-bold mt-1">{p.count}L</span>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>

                        {/* TOP TRIPLETS */}
                        <Card className="bg-white shadow-sm border-t-4 border-t-emerald-500 overflow-hidden lg:col-span-3">
                            <CardHeader className="py-2 px-4 flex flex-row items-center justify-between space-y-0 pb-1">
                                <CardTitle className="text-[11px] font-bold text-emerald-700 uppercase tracking-tight">Top 4 Bộ 3 Số Hay Ra Cùng</CardTitle>
                                <TrendingUp size={14} className="text-emerald-500" />
                            </CardHeader>
                            <CardContent className="p-3 pt-1">
                                <div className="flex flex-wrap gap-2 justify-center lg:justify-between px-1">
                                    {(cooccurrenceStats?.triplets || []).slice(0, 4).map((t: any, idx: number) => (
                                        <div key={idx} className="flex flex-col items-center bg-emerald-50 p-1 rounded border border-emerald-100 min-w-[82px]">
                                            <div className="flex gap-0.5">
                                                {t.numbers.map((n: number) => (
                                                    <div key={n} className="w-6 h-6 rounded-full bg-emerald-600 text-white text-[10px] font-bold flex items-center justify-center">
                                                        {String(n).padStart(2, '0')}
                                                    </div>
                                                ))}
                                            </div>
                                            <span className="text-[9px] text-emerald-700 font-bold mt-1">{t.count}L</span>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    <div className="flex flex-col lg:flex-row gap-6 lg:gap-8 items-start">

                        {/* 70% Left - Analytics & History */}
                        <div className="w-full lg:w-[70%] space-y-6">
                            <Card className="h-[430px]">
                                <CardHeader className="py-4">
                                    <CardTitle className="text-[var(--color-text-main)] flex items-center gap-2">
                                        <TrendingUp size={18} className="text-[var(--color-vietlott-red)]" /> Phân Tích Độ Tự Tin Dự Báo (30 Kỳ)
                                    </CardTitle>
                                </CardHeader>
                                <CardContent className="h-[340px]">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <LineChart data={accuracyData.length > 0 ? accuracyData : mockChartData}>
                                            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
                                            <XAxis
                                                dataKey="draw"
                                                stroke="#64748B"
                                                fontSize={10}
                                                tickLine={false}
                                                axisLine={false}
                                                interval="preserveStartEnd"
                                                minTickGap={30}
                                            />
                                            <YAxis yAxisId="left" stroke="#64748B" fontSize={12} tickLine={false} axisLine={false} domain={[0, 100]} />
                                            <YAxis yAxisId="right" orientation="right" stroke="#FFB800" fontSize={12} tickLine={false} axisLine={false} domain={[0, 6]} />
                                            <Tooltip
                                                contentStyle={{ backgroundColor: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                                itemStyle={{ fontWeight: 'bold' }}
                                            />
                                            <Line
                                                yAxisId="left"
                                                type="monotone"
                                                dataKey="confidence"
                                                name="Độ Tự Tin (%)"
                                                stroke="var(--color-vietlott-red)"
                                                strokeWidth={3}
                                                dot={{ fill: "#FFFFFF", stroke: "var(--color-vietlott-red)", strokeWidth: 2, r: 4 }}
                                                activeDot={{ r: 6, fill: "var(--color-vietlott-red)" }}
                                            />
                                            <Line
                                                yAxisId="right"
                                                type="monotone"
                                                dataKey="matches"
                                                name="Số Bóng Trùng"
                                                stroke="var(--color-lucky-gold)"
                                                strokeWidth={3}
                                                dot={{ fill: "#FFFFFF", stroke: "var(--color-lucky-gold)", strokeWidth: 2, r: 4 }}
                                                activeDot={{ r: 6, fill: "var(--color-lucky-gold)" }}
                                            />
                                        </LineChart>
                                    </ResponsiveContainer>
                                </CardContent>
                            </Card>

                            {/* DATA TABLE */}
                            <Card>
                                <CardHeader className="py-4">
                                    <div className="flex items-center gap-2">
                                        <History size={18} className="text-[var(--color-lucky-gold)]" />
                                        <CardTitle className="text-[var(--color-text-main)]">Lịch Sử Dữ Liệu Đã Cào</CardTitle>
                                    </div>
                                    <CardDescription>Danh sách các kỳ quay đã được AI thu thập và học mảng</CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <div className="overflow-x-auto">
                                        <table className="w-full text-xs text-left whitespace-nowrap">
                                            <thead className="bg-[#FFF4F2] text-[var(--color-vietlott-red)] font-semibold border-b border-red-100">
                                                <tr>
                                                    <th className="px-3 py-3 rounded-tl-md">Kỳ Quay</th>
                                                    <th className="px-3 py-3">Ngày</th>
                                                    <th className="px-3 py-3 text-center">Kết Quả Bóng</th>
                                                    <th className="px-3 py-3 text-right">Jackpot</th>
                                                    <th className="px-3 py-3 text-right">Giải Nhất</th>
                                                    <th className="px-3 py-3 text-right">Giải Nhì</th>
                                                    <th className="px-3 py-3 text-right rounded-tr-md">Giải Ba</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {history.length > 0 ? history.map((row: any) => (
                                                    <tr key={row.draw_period} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                                                        <td className="px-3 py-3 font-semibold text-gray-700">#{row.draw_period}</td>
                                                        <td className="px-3 py-3 text-gray-500">{new Date(row.draw_date).toLocaleDateString()}</td>
                                                        <td className="px-3 py-3 text-center">
                                                            <div className="flex gap-1 justify-center">
                                                                {(row.numbers || []).map((n: number, i: number) => (
                                                                    <span key={i} className={`inline-flex w-6 h-6 rounded-full items-center justify-center text-[10px] font-bold border shadow-sm ${(lotteryType === 'power655' && i === 6)
                                                                        ? 'bg-amber-400 text-amber-900 border-amber-500'
                                                                        : 'bg-red-100 text-[var(--color-vietlott-red-dark)] border-red-200'
                                                                        }`}>
                                                                        {String(n).padStart(2, '0')}
                                                                    </span>
                                                                ))}
                                                            </div>
                                                        </td>
                                                        <td className="px-3 py-3 text-right">
                                                            <div className="font-mono font-bold text-[var(--color-vietlott-red)]">
                                                                {row.jackpot_value ? (row.jackpot_value / 1000000).toLocaleString('vi-VN') + 'M' : '---'}
                                                            </div>
                                                            {lotteryType === 'power655' && (
                                                                <div className="font-mono text-[10px] text-amber-600 font-bold">
                                                                    JP2: {row.jackpot2_value ? (row.jackpot2_value / 1000000).toLocaleString('vi-VN') + 'M' : '---'}
                                                                </div>
                                                            )}
                                                            <div className="text-[10px] text-gray-400">
                                                                {row.jackpot_winners + (row.jackpot2_winners || 0)} giải
                                                            </div>
                                                        </td>
                                                        <td className="px-3 py-3 text-right">
                                                            <div className="font-mono text-gray-700">{row.first_prize_value ? row.first_prize_value.toLocaleString('vi-VN') : '---'}</div>
                                                            <div className="text-[10px] text-gray-400">{row.first_prize_winners || 0} giải</div>
                                                        </td>
                                                        <td className="px-3 py-3 text-right">
                                                            <div className="font-mono text-gray-700">{row.second_prize_value ? row.second_prize_value.toLocaleString('vi-VN') : '---'}</div>
                                                            <div className="text-[10px] text-gray-400">{row.second_prize_winners || 0} giải</div>
                                                        </td>
                                                        <td className="px-3 py-3 text-right">
                                                            <div className="font-mono text-gray-700">{row.third_prize_value ? row.third_prize_value.toLocaleString('vi-VN') : '---'}</div>
                                                            <div className="text-[10px] text-gray-400">{row.third_prize_winners || 0} giải</div>
                                                        </td>
                                                    </tr>
                                                )) : (
                                                    <tr><td colSpan={7} className="text-center py-6 text-gray-400 bg-gray-50 italic">Đang tải dữ liệu từ Crawler...</td></tr>
                                                )}
                                            </tbody>
                                        </table>
                                    </div>

                                    {/* Pagination Controls */}
                                    <div className="mt-4 flex items-center justify-between border-t border-gray-100 pt-4">
                                        <div className="text-sm text-gray-500">
                                            Hiển thị <span className="font-medium text-gray-700">{history.length}</span> trên <span className="font-medium text-gray-700">{totalCount}</span> kỳ quay
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={() => fetchHistory(currentPage - 1)}
                                                disabled={currentPage <= 1 || loading}
                                                className="h-8 w-8 p-0"
                                            >
                                                <ChevronLeft size={16} />
                                            </Button>
                                            <div className="text-sm font-medium text-gray-700 min-w-[60px] text-center">
                                                Trang {currentPage} / {Math.ceil(totalCount / pageSize) || 1}
                                            </div>
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={() => fetchHistory(currentPage + 1)}
                                                disabled={currentPage >= Math.ceil(totalCount / pageSize) || loading}
                                                className="h-8 w-8 p-0"
                                            >
                                                <ChevronRight size={16} />
                                            </Button>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        </div>

                        {/* 30% Right - Predictive Control Panel (Sticky) */}
                        <div className="w-full lg:w-[30%] lg:sticky lg:top-24 space-y-6">
                            <Card className="border-[var(--color-lucky-gold)] border-t-4 shadow-md">
                                <CardHeader className="bg-gradient-to-br from-red-50 to-white pb-6">
                                    <CardTitle className="text-[var(--color-vietlott-red)] text-xl items-center pb-1">
                                        SIÊU MÁY TÍNH DỰ BÁO
                                    </CardTitle>
                                    <CardDescription className="text-[var(--color-text-main)] font-medium">
                                        Đang dự báo cho kỳ: <span className="text-[var(--color-vietlott-red)] font-bold text-lg">{prediction ? `#${prediction.target_period} ` : '---'}</span>
                                    </CardDescription>
                                </CardHeader>

                                <CardContent className="space-y-6 pt-5">
                                    <div className="space-y-4">
                                        <p className="text-sm font-semibold text-[var(--color-text-muted)] mb-2">CÁC BỘ SỐ TIỀM NĂNG NHẤT (ENSEMBLE)</p>
                                        {prediction?.prediction_sets && prediction.prediction_sets.length > 0 ? (
                                            prediction.prediction_sets.map((set: any, setIdx: number) => (
                                                <div key={setIdx} className="bg-white rounded-lg p-3 border border-red-100 shadow-sm relative">
                                                    <div className="absolute -top-2.5 -left-2.5 bg-red-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-full shadow-sm border border-white">
                                                        TOP {setIdx + 1}
                                                    </div>
                                                    <div className="absolute top-2 right-2 flex items-center gap-1 bg-red-50 text-[var(--color-vietlott-red)] px-2 py-0.5 rounded text-[10px] font-bold border border-red-100">
                                                        Tỷ lệ: {Number(set.confidence).toFixed(1)}%
                                                    </div>
                                                    <div className="flex flex-wrap gap-1.5 justify-center mt-3">
                                                        {set.numbers.map((num: any, idx: number) => (
                                                            <div key={idx} className={`w-[36px] h-[36px] rounded-full flex items-center justify-center font-sans text-sm font-bold border-2 ${setIdx === 0 ? 'bg-[var(--color-vietlott-red)] border-[var(--color-lucky-gold)] text-white shadow-sm' : 'bg-red-50 border-red-200 text-[var(--color-vietlott-red)]'}`}>
                                                                {num === -1 ? '?' : String(num).padStart(2, '0')}
                                                            </div>
                                                        ))}
                                                    </div>
                                                </div>
                                            ))
                                        ) : (
                                            <div className="flex flex-wrap gap-2 justify-center">
                                                {(prediction?.predicted_numbers || [0, 0, 0, 0, 0, 0]).map((num: any, idx: number) => (
                                                    <div key={idx} className="w-[48px] h-[48px] rounded-full flex items-center justify-center font-sans text-xl font-bold bg-[var(--color-vietlott-red)] border-2 border-[var(--color-lucky-gold)] text-white shadow-vietlott">
                                                        {num === -1 ? '?' : String(num).padStart(2, '0')}
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>

                                    {!prediction?.prediction_sets && (
                                        <div className="pt-5 border-t border-gray-100">
                                            <div className="flex justify-between items-center mb-2">
                                                <span className="text-sm font-semibold text-[var(--color-text-muted)]">CƠ HỘI TRÚNG GIẢI</span>
                                                <span className="text-[var(--color-vietlott-red)] font-bold text-lg">
                                                    {prediction ? `${typeof prediction.confidence === 'number' ? prediction.confidence.toFixed(1) : prediction.confidence}%` : '---'}
                                                </span>
                                            </div>
                                            <div className="h-3 w-full bg-gray-100 rounded-full overflow-hidden">
                                                <div className="h-full bg-gradient-to-r from-[var(--color-lucky-gold)] to-[var(--color-vietlott-red)] transition-all duration-1000 ease-out"
                                                    style={{ width: prediction ? `${typeof prediction.confidence === 'number' ? prediction.confidence : parseFloat(prediction.confidence)}%` : '0%' }} />
                                            </div>
                                        </div>
                                    )}

                                    <Button
                                        variant="primary"
                                        size="lg"
                                        className="w-full font-bold shadow-vietlott"
                                        onClick={handleRefresh}
                                        disabled={loading}
                                    >
                                        <RefreshCw size={18} className={cn("mr-2", loading && "animate-spin")} />
                                        {loading ? 'ĐANG PHÂN TÍCH DL...' : 'CẶP NHẬT KẾT QUẢ CRAWL'}
                                    </Button>
                                </CardContent>
                            </Card>

                            {/* PAST PREDICTIONS */}
                            {accuracyData.length > 0 && (
                                (() => {
                                    // Use the original history (which was reversed above). Since accuracyData is reversed,
                                    // we can reverse it back to get newest first, or just read from the end.
                                    const historyItems = [...accuracyData].reverse();
                                    const currentView = historyItems[pastCursor];
                                    if (!currentView) return null;

                                    const predicted = currentView.predicted || [];
                                    const actual = currentView.actual || [];

                                    return (
                                        <Card className="shadow-md">
                                            <CardHeader className="bg-gradient-to-br from-gray-50 to-white pb-4 border-b border-gray-100 flex flex-row items-center justify-between">
                                                <div>
                                                    <CardTitle className="text-gray-800 text-sm items-center pb-1 uppercase tracking-tight font-bold">
                                                        KẾT QUẢ DỰ BÁO TRƯỚC
                                                    </CardTitle>
                                                    <CardDescription className="text-gray-500 text-xs font-medium">
                                                        Kiểm chứng kỳ: <span className="text-gray-800 font-bold">{currentView.draw}</span>
                                                    </CardDescription>
                                                </div>
                                                <div className="flex items-center gap-1">
                                                    <Button variant="outline" size="sm" className="h-7 w-7 p-0"
                                                        onClick={() => setPastCursor(Math.max(0, pastCursor - 1))}
                                                        disabled={pastCursor === 0}>
                                                        <ChevronLeft size={14} />
                                                    </Button>
                                                    <Button variant="outline" size="sm" className="h-7 w-7 p-0"
                                                        onClick={() => setPastCursor(Math.min(historyItems.length - 1, pastCursor + 1))}
                                                        disabled={pastCursor === historyItems.length - 1}>
                                                        <ChevronRight size={14} />
                                                    </Button>
                                                </div>
                                            </CardHeader>
                                            <CardContent className="space-y-4 pt-4">
                                                <div>
                                                    <p className="text-[11px] font-bold text-gray-500 mb-2 uppercase tracking-wide">Số AI dự báo</p>
                                                    {currentView.prediction_sets && currentView.prediction_sets.length > 0 ? (
                                                        <div className="space-y-3">
                                                            {currentView.prediction_sets.map((set: any, setIdx: number) => {
                                                                const setMatches = set.numbers.filter((n: number) => actual.includes(n)).length;
                                                                return (
                                                                    <div key={setIdx} className={`rounded-xl p-2 border ${setIdx === 0 ? 'bg-red-50 border-red-100' : 'bg-gray-50 border-gray-100'}`}>
                                                                        <div className="flex justify-between items-center mb-2 px-1">
                                                                            <span className={`text-[10px] font-bold ${setIdx === 0 ? 'text-[var(--color-vietlott-red)]' : 'text-gray-500'}`}>
                                                                                TOP {setIdx + 1}
                                                                            </span>
                                                                            <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${setMatches > 0 ? 'bg-amber-100 text-amber-700' : 'bg-gray-200 text-gray-500'}`}>
                                                                                Trúng {setMatches}
                                                                            </span>
                                                                        </div>
                                                                        <div className="flex flex-wrap gap-1 justify-center">
                                                                            {set.numbers.map((num: number, idx: number) => {
                                                                                const isMatch = actual.includes(num);
                                                                                return (
                                                                                    <div key={idx} className={`w-[32px] h-[32px] rounded-full flex items-center justify-center font-sans text-xs font-bold border-2 
                                                                                        ${isMatch ? 'bg-[var(--color-lucky-gold)] border-amber-500 text-white shadow-sm' : 'bg-white border-gray-200 text-gray-500'}`}>
                                                                                        {String(num).padStart(2, '0')}
                                                                                    </div>
                                                                                );
                                                                            })}
                                                                        </div>
                                                                    </div>
                                                                );
                                                            })}
                                                        </div>
                                                    ) : (
                                                        <div className="flex flex-wrap gap-1.5 justify-center">
                                                            {predicted.map((num: number, idx: number) => {
                                                                const isMatch = actual.includes(num);
                                                                return (
                                                                    <div key={idx} className={`w-[36px] h-[36px] rounded-full flex items-center justify-center font-sans text-sm font-bold border-2 
                                                                        ${isMatch ? 'bg-[var(--color-lucky-gold)] border-amber-500 text-white shadow-sm' : 'bg-gray-100 border-gray-200 text-gray-400'}`}>
                                                                        {String(num).padStart(2, '0')}
                                                                    </div>
                                                                );
                                                            })}
                                                        </div>
                                                    )}
                                                </div>

                                                <div>
                                                    <p className="text-[11px] font-bold text-gray-500 mb-2 uppercase tracking-wide">Kết quả thực tế quay thưởng</p>
                                                    <div className="flex flex-wrap gap-1.5 justify-center">
                                                        {actual.map((num: number, idx: number) => {
                                                            // If we have prediction sets, check if ANY of the sets matched this actual number for visual highlight
                                                            const isMatch = currentView.prediction_sets
                                                                ? currentView.prediction_sets.some((s: any) => s.numbers.includes(num))
                                                                : predicted.includes(num);

                                                            return (
                                                                <div key={idx} className={`w-[36px] h-[36px] rounded-full flex items-center justify-center font-sans text-sm font-bold border 
                                                                    ${isMatch ? 'bg-[var(--color-lucky-gold)] border-amber-500 text-white shadow-sm' : 'bg-white border-gray-300 text-gray-700'}`}>
                                                                    {String(num).padStart(2, '0')}
                                                                </div>
                                                            );
                                                        })}
                                                    </div>
                                                </div>

                                                <div className="flex justify-between items-center bg-gray-50 p-3 rounded-lg border border-gray-100 mt-2">
                                                    <span className="text-xs font-bold text-gray-600 uppercase tracking-widest">ĐỘ CHÍNH XÁC TOP 1</span>
                                                    <span className="font-bold text-[var(--color-vietlott-red)] bg-red-100 px-3 py-1 rounded-full text-sm">
                                                        {currentView.matches} / {lotteryType === 'power655' ? '7' : '6'} bóng
                                                    </span>
                                                </div>
                                            </CardContent>
                                        </Card>
                                    );
                                })()
                            )}

                            <Card>
                                <CardHeader className="py-3">
                                    <CardTitle className="text-sm text-[var(--color-text-muted)]">NHẬT KÝ HỆ THỐNG</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="font-mono text-[11px] bg-gray-900 text-gray-300 p-3 rounded-md space-y-1">
                                        {logs.map((log, idx) => (
                                            <p key={idx} className={log.includes('[WARN]') ? 'text-[var(--color-lucky-gold)]' : 'text-gray-400'}>
                                                {log.includes('[OK]') ? <span className="text-[#A3E635]">[OK]</span> : null}
                                                {log.replace('[OK]', '')}
                                            </p>
                                        ))}
                                    </div>
                                </CardContent>
                            </Card>
                        </div>

                    </div>
                </div>
            </div>
        </Layout>
    );
}
