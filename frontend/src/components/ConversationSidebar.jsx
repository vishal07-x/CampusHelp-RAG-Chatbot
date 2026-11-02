import React from 'react';
import { Plus, MessageSquare, Trash2, Calendar } from 'lucide-react';

export const ConversationSidebar = ({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
}) => {
  return (
    <aside className="w-64 bg-slate-50 border-r border-slate-200 flex flex-col h-full flex-shrink-0">
      {/* New Chat Button */}
      <div className="p-3 border-b border-slate-200">
        <button
          onClick={onNewConversation}
          className="w-full flex items-center justify-center space-x-2 px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow-sm shadow-indigo-100 transition-all active:scale-98"
        >
          <Plus className="w-4 h-4" />
          <span>New Consultation</span>
        </button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        <div className="px-2 py-1.5 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
          Saved Conversations
        </div>

        {conversations.length === 0 ? (
          <div className="text-center py-8 px-4 text-xs text-slate-400">
            <MessageSquare className="w-8 h-8 mx-auto text-slate-300 mb-2 stroke-1" />
            <p>No past conversations yet.</p>
          </div>
        ) : (
          conversations.map((c) => {
            const isActive = c.id === activeConversationId;
            return (
              <div
                key={c.id}
                onClick={() => onSelectConversation(c.id)}
                className={`group flex items-center justify-between px-3 py-2 rounded-xl text-xs cursor-pointer transition-all ${
                  isActive
                    ? 'bg-indigo-50 text-indigo-900 font-semibold border border-indigo-200/60'
                    : 'text-slate-600 hover:bg-slate-100/80 hover:text-slate-900'
                }`}
              >
                <div className="flex items-center space-x-2 truncate pr-2">
                  <MessageSquare className={`w-3.5 h-3.5 flex-shrink-0 ${isActive ? 'text-indigo-600' : 'text-slate-400'}`} />
                  <span className="truncate">{c.title || 'Untitled Conversation'}</span>
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteConversation(c.id);
                  }}
                  title="Delete conversation"
                  className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-rose-600 rounded transition-opacity"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            );
          })
        )}
      </div>

      {/* Footer Info */}
      <div className="p-3 border-t border-slate-200 text-[11px] text-slate-400 text-center">
        CampusHelp RAG v1.0
      </div>
    </aside>
  );
};
