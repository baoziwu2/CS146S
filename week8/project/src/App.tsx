import { useState } from 'react';
import { Terminal, FileText, CheckSquare, Activity } from 'lucide-react';
import NotesSection from './components/notes/NotesSection';
import ActionItemsSection from './components/actionItems/ActionItemsSection';

type Tab = 'notes' | 'actions';

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>('notes');

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between h-14">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <Terminal size={16} className="text-white" />
              </div>
              <div>
                <span className="text-sm font-bold text-gray-900 tracking-tight">
                  Developer Control Center
                </span>
                <div className="flex items-center gap-1 -mt-0.5">
                  <Activity size={8} className="text-emerald-500" />
                  <span className="text-[10px] text-emerald-600 font-medium">Live</span>
                </div>
              </div>
            </div>

            <nav className="flex items-center gap-1 bg-gray-100 p-1 rounded-xl">
              <TabButton
                active={activeTab === 'notes'}
                onClick={() => setActiveTab('notes')}
                icon={<FileText size={13} />}
                label="Notes"
              />
              <TabButton
                active={activeTab === 'actions'}
                onClick={() => setActiveTab('actions')}
                icon={<CheckSquare size={13} />}
                label="Action Items"
              />
            </nav>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
        <div className="mb-6">
          <h1 className="text-xl font-bold text-gray-900">
            {activeTab === 'notes' ? 'Notes' : 'Action Items'}
          </h1>
          <p className="text-sm text-gray-500 mt-0.5">
            {activeTab === 'notes'
              ? 'Organize your thoughts, ideas, and documentation.'
              : 'Track tasks and action items to completion.'}
          </p>
        </div>

        <div
          key={activeTab}
          className="animate-fade-in"
        >
          {activeTab === 'notes' ? <NotesSection /> : <ActionItemsSection />}
        </div>
      </main>
    </div>
  );
}

function TabButton({
  active,
  onClick,
  icon,
  label,
}: {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-medium rounded-lg transition-all duration-150 ${
        active
          ? 'bg-white text-gray-900 shadow-sm'
          : 'text-gray-500 hover:text-gray-700'
      }`}
    >
      {icon}
      {label}
    </button>
  );
}
