import { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { ChatWorkspace } from './components/ChatWorkspace';
import { DocumentManagement } from './components/DocumentManagement';
import { CollectionsOverview } from './components/CollectionsOverview';
import { SourceViewer } from './components/SourceViewer';
import { api } from './api';
import type { ConversationItem, DocumentRecord, CollectionItem, CitationItem } from './api';

export function App() {
  const [activeTab, setActiveTab] = useState<'chat' | 'documents' | 'collections'>('chat');
  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | undefined>(undefined);
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [collections, setCollections] = useState<CollectionItem[]>([]);
  const [selectedCollectionId, setSelectedCollectionId] = useState<string | undefined>(undefined);
  const [activeCitation, setActiveCitation] = useState<CitationItem | null>(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [convs, docs, cols] = await Promise.all([
        api.getConversations().catch(() => []),
        api.getDocuments().catch(() => []),
        api.getCollections().catch(() => []),
      ]);
      setConversations(convs);
      setDocuments(docs);
      setCollections(cols);
      if (convs.length > 0 && !activeConversationId) {
        setActiveConversationId(convs[0].id);
      }
    } catch (e) {
      console.error("Failed to load initial data", e);
    }
  };

  const handleNewChat = () => {
    setActiveConversationId(undefined);
    setActiveTab('chat');
    setIsMobileMenuOpen(false);
  };

  const handleConversationCreated = async (id: string) => {
    setActiveConversationId(id);
    const convs = await api.getConversations().catch(() => []);
    setConversations(convs);
  };

  const handleDeleteConversation = async (id: string) => {
    try {
      await api.deleteConversation(id);
      if (activeConversationId === id) {
        setActiveConversationId(undefined);
      }
      const convs = await api.getConversations().catch(() => []);
      setConversations(convs);
    } catch (e) {
      console.error("Failed to delete conversation", e);
    }
  };

  const handleSelectCollectionForChat = (colId: string) => {
    setSelectedCollectionId(colId);
    setActiveConversationId(undefined);
    setActiveTab('chat');
    setIsMobileMenuOpen(false);
  };

  return (
    <div className="flex h-screen w-full bg-surface text-on-surface font-body overflow-hidden">
      {/* Navigation Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={(tab) => {
          setActiveTab(tab);
          setIsMobileMenuOpen(false);
        }}
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={(id) => {
          setActiveConversationId(id);
          setIsMobileMenuOpen(false);
        }}
        onNewChat={handleNewChat}
        onDeleteConversation={handleDeleteConversation}
        isOpen={isMobileMenuOpen}
        onClose={() => setIsMobileMenuOpen(false)}
      />

      {/* Main Content Workspace View */}
      {activeTab === 'chat' && (
        <ChatWorkspace
          conversationId={activeConversationId}
          onConversationCreated={handleConversationCreated}
          collections={collections}
          selectedCollectionId={selectedCollectionId}
          onSelectCollection={(id) => setSelectedCollectionId(id)}
          onOpenCitation={(cit) => setActiveCitation(cit)}
          onToggleMobileMenu={() => setIsMobileMenuOpen((prev) => !prev)}
        />
      )}

      {activeTab === 'documents' && (
        <DocumentManagement
          collections={collections}
          onToggleMobileMenu={() => setIsMobileMenuOpen((prev) => !prev)}
        />
      )}

      {activeTab === 'collections' && (
        <CollectionsOverview
          collections={collections}
          documents={documents}
          onRefreshCollections={loadData}
          onSelectCollectionForChat={handleSelectCollectionForChat}
          onToggleMobileMenu={() => setIsMobileMenuOpen((prev) => !prev)}
        />
      )}

      {/* Citation Inspector Side Drawer */}
      <SourceViewer
        citation={activeCitation}
        onClose={() => setActiveCitation(null)}
      />
    </div>
  );
}

export default App;
