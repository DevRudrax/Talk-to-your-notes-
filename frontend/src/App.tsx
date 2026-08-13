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
  };

  const handleConversationCreated = async (id: string) => {
    setActiveConversationId(id);
    const convs = await api.getConversations().catch(() => []);
    setConversations(convs);
  };

  const handleSelectCollectionForChat = (colId: string) => {
    setSelectedCollectionId(colId);
    setActiveConversationId(undefined);
    setActiveTab('chat');
  };

  return (
    <div className="flex h-screen w-full bg-surface text-on-surface font-body overflow-hidden">
      {/* Navigation Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={(id) => setActiveConversationId(id)}
        onNewChat={handleNewChat}
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
        />
      )}

      {activeTab === 'documents' && (
        <DocumentManagement collections={collections} />
      )}

      {activeTab === 'collections' && (
        <CollectionsOverview
          collections={collections}
          documents={documents}
          onRefreshCollections={loadData}
          onSelectCollectionForChat={handleSelectCollectionForChat}
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
