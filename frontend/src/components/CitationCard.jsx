import React, { useState } from 'react';
import { FileText, ChevronDown, ChevronUp, ExternalLink, Bookmark } from 'lucide-react';

export const CitationCard = ({ citation, index }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!citation) return null;

  return (
    <div className="bg-slate-50 hover:bg-slate-100/80 border border-slate-200/90 rounded-xl transition-all duration-200 overflow-hidden text-left">
      <div 
        onClick={() => setIsExpanded(!isExpanded)}
        className="p-2.5 flex items-center justify-between cursor-pointer select-none"
      >
        <div className="flex items-center space-x-2.5 min-w-0 pr-2">
          <div className="w-6 h-6 rounded-md bg-indigo-100 text-indigo-700 flex items-center justify-center flex-shrink-0 text-xs font-bold">
            [{index + 1}]
          </div>
          <div className="min-w-0">
            <div className="text-xs font-semibold text-slate-800 truncate flex items-center space-x-1.5">
              <span className="truncate">{citation.document_name}</span>
            </div>
            <div className="text-[11px] text-slate-500 flex items-center space-x-2 mt-0.5">
              <span className="bg-indigo-50 text-indigo-700 font-semibold px-1.5 py-0.2 rounded text-[10px] border border-indigo-200/60">
                Page {citation.page_number}
              </span>
              <span>•</span>
              <span className="capitalize">{citation.department || 'General'}</span>
              <span>•</span>
              <span className="text-emerald-600 font-medium">
                Score: {Math.round((citation.relevance_score || 0) * 100)}%
              </span>
            </div>
          </div>
        </div>

        <button 
          aria-label={isExpanded ? "Collapse reference" : "Expand reference"}
          className="p-1 text-slate-400 hover:text-slate-600 rounded-md"
        >
          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
      </div>

      {isExpanded && (
        <div className="px-3 pb-3 pt-1 border-t border-slate-200/60 bg-white/70">
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1 flex items-center space-x-1">
            <Bookmark className="w-3 h-3 text-indigo-500" />
            <span>Retrieved Evidence Excerpt:</span>
          </div>
          <p className="text-xs text-slate-700 leading-relaxed bg-slate-50 p-2.5 rounded-lg border border-slate-200/50 italic">
            "{citation.excerpt || 'No preview excerpt available.'}"
          </p>
        </div>
      )}
    </div>
  );
};
