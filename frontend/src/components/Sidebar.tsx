import React from 'react';
import type { ConversationItem } from '../api';

interface SidebarProps {
  activeTab: 'chat' | 'documents' | 'collections';
  setActiveTab: (tab: 'chat' | 'documents' | 'collections') => void;
  conversations: ConversationItem[];
  activeConversationId?: string;
  onSelectConversation: (id: string) => void;
  onNewChat: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewChat,
}) => {
  return (
    <nav className="fixed h-screen w-[250px] left-0 top-0 border-r border-outline-variant bg-surface flex flex-col py-6 z-20 select-none">
      {/* Brand & New Chat */}
      <div className="px-4 pb-6 border-b border-outline-variant">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-on-primary font-bold text-sm shadow-sm">
            TN
          </div>
          <div className="text-lg font-bold text-on-surface tracking-tight">
            Talk to Your Notes
          </div>
        </div>
        <button
          onClick={onNewChat}
          className="w-full flex items-center justify-between bg-on-surface text-surface px-4 py-2.5 rounded-lg font-medium text-sm transition-all duration-150 ease-out hover:bg-inverse-surface active:scale-[0.98] shadow-sm"
        >
          <span>New Chat</span>
          <span className="material-symbols-outlined text-[18px]">add</span>
        </button>
      </div>

      {/* Main Navigation Links */}
      <div className="px-4 py-4 flex flex-col gap-1">
        <button
          onClick={() => setActiveTab('chat')}
          className={`flex items-center gap-3 px-4 py-2.5 rounded-xl font-medium text-sm transition-all duration-150 ease-out text-left ${
            activeTab === 'chat'
              ? 'bg-secondary-container text-on-secondary-container'
              : 'text-on-surface-variant hover:bg-surface-container'
          }`}
        >
          <span
            className="material-symbols-outlined text-[20px]"
            style={{ fontVariationSettings: activeTab === 'chat' ? "'FILL' 1" : "'FILL' 0" }}
          >
            chat_bubble
          </span>
          <span>Chat</span>
        </button>

        <button
          onClick={() => setActiveTab('documents')}
          className={`flex items-center gap-3 px-4 py-2.5 rounded-xl font-medium text-sm transition-all duration-150 ease-out text-left ${
            activeTab === 'documents'
              ? 'bg-secondary-container text-on-secondary-container'
              : 'text-on-surface-variant hover:bg-surface-container'
          }`}
        >
          <span
            className="material-symbols-outlined text-[20px]"
            style={{ fontVariationSettings: activeTab === 'documents' ? "'FILL' 1" : "'FILL' 0" }}
          >
            description
          </span>
          <span>Notes & Documents</span>
        </button>

        <button
          onClick={() => setActiveTab('collections')}
          className={`flex items-center gap-3 px-4 py-2.5 rounded-xl font-medium text-sm transition-all duration-150 ease-out text-left ${
            activeTab === 'collections'
              ? 'bg-secondary-container text-on-secondary-container'
              : 'text-on-surface-variant hover:bg-surface-container'
          }`}
        >
          <span
            className="material-symbols-outlined text-[20px]"
            style={{ fontVariationSettings: activeTab === 'collections' ? "'FILL' 1" : "'FILL' 0" }}
          >
            folder_copy
          </span>
          <span>Collections</span>
        </button>
      </div>

      {/* Recent Chats List */}
      <div className="px-4 py-2 flex-1 overflow-y-auto">
        <h3 className="text-[11px] font-semibold text-outline uppercase tracking-wider mb-2 px-2">
          Recent Chats
        </h3>
        <ul className="flex flex-col gap-[2px]">
          {conversations.length === 0 ? (
            <li className="text-xs text-outline px-2 py-1 italic">No recent chats</li>
          ) : (
            conversations.map((c) => (
              <li key={c.id}>
                <button
                  onClick={() => {
                    setActiveTab('chat');
                    onSelectConversation(c.id);
                  }}
                  className={`w-full text-left text-xs truncate py-2 px-2.5 rounded transition-colors ${
                    activeConversationId === c.id
                      ? 'bg-surface-container-high text-on-surface font-semibold'
                      : 'text-on-surface-variant hover:bg-surface-container'
                  }`}
                  title={c.title}
                >
                  {c.title}
                </button>
              </li>
            ))
          )}
        </ul>
      </div>

      {/* Footer Profile / Settings */}
      <div className="px-4 pt-4 mt-auto border-t border-outline-variant flex flex-col gap-1">
        <div className="flex items-center gap-3 px-3 py-2 text-on-surface-variant text-xs">
          <span className="material-symbols-outlined text-[20px]">account_circle</span>
          <span className="truncate font-medium">user@example.com</span>
        </div>
      </div>
    </nav>
  );
};
