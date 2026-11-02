import React from 'react';
import { 
  Compass, 
  BookOpen, 
  CreditCard, 
  FileCheck, 
  Briefcase, 
  Building 
} from 'lucide-react';

const FILTERS = [
  { id: 'all', label: 'All Topics', icon: Compass },
  { id: 'Academics', label: 'Academics & Attendance', icon: BookOpen },
  { id: 'Finance', label: 'Fees & Scholarships', icon: CreditCard },
  { id: 'Examinations', label: 'Exams & Grading', icon: FileCheck },
  { id: 'Placements', label: 'Placements & Career', icon: Briefcase },
  { id: 'Facilities', label: 'Campus & Hostel', icon: Building },
];

export const DepartmentFilter = ({ selectedFilter, onSelectFilter }) => {
  return (
    <div className="w-full overflow-x-auto py-2 no-scrollbar">
      <div className="flex items-center space-x-2 min-w-max px-1">
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider mr-1">
          Filter:
        </span>
        {FILTERS.map((f) => {
          const Icon = f.icon;
          const isActive = (selectedFilter || 'all').toLowerCase() === f.id.toLowerCase();
          return (
            <button
              key={f.id}
              onClick={() => onSelectFilter(f.id === 'all' ? null : f.id)}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-200'
                  : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200/80'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{f.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
