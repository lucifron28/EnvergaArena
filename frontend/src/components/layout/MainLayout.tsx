import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import Footer from './Footer';

export default function MainLayout() {
    return (
        <div className="flex flex-col min-h-screen font-sans bg-ivory text-charcoal">
            <Navbar />
            <main className="flex-grow w-full max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
                <Outlet />
            </main>
            <Footer />
        </div>
    );
}
