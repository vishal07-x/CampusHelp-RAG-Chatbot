import React, { useState, useEffect } from 'react';
import { 
  GraduationCap, 
  Shield, 
  MessageSquare, 
  LogIn, 
  LogOut, 
  User, 
  CheckCircle2, 
  AlertCircle 
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { checkSystemReady } from '../api/client';

export const Navbar = ({ activeTab, setActiveTab, onOpenAuth }) => {
  const { user, isAuthenticated, isAdmin, logout } = useAuth();
  const [systemReady, setSystemReady] = useState(true);

  useEffect(() => {
    const probe = async () => {
      try {
        const res = await checkSystemReady();
        setSystemReady(res.ready);
      } catch (e) {
        setSystemReady(false);
      }
    };
    probe();
    const interval = setInterval(probe, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="sticky top-0 z-30 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-sm transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-blue-500 flex items-center justify-center shadow-md shadow-indigo-100 text-white">
            <GraduationCap className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-indigo-900 to-indigo-600 bg-clip-text text-transparent">
                CampusHelp
              </span>
              <span className="px-2 py-0.5 text-[10px] font-semibold bg-indigo-50 text-indigo-700 rounded-full border border-indigo-200">
                RAG 2.0
              </span>
            </div>
            <p className="text-xs text-slate-500 hidden sm:block">AI-Powered Institutional Knowledge Assistant</p>
          </div>
        </div>

        {/* Center Nav Tabs */}
        <div className="flex items-center bg-slate-100 p-1 rounded-xl text-sm font-medium">
          <button
            onClick={() => setActiveTab('chat')}
            className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg transition-all ${
              activeTab === 'chat'
                ? 'bg-white text-indigo-600 shadow-sm font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <MessageSquare className="w-4 h-4" />
            <span>Assistant</span>
          </button>
          
          <button
            onClick={() => {
              if (!isAuthenticated) {
                onOpenAuth('login');
              } else {
                setActiveTab('admin');
              }
            }}
            className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg transition-all ${
              activeTab === 'admin'
                ? 'bg-white text-indigo-600 shadow-sm font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Shield className="w-4 h-4" />
            <span>Admin Portal</span>
            {isAdmin && (
              <span className="w-2 h-2 rounded-full bg-indigo-600 inline-block"></span>
            )}
          </button>
        </div>

        {/* Right Action: Status & Auth */}
        <div className="flex items-center space-x-3">
          {/* Health indicator */}
          <div 
            title={systemReady ? "RAG & Database Connected" : "Connecting to Services..."}
            className="hidden md:flex items-center space-x-1.5 px-2.5 py-1 bg-slate-50 rounded-full border border-slate-200 text-xs font-medium text-slate-600"
          >
            <span className={`w-2 h-2 rounded-full ${systemReady ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`}></span>
            <span>{systemReady ? 'Online' : 'Reconnecting'}</span>
          </div>

          {isAuthenticated ? (
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2 pl-2">
                <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-xs uppercase border border-indigo-200">
                  {user?.full_name ? user.full_name.charAt(0) : user?.email?.charAt(0) || 'U'}
                </div>
                <div className="hidden lg:block text-left">
                  <div className="text-xs font-semibold text-slate-800 leading-tight">
                    {user?.full_name || user?.email?.split('@')[0]}
                  </div>
                  <div className="text-[10px] text-indigo-600 font-medium uppercase tracking-wider">
                    {user?.role}
                  </div>
                </div>
              </div>
              <button
                onClick={logout}
                title="Sign Out"
                className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <button
              onClick={() => onOpenAuth('login')}
              className="flex items-center space-x-1.5 px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-semibold shadow-sm shadow-indigo-200 transition-all active:scale-95"
            >
              <LogIn className="w-4 h-4" />
              <span>Sign In</span>
            </button>
          )}

        </div>

      </div>
    </header>
  );
};
