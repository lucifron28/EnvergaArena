import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Trophy, Calendar, Users, Home, LogIn, LayoutDashboard, LogOut, Bot } from 'lucide-react';

export default function Navbar() {
    const { isAuthenticated, user, logoutState } = useAuth();

    return (
        <div className="navbar bg-maroon text-white shadow-xl px-4 md:px-8 z-50 sticky top-0">
            <div className="navbar-start">
                <div className="dropdown">
                    <div tabIndex={0} role="button" className="btn btn-ghost lg:hidden text-white">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h8m-8 6h16" /></svg>
                    </div>
                    <ul tabIndex={0} className="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52 text-charcoal">
                        <li><NavLink to="/"><Home className="w-4 h-4"/> Home</NavLink></li>
                        <li><NavLink to="/schedules"><Calendar className="w-4 h-4"/> Schedules</NavLink></li>
                        <li><NavLink to="/results"><Trophy className="w-4 h-4"/> Results & Tally</NavLink></li>
                    </ul>
                </div>
                <NavLink to="/" className="btn btn-ghost text-xl font-bold tracking-tight text-gold hover:bg-white/10">
                    Enverga Arena
                </NavLink>
            </div>
            
            <div className="navbar-center hidden lg:flex">
                <ul className="menu menu-horizontal px-1 font-medium text-white/90">
                    <li><NavLink to="/" className={({isActive}) => isActive ? "text-gold bg-white/10" : "hover:text-gold"}><Home className="w-4 h-4 mr-1"/> Home</NavLink></li>
                    <li><NavLink to="/schedules" className={({isActive}) => isActive ? "text-gold bg-white/10" : "hover:text-gold"}><Calendar className="w-4 h-4 mr-1"/> Schedules</NavLink></li>
                    <li><NavLink to="/results" className={({isActive}) => isActive ? "text-gold bg-white/10" : "hover:text-gold"}><Trophy className="w-4 h-4 mr-1"/> Results</NavLink></li>
                    <li><NavLink to="/rooney" className={({isActive}) => isActive ? "text-gold bg-white/10" : "hover:text-gold"}><Bot className="w-4 h-4 mr-1"/> Rooney AI</NavLink></li>
                </ul>
            </div>
            
            <div className="navbar-end gap-2">
                {!isAuthenticated ? (
                    <NavLink to="/login" className="btn btn-sm btn-ghost text-ivory hover:bg-white/10 hover:text-gold border border-white/20">
                        <LogIn className="w-4 h-4 mr-1"/> Login
                    </NavLink>
                ) : (
                    <div className="dropdown dropdown-end">
                        <div tabIndex={0} role="button" className="btn btn-ghost btn-sm text-gold hover:bg-white/10">
                            <Users className="w-4 h-4 mr-1"/>
                            {user?.username}
                        </div>
                        <ul tabIndex={0} className="mt-3 z-[1] p-2 shadow menu menu-sm dropdown-content bg-base-100 rounded-box w-52 text-charcoal">
                            <li className="menu-title px-4 py-2 opacity-60">Role: {user?.role}</li>
                            <li><NavLink to="/admin"><LayoutDashboard className="w-4 h-4"/> Dashboard</NavLink></li>
                            <li><button onClick={logoutState} className="text-error"><LogOut className="w-4 h-4"/> Logout</button></li>
                        </ul>
                    </div>
                )}
            </div>
        </div>
    );
}
