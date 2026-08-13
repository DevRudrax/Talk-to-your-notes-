import React, { useState } from 'react';
import type { ConversationItem } from '../api';

interface SidebarProps {
  activeTab: 'chat' | 'documents' | 'collections';
  setActiveTab: (tab: 'chat' | 'documents' | 'collections') => void;
  conversations: ConversationItem[];
  activeConversationId?: string;
  onSelectConversation: (id: string) => void;
  onNewChat: () => void;
  onDeleteConversation?: (id: string) => void;
  isOpen?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewChat,
  onDeleteConversation,
  isOpen = false,
  onClose,
}) => {
  const [deleteTargetId, setDeleteTargetId] = useState<string | null>(null);

  const handleConfirmDelete = () => {
    if (deleteTargetId && onDeleteConversation) {
      onDeleteConversation(deleteTargetId);
    }
    setDeleteTargetId(null);
  };

  return (
    <>
      {/* Mobile Backdrop Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden transition-opacity"
          onClick={onClose}
        />
      )}

      {/* Navigation Sidebar Drawer */}
      <nav
        className={`fixed h-screen w-[280px] md:w-[250px] left-0 top-0 border-r border-outline-variant bg-surface flex flex-col py-6 z-50 select-none transition-transform duration-200 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        {/* Brand & New Chat */}
        <div className="px-4 pb-6 border-b border-outline-variant">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-on-primary font-bold text-sm shadow-sm">
                TN
              </div>
              <div className="text-lg font-bold text-on-surface tracking-tight">
                Talk to Your Notes
              </div>
            </div>
            {/* Mobile Close Button */}
            <button
              onClick={onClose}
              className="md:hidden p-1 rounded-lg text-on-surface-variant hover:bg-surface-container transition-colors"
              aria-label="Close menu"
            >
              <span className="material-symbols-outlined text-[20px]">close</span>
            </button>
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
                <li key={c.id} className="group relative flex items-center">
                  <button
                    onClick={() => {
                      setActiveTab('chat');
                      onSelectConversation(c.id);
                    }}
                    className={`w-full text-left text-xs truncate py-2 pl-2.5 pr-8 rounded transition-colors ${
                      activeConversationId === c.id
                        ? 'bg-surface-container-high text-on-surface font-semibold'
                        : 'text-on-surface-variant hover:bg-surface-container'
                    }`}
                    title={c.title}
                  >
                    {c.title}
                  </button>
                  {onDeleteConversation && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setDeleteTargetId(c.id);
                      }}
                      className="absolute right-1 opacity-0 group-hover:opacity-100 p-1 text-outline hover:text-error rounded transition-opacity"
                      title="Delete Conversation"
                    >
                      <span className="material-symbols-outlined text-[16px]">delete</span>
                    </button>
                  )}
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

      {/* Delete Confirmation Modal */}
      {deleteTargetId && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-surface rounded-2xl p-6 max-w-sm w-full shadow-2xl border border-outline-variant animate-in fade-in zoom-in duration-150">
            <h3 className="text-base font-bold text-on-surface mb-2">Delete this conversation?</h3>
            <p className="text-xs text-on-surface-variant mb-6">
              This action cannot be undone. All messages and source references in this chat will be permanently deleted.
            </p>
            <div className="flex items-center justify-end gap-3">
              <button
                onClick={() => setDeleteTargetId(null)}
                className="px-4 py-2 text-xs font-medium text-on-surface-variant hover:bg-surface-container rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmDelete}
                className="px-4 py-2 text-xs font-medium bg-error text-on-error hover:bg-error/90 rounded-lg transition-colors shadow-sm"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
