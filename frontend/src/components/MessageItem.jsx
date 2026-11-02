import React, { useState } from 'react';
import { 
  User, 
  Bot, 
  ThumbsUp, 
  ThumbsDown, 
  Sparkles, 
  Clock, 
  Layers, 
  Check, 
  Send,
  MessageSquare
} from 'lucide-react';
import { CitationCard } from './CitationCard';
import { submitFeedback } from '../api/client';

export const MessageItem = ({ message }) => {
  const isUser = message.sender === 'user';
  const [feedbackRating, setFeedbackRating] = useState(null);
  const [feedbackText, setFeedbackText] = useState('');
  const [showFeedbackInput, setShowFeedbackInput] = useState(false);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);

  const handleFeedback = async (rating) => {
    setFeedbackRating(rating);
    setShowFeedbackInput(true);
    try {
      await submitFeedback(message.id, rating, '');
    } catch (e) {
      console.error('Feedback initial rating error:', e);
    }
  };

  const handleSaveFeedbackComment = async () => {
    if (!feedbackText.trim()) {
      setShowFeedbackInput(false);
      return;
    }
    try {
      await submitFeedback(message.id, feedbackRating, feedbackText);
      setFeedbackSubmitted(true);
      setShowFeedbackInput(false);
    } catch (e) {
      console.error('Feedback comment save error:', e);
    }
  };

  return (
    <div className={`flex w-full py-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex items-start max-w-3xl space-x-3 ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
        
        {/* Avatar */}
        <div className={`w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 text-white shadow-sm ${
          isUser 
            ? 'bg-gradient-to-tr from-slate-700 to-slate-900' 
            : 'bg-gradient-to-tr from-indigo-600 to-blue-600'
        }`}>
          {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
        </div>

        {/* Bubble */}
        <div className="flex-1 min-w-0">
          <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
            isUser
              ? 'bg-indigo-600 text-white rounded-tr-none shadow-sm shadow-indigo-100 font-medium'
              : 'bg-white text-slate-800 rounded-tl-none border border-slate-200/90 shadow-sm'
          }`}>
            
            {/* Message Body */}
            <div className="whitespace-pre-wrap break-words">
              {message.content}
            </div>

            {/* Assistant Extra: Citations & Performance Latency */}
            {!isUser && (
              <div className="mt-4 pt-3 border-t border-slate-100">
                
                {/* Citations section */}
                {message.citations && message.citations.length > 0 && (
                  <div className="space-y-2 mb-3">
                    <div className="flex items-center space-x-1.5 text-xs font-semibold text-slate-600">
                      <Layers className="w-3.5 h-3.5 text-indigo-600" />
                      <span>Verified Document Citations ({message.citations.length}):</span>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {message.citations.map((c, idx) => (
                        <CitationCard key={idx} citation={c} index={idx} />
                      ))}
                    </div>
                  </div>
                )}

                {/* Footer Bar: Metrics & Feedback */}
                <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1">
                  
                  {/* Latency badge */}
                  <div className="flex items-center space-x-1.5">
                    <Clock className="w-3 h-3 text-slate-400" />
                    <span>
                      {message.latency_ms 
                        ? `Response in ${(message.latency_ms / 1000).toFixed(2)}s` 
                        : 'Real-time response'}
                    </span>
                  </div>

                  {/* Feedback buttons */}
                  <div className="flex items-center space-x-1">
                    {feedbackSubmitted ? (
                      <span className="text-[11px] text-emerald-600 font-medium flex items-center space-x-1">
                        <Check className="w-3 h-3" />
                        <span>Thanks for your feedback!</span>
                      </span>
                    ) : (
                      <>
                        <button
                          onClick={() => handleFeedback(1)}
                          title="Helpful response"
                          className={`p-1 rounded-md transition-colors ${
                            feedbackRating === 1 
                              ? 'text-emerald-600 bg-emerald-50' 
                              : 'text-slate-400 hover:text-emerald-600 hover:bg-slate-50'
                          }`}
                        >
                          <ThumbsUp className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => handleFeedback(-1)}
                          title="Unhelpful response"
                          className={`p-1 rounded-md transition-colors ${
                            feedbackRating === -1 
                              ? 'text-rose-600 bg-rose-50' 
                              : 'text-slate-400 hover:text-rose-600 hover:bg-slate-50'
                          }`}
                        >
                          <ThumbsDown className="w-3.5 h-3.5" />
                        </button>
                      </>
                    )}
                  </div>

                </div>

                {/* Optional Feedback Comment Input Drawer */}
                {showFeedbackInput && !feedbackSubmitted && (
                  <div className="mt-2.5 p-2 bg-slate-50 rounded-xl border border-slate-200 text-xs animate-in fade-in">
                    <label className="block text-[11px] font-medium text-slate-600 mb-1">
                      {feedbackRating === 1 ? 'What was helpful? (Optional)' : 'How can this answer be improved?'}
                    </label>
                    <div className="flex items-center space-x-2">
                      <input
                        type="text"
                        value={feedbackText}
                        onChange={(e) => setFeedbackText(e.target.value)}
                        placeholder="Add a brief comment..."
                        className="flex-1 bg-white border border-slate-200 rounded-lg px-2.5 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500"
                        onKeyDown={(e) => e.key === 'Enter' && handleSaveFeedbackComment()}
                      />
                      <button
                        onClick={handleSaveFeedbackComment}
                        className="px-2.5 py-1 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 text-xs"
                      >
                        Submit
                      </button>
                      <button
                        onClick={() => setShowFeedbackInput(false)}
                        className="px-2 py-1 text-slate-500 hover:text-slate-700 text-xs"
                      >
                        Skip
                      </button>
                    </div>
                  </div>
                )}

              </div>
            )}

          </div>
        </div>

      </div>
    </div>
  );
};
