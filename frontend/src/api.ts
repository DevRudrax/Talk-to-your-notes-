const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8001";

export interface DocumentRecord {
  id: string;
  user_id: string;
  collection_id?: string;
  file_name: string;
  file_type: string;
  file_size: number;
  mime_type: string;
  page_count: number;
  status: 'uploaded' | 'processing' | 'extracting' | 'chunking' | 'embedding' | 'indexed' | 'failed' | 'deleted';
  processing_error?: string;
  created_at: string;
  updated_at: string;
  indexed_at?: string;
}

export interface CitationItem {
  chunk_id: string;
  document_id: string;
  file_name: string;
  page_number?: number;
  section_title?: string;
  snippet: string;
  similarity: number;
  reason: string;
}

export interface ChatResponse {
  conversation_id: string;
  user_message_id: string;
  assistant_message_id: string;
  answer: string;
  citations: CitationItem[];
  grounded: boolean;
}

export interface ConversationItem {
  id: string;
  user_id: string;
  collection_id?: string;
  title: string;
  conversation_summary?: string;
  created_at: string;
  updated_at: string;
}

export interface MessageItem {
  id: string;
  conversation_id: string;
  user_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
  citations?: CitationItem[];
}

export interface CollectionItem {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export const api = {
  // Documents
  async getDocuments(collectionId?: string): Promise<DocumentRecord[]> {
    const url = new URL(`${BACKEND_URL}/api/documents`);
    if (collectionId) url.searchParams.append("collection_id", collectionId);
    const res = await fetch(url.toString());
    if (!res.ok) throw new Error("Failed to fetch documents");
    return res.json();
  },

  async uploadDocument(file: File, collectionId?: string): Promise<DocumentRecord> {
    const formData = new FormData();
    formData.append("file", file);
    if (collectionId) formData.append("collection_id", collectionId);

    const res = await fetch(`${BACKEND_URL}/api/documents/upload`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Upload failed" }));
      throw new Error(err.detail || "Upload failed");
    }
    return res.json();
  },

  async deleteDocument(documentId: string): Promise<void> {
    const res = await fetch(`${BACKEND_URL}/api/documents/${documentId}`, {
      method: "DELETE",
    });
    if (!res.ok) throw new Error("Failed to delete document");
  },

  // Chat
  async sendChatMessage(message: string, conversationId?: string, collectionId?: string): Promise<ChatResponse> {
    const res = await fetch(`${BACKEND_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
        collection_id: collectionId,
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Chat request failed" }));
      throw new Error(err.detail || "Chat request failed");
    }
    return res.json();
  },

  // Conversations
  async getConversations(): Promise<ConversationItem[]> {
    const res = await fetch(`${BACKEND_URL}/api/conversations`);
    if (!res.ok) throw new Error("Failed to fetch conversations");
    return res.json();
  },

  async getConversationDetail(id: string): Promise<ConversationItem & { messages: MessageItem[] }> {
    const res = await fetch(`${BACKEND_URL}/api/conversations/${id}`);
    if (!res.ok) throw new Error("Failed to fetch conversation detail");
    return res.json();
  },

  async deleteConversation(id: string): Promise<void> {
    const res = await fetch(`${BACKEND_URL}/api/conversations/${id}`, {
      method: "DELETE",
    });
    if (!res.ok) throw new Error("Failed to delete conversation");
  },

  // Collections
  async getCollections(): Promise<CollectionItem[]> {
    const res = await fetch(`${BACKEND_URL}/api/collections`);
    if (!res.ok) throw new Error("Failed to fetch collections");
    return res.json();
  },

  async createCollection(name: string, description?: string): Promise<CollectionItem> {
    const res = await fetch(`${BACKEND_URL}/api/collections`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, description }),
    });
    if (!res.ok) throw new Error("Failed to create collection");
    return res.json();
  },

  async deleteCollection(id: string): Promise<void> {
    const res = await fetch(`${BACKEND_URL}/api/collections/${id}`, {
      method: "DELETE",
    });
    if (!res.ok) throw new Error("Failed to delete collection");
  }
};
