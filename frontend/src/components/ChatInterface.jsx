import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Trash2, 
  Sparkles, 
  GraduationCap, 
  HelpCircle, 
  FileText, 
  Building2, 
  BookOpen, 
  Award,
  AlertCircle
} from 'lucide-react';
import { MessageItem } from './MessageItem';
import { DepartmentFilter } from './DepartmentFilter';
import { sendChatMessage } from '../api/client';

const SUGGESTED_QUESTIONS = [
  {
    topic: "Attendance",
    question: "What is the minimum attendance requirement for semester examinations?",
    icon: BookOpen,
  },
  {
    topic: "Tuition Fees",
    question: "When is the last date to pay tuition fees for the Fall semester without penalty?",
    icon: Building2,
  },
  {
    topic: "Placement Policy",
    question: "What is the minimum CGPA and backlog criterion to participate in campus placements?",
    icon: Award,
  },
  {
    topic: "Hostel & Facilities",
    question: "What is the residential hostel curfew timing and medical emergency procedure?",
    icon: FileText,
  },
];

export const ChatInterface = ({
  conversationId,
  messages,
  setMessages,
  onConversationCreated,
  onClearChat,
}) => {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [departmentFilter, setDepartmentFilter] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (queryText = null) => {
    const textToSend = queryText || input;
    if (!textToSend.trim() || loading) return;

    setError(null);
    const tempUserMessage = {
      id: `temp_${Date.now()}`,
      sender: 'user',
      content: textToSend.trim(),
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, tempUserMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await sendChatMessage({
        message: textToSend.trim(),
        conversation_id: conversationId,
        department_filter: departmentFilter,
      });

      const assistantMessage = {
        id: response.message_id,
        conversation_id: response.conversation_id,
        sender: 'assistant',
        content: response.answer,
        citations: response.citations,
        latency_ms: response.total_latency_ms,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);

      if (!conversationId && response.conversation_id && onConversationCreated) {
        onConversationCreated(response.conversation_id);
      }
    } catch (err) {
      console.error('Chat error:', err);
      const detail = err.response?.data?.detail || 'Unable to connect to the knowledge engine. Please ensure the backend is running.';
      setError(detail);
      setMessages((prev) => [
        ...prev,
        {
          id: `err_${Date.now()}`,
          sender: 'assistant',
          content: `⚠️ Error: ${detail}`,
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col flex-1 h-full bg-slate-50/50">
      {/* Top Filter Bar */}
      <div className="bg-white border-b border-slate-200 px-4 py-1.5 shadow-xs">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <DepartmentFilter
            selectedFilter={departmentFilter}
            onSelectFilter={setDepartmentFilter}
          />
          {messages.length > 0 && (
            <button
              onClick={onClearChat}
              title="Clear conversation"
              className="flex items-center space-x-1 text-xs text-slate-500 hover:text-rose-600 px-2.5 py-1.5 rounded-lg hover:bg-rose-50 transition-colors ml-2 flex-shrink-0"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Clear</span>
            </button>
          )}
        </div>
      </div>

      {/* Messages Thread */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-3xl mx-auto space-y-2">
          {messages.length === 0 ? (
            /* Welcome Hero & Suggested Questions */
            <div className="text-center py-8 px-4">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-500 to-blue-600 text-white flex items-center justify-center mx-auto mb-4 shadow-lg shadow-indigo-100">
                <GraduationCap className="w-8 h-8" />
              </div>
              <h2 className="text-2xl font-bold text-slate-800 tracking-tight mb-2">
                Welcome to CampusHelp
              </h2>
              <p className="text-sm text-slate-500 max-w-lg mx-auto mb-8">
                Your AI-powered college advisor. Ask questions about academic policies, tuition fees, examination schedules, placement rules, and hostel guidelines.
              </p>

              {/* Suggestions Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-left max-w-2xl mx-auto">
                {SUGGESTED_QUESTIONS.map((item, idx) => {
                  const Icon = item.icon;
                  return (
                    <div
                      key={idx}
                      onClick={() => handleSend(item.question)}
                      className="p-3.5 bg-white hover:bg-indigo-50/60 border border-slate-200 hover:border-indigo-300 rounded-xl cursor-pointer transition-all duration-200 shadow-xs hover:shadow-sm group"
                    >
                      <div className="flex items-center space-x-2 text-indigo-600 font-semibold text-xs mb-1">
                        <Icon className="w-3.5 h-3.5" />
                        <span>{item.topic}</span>
                      </div>
                      <p className="text-xs text-slate-700 group-hover:text-slate-900 leading-snug">
                        "{item.question}"
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            messages.map((msg) => <MessageItem key={msg.id} message={msg} />)
          )}

          {/* Typing Indicator */}
          {loading && (
            <div className="flex items-start space-x-3 py-4">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-blue-600 flex items-center justify-center text-white shadow-sm flex-shrink-0 animate-pulse">
                <Sparkles className="w-4 h-4" />
              </div>
              <div className="bg-white px-4 py-3 rounded-2xl rounded-tl-none border border-slate-200 text-xs text-slate-500 flex items-center space-x-2 shadow-xs">
                <span className="w-2 h-2 rounded-full bg-indigo-500 animate-bounce"></span>
                <span className="w-2 h-2 rounded-full bg-indigo-500 animate-bounce [animation-delay:0.2s]"></span>
                <span className="w-2 h-2 rounded-full bg-indigo-500 animate-bounce [animation-delay:0.4s]"></span>
                <span className="text-xs font-medium text-slate-600 ml-1">
                  Searching institutional documents & verifying citations...
                </span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Form Bar */}
      <div className="bg-white border-t border-slate-200 p-4">
        <div className="max-w-3xl mx-auto">
          {error && (
            <div className="mb-2 p-2 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-700 flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="relative flex items-center bg-slate-50 border border-slate-300 focus-within:border-indigo-500 focus-within:ring-2 focus-within:ring-indigo-100 rounded-2xl transition-all shadow-inner">
            <textarea
              ref={inputRef}
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask anything about fees, exams, attendance, placements..."
              className="w-full bg-transparent px-4 py-3.5 text-sm text-slate-800 placeholder-slate-400 focus:outline-none resize-none max-h-32"
            />
            <button
              onClick={() => handleSend()}
              disabled={!input.trim() || loading}
              className={`p-2.5 mr-2 rounded-xl text-white transition-all ${
                input.trim() && !loading
                  ? 'bg-indigo-600 hover:bg-indigo-700 shadow-md shadow-indigo-200 scale-100'
                  : 'bg-slate-300 cursor-not-allowed scale-95'
              }`}
            >
              <Send className="w-4 h-4" />
            </button>
          </div>

          <div className="flex items-center justify-between text-[11px] text-slate-400 px-2 mt-2">
            <span>Press Enter to send • Shift+Enter for new line</span>
            <span>All answers verified with document page citations</span>
          </div>
        </div>
      </div>
    </div>
  );
};
