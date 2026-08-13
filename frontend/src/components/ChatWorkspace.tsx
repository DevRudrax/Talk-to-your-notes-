import React, { useState, useEffect, useRef } from 'react';
import { api } from '../api';
import type { MessageItem, CitationItem, CollectionItem } from '../api';

interface ChatWorkspaceProps {
  conversationId?: string;
  onConversationCreated: (id: string) => void;
  collections: CollectionItem[];
  selectedCollectionId?: string;
  onSelectCollection: (id?: string) => void;
  onOpenCitation: (citation: CitationItem) => void;
}

export const ChatWorkspace: React.FC<ChatWorkspaceProps> = ({
  conversationId,
  onConversationCreated,
  collections,
  selectedCollectionId,
  onSelectCollection,
  onOpenCitation,
}) => {
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationTitle, setConversationTitle] = useState('New Thread');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (conversationId) {
      loadConversation(conversationId);
    } else {
      setMessages([]);
      setConversationTitle('New Thread');
    }
  }, [conversationId]);

  const loadConversation = async (id: string) => {
    try {
      const data = await api.getConversationDetail(id);
      setConversationTitle(data.title);
      setMessages(data.messages || []);
    } catch (e) {
      console.error("Failed to load conversation", e);
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = async (textToSend?: string) => {
    const text = (textToSend || inputMessage).trim();
    if (!text || isLoading) return;

    setInputMessage('');
    setIsLoading(true);

    const tempUserMsg: MessageItem = {
      id: `temp-${Date.now()}`,
      conversation_id: conversationId || '',
      user_id: 'user',
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const res = await api.sendChatMessage(text, conversationId, selectedCollectionId);
      if (!conversationId) {
        onConversationCreated(res.conversation_id);
      }

      const assistantMsg: MessageItem = {
        id: res.assistant_message_id,
        conversation_id: res.conversation_id,
        user_id: 'assistant',
        role: 'assistant',
        content: res.answer,
        created_at: new Date().toISOString(),
        citations: res.citations,
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (e: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          conversation_id: conversationId || '',
          user_id: 'assistant',
          role: 'assistant',
          content: `⚠️ Error: ${e.message || "Failed to process request."}`,
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-screen ml-[250px] bg-surface relative overflow-hidden">
      {/* Top Header */}
      <header className="h-16 border-b border-outline-variant bg-surface flex justify-between items-center px-6 z-10">
        <div className="flex items-center gap-4">
          <h2 className="text-base font-bold text-on-surface truncate">
            {conversationTitle}
          </h2>
          {selectedCollectionId && (
            <span className="px-2.5 py-0.5 bg-primary-container text-on-primary-container text-xs rounded-full font-medium flex items-center gap-1">
              <span className="material-symbols-outlined text-[14px]">folder</span>
              {collections.find((c) => c.id === selectedCollectionId)?.name || 'Collection'}
            </span>
          )}
        </div>

        {/* Collection Selector Filter */}
        <div className="flex items-center gap-2">
          <label className="text-xs text-outline font-medium">Filter Scope:</label>
          <select
            value={selectedCollectionId || ''}
            onChange={(e) => onSelectCollection(e.target.value || undefined)}
            className="text-xs bg-surface-container-lowest border border-outline-variant rounded-lg px-2.5 py-1.5 text-on-surface focus:outline-none focus:border-primary"
          >
            <option value="">All Indexed Documents</option>
            {collections.map((col) => (
              <option key={col.id} value={col.id}>
                📁 {col.name}
              </option>
            ))}
          </select>
        </div>
      </header>

      {/* Scrollable Message History Area */}
      <div className="flex-1 overflow-y-auto px-6 py-8 flex flex-col gap-6 max-w-3xl w-full mx-auto pb-44">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center my-auto py-16 text-center space-y-4">
            <div className="w-12 h-12 rounded-full bg-primary-container text-on-primary-container flex items-center justify-center">
              <span className="material-symbols-outlined text-[28px]">psychology</span>
            </div>
            <div>
              <h3 className="text-lg font-bold text-on-surface">Talk to Your Notes</h3>
              <p className="text-sm text-outline max-w-sm mt-1">
                Ask questions about your uploaded PDFs, Markdown, and TXT notes. All responses are strictly grounded in your private knowledge base.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-md pt-4">
              {[
                'Explain 3NF in database normalization',
                'What are the key ACID properties?',
                'Summarize the core concepts in my uploaded notes',
                'What is the difference between 2NF and 3NF?',
              ].map((starter, i) => (
                <button
                  key={i}
                  onClick={() => handleSend(starter)}
                  className="text-left text-xs bg-surface-container-lowest border border-outline-variant p-3 rounded-xl hover:border-primary transition-colors text-on-surface"
                >
                  "{starter}"
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-3 w-full ${
                msg.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded bg-primary-container text-on-primary-container flex items-center justify-center flex-shrink-0 mt-1 shadow-xs">
                  <span className="material-symbols-outlined text-[18px]">temp_preferences_custom</span>
                </div>
              )}

              <div
                className={`max-w-[85%] ${
                  msg.role === 'user'
                    ? 'bg-surface-container-highest px-5 py-3.5 rounded-2xl rounded-tr-xs border border-outline-variant text-on-surface text-sm'
                    : 'flex-1 max-w-prose space-y-4'
                }`}
              >
                {msg.role === 'user' ? (
                  <p>{msg.content}</p>
                ) : (
                  <div className="space-y-4">
                    <div className="prose prose-sm max-w-none text-on-surface text-sm leading-relaxed whitespace-pre-wrap">
                      {msg.content}
                    </div>

                    {/* Sources section if citations exist */}
                    {msg.citations && msg.citations.length > 0 && (
                      <div className="pt-3 border-t border-outline-variant/60">
                        <div className="flex items-center gap-1.5 mb-2 text-xs font-semibold text-on-surface-variant">
                          <span className="material-symbols-outlined text-[16px]">library_books</span>
                          <span>Verified Sources ({msg.citations.length})</span>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {msg.citations.map((cit, idx) => (
                            <button
                              key={idx}
                              onClick={() => onOpenCitation(cit)}
                              className="flex items-center gap-1.5 px-3 py-1.5 bg-surface-container border border-outline-variant rounded hover:bg-surface-container-high transition-colors text-xs font-medium text-on-surface"
                            >
                              <span className="material-symbols-outlined text-[14px] text-primary">
                                {cit.file_name.endsWith('.pdf') ? 'picture_as_pdf' : 'description'}
                              </span>
                              <span>{cit.file_name}</span>
                              {cit.page_number && (
                                <span className="text-[10px] text-outline">(p. {cit.page_number})</span>
                              )}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex gap-3 w-full items-center text-outline text-xs italic">
            <div className="w-8 h-8 rounded bg-primary-container text-on-primary-container flex items-center justify-center animate-pulse">
              <span className="material-symbols-outlined text-[18px]">psychology</span>
            </div>
            <span>Retrieving notes and packing context...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Fixed Bottom Input Bar */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-surface via-surface to-transparent pt-6 pb-6 px-6 w-full max-w-3xl mx-auto z-10">
        <div className="relative bg-surface-container-lowest border border-outline-variant rounded-xl shadow-[0_4px_12px_rgba(0,0,0,0.05)] focus-within:border-primary focus-within:ring-1 focus-within:ring-primary transition-all flex flex-col">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Ask a question about your notes..."
            rows={2}
            className="w-full bg-transparent border-none resize-none px-4 py-3 text-sm text-on-surface placeholder:text-outline focus:outline-none"
          />
          <div className="flex justify-between items-center px-3 pb-3 pt-1 border-t border-outline-variant/30">
            <div className="flex items-center gap-2 text-xs text-outline">
              <span className="material-symbols-outlined text-[16px]">info</span>
              <span>Grounded in your private notes</span>
            </div>

            <button
              onClick={() => handleSend()}
              disabled={!inputMessage.trim() || isLoading}
              className="p-2 bg-on-surface text-surface rounded-lg hover:bg-inverse-surface disabled:opacity-40 transition-colors flex items-center justify-center"
            >
              <span className="material-symbols-outlined text-[18px]">arrow_upward</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
