import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './context/AuthContext';

// Layout
import MainLayout from './components/layout/MainLayout';

// Public Pages
import Home from './pages/Public/Home';
import Schedules from './pages/Public/Schedules';
import Results from './pages/Public/Results';
import Rooney from './pages/Public/Rooney';

// Auth & Admin
import Login from './pages/Auth/Login';
import Dashboard from './pages/Admin/Dashboard';
import Masterlist from './pages/Admin/Masterlist';
import { ProtectedRoute } from './components/ProtectedRoute';

const queryClient = new QueryClient();

export default function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <AuthProvider>
                <BrowserRouter>
                    <Routes>
                        {/* Public Shell */}
                        <Route element={<MainLayout />}>
                            <Route path="/" element={<Home />} />
                            <Route path="/schedules" element={<Schedules />} />
                            <Route path="/results" element={<Results />} />
                            <Route path="/rooney" element={<Rooney />} />
                            <Route path="/login" element={<Login />} />

                            {/* Protected Admin Shell */}
                            <Route element={<ProtectedRoute allowedRoles={['admin', 'department_rep']} />}>
                                <Route path="/admin" element={<Dashboard />} />
                                <Route path="/admin/masterlist" element={<Masterlist />} />
                            </Route>
                        </Route>
                    </Routes>
                </BrowserRouter>
            </AuthProvider>
        </QueryClientProvider>
    );
}
