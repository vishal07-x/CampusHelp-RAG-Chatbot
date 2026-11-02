import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { ConversationSidebar } from './components/ConversationSidebar';
import { ChatInterface } from './components/ChatInterface';
import { AdminDashboard } from './components/AdminDashboard';
import { AuthModal } from './components/AuthModal';
import { getConversations, getConversation, deleteConversation } from './api/client';

function CampusHelpApp() {
  const [activeTab, setActiveTab] = useState('chat'); // 'chat' or 'admin'
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState('login');

  const { isAuthenticated } = useAuth();

  // Load conversation list when authenticated
  const loadConversations = async () => {
    if (!isAuthenticated) {
      setConversations([]);
      return;
    }
    try {
      const data = await getConversations();
      setConversations(data);
    } catch (e) {
      console.error('Failed to load conversations:', e);
    }
  };

  useEffect(() => {
    loadConversations();
  }, [isAuthenticated]);

  // Load specific conversation messages
  const handleSelectConversation = async (conversationId) => {
    setActiveConversationId(conversationId);
    try {
      const data = await getConversation(conversationId);
      setMessages(data.messages || []);
    } catch (e) {
      console.error('Failed to load conversation detail:', e);
    }
  };

  const handleNewConversation = () => {
    setActiveConversationId(null);
    setMessages([]);
  };

  const handleDeleteConversation = async (conversationId) => {
    try {
      await deleteConversation(conversationId);
      if (activeConversationId === conversationId) {
        handleNewConversation();
      }
      loadConversations();
    } catch (e) {
      console.error('Failed to delete conversation:', e);
    }
  };

  const handleConversationCreated = (newConvId) => {
    setActiveConversationId(newConvId);
    loadConversations();
  };

  const handleOpenAuth = (mode = 'login') => {
    setAuthMode(mode);
    setAuthModalOpen(true);
  };

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-slate-50">
      {/* Top Navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenAuth={handleOpenAuth}
      />

      {/* Main View Area */}
      <div className="flex-1 flex overflow-hidden">
        {activeTab === 'chat' ? (
          <>
            {/* Sidebar for past chat history (desktop) */}
            <div className="hidden md:flex">
              <ConversationSidebar
                conversations={conversations}
                activeConversationId={activeConversationId}
                onSelectConversation={handleSelectConversation}
                onNewConversation={handleNewConversation}
                onDeleteConversation={handleDeleteConversation}
              />
            </div>

            {/* Central Chat Interface */}
            <ChatInterface
              conversationId={activeConversationId}
              messages={messages}
              setMessages={setMessages}
              onConversationCreated={handleConversationCreated}
              onClearChat={handleNewConversation}
            />
          </>
        ) : (
          <AdminDashboard onOpenAuth={handleOpenAuth} />
        )}
      </div>

      {/* Authentication Modal */}
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        initialMode={authMode}
      />
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <CampusHelpApp />
    </AuthProvider>
  );
}
