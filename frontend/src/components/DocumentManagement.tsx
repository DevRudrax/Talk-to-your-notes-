import React, { useState, useEffect } from 'react';
import { api } from '../api';
import type { DocumentRecord, CollectionItem } from '../api';

interface DocumentManagementProps {
  collections: CollectionItem[];
}

export const DocumentManagement: React.FC<DocumentManagementProps> = ({ collections }) => {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [selectedCollection, setSelectedCollection] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const docs = await api.getDocuments();
      setDocuments(docs);
    } catch (e) {
      console.error("Failed to load documents", e);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const file = files[0];

    setErrorMsg(null);
    setUploading(true);

    try {
      await api.uploadDocument(file, selectedCollection || undefined);
      await fetchDocuments();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to upload file");
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this document and its vector index?")) return;
    try {
      await api.deleteDocument(id);
      setDocuments((prev) => prev.filter((d) => d.id !== id));
    } catch (e) {
      console.error("Failed to delete document", e);
    }
  };

  const filteredDocs = documents.filter((doc) =>
    doc.file_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="flex-1 flex flex-col h-screen ml-[250px] bg-surface overflow-y-auto">
      {/* Top Header */}
      <header className="h-16 border-b border-outline-variant bg-surface flex justify-between items-center px-8 z-10 sticky top-0">
        <div>
          <h2 className="text-base font-bold text-on-surface">Notes & Document Management</h2>
          <p className="text-xs text-outline">Manage your indexed PDF, Markdown, and TXT files</p>
        </div>

        <button
          onClick={fetchDocuments}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-surface-container border border-outline-variant rounded-lg text-xs font-medium text-on-surface hover:bg-surface-container-high transition-colors"
        >
          <span className="material-symbols-outlined text-[16px]">refresh</span>
          <span>Refresh</span>
        </button>
      </header>

      <div className="p-8 max-w-5xl w-full mx-auto space-y-8">
        {/* File Upload Dropzone */}
        <div className="bg-surface-container-lowest border-2 border-dashed border-outline-variant hover:border-primary rounded-2xl p-8 text-center transition-all">
          <div className="w-12 h-12 rounded-full bg-primary-container text-on-primary-container flex items-center justify-center mx-auto mb-3 shadow-xs">
            <span className="material-symbols-outlined text-[24px]">cloud_upload</span>
          </div>
          <h3 className="text-base font-semibold text-on-surface">Upload Documents to Knowledge Base</h3>
          <p className="text-xs text-outline max-w-md mx-auto mt-1 mb-4">
            Supports PDF, Markdown (.md), and plain text (.txt) files up to 25 MB. Text is automatically extracted, semantically chunked, and embedded into pgvector.
          </p>

          {/* Optional Collection Assignment */}
          <div className="max-w-xs mx-auto mb-4 flex items-center gap-2">
            <span className="text-xs text-outline font-medium">Assign Collection:</span>
            <select
              value={selectedCollection}
              onChange={(e) => setSelectedCollection(e.target.value)}
              className="text-xs bg-surface border border-outline-variant rounded-md px-2 py-1 text-on-surface flex-1"
            >
              <option value="">None (Uncategorized)</option>
              {collections.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          <label className="inline-flex items-center gap-2 bg-primary text-on-primary px-5 py-2.5 rounded-lg text-sm font-medium cursor-pointer hover:bg-primary-container transition-colors shadow-xs">
            <span>Select File to Upload</span>
            <input
              type="file"
              accept=".pdf,.md,.markdown,.txt"
              onChange={(e) => handleFileUpload(e.target.files)}
              disabled={uploading}
              className="hidden"
            />
          </label>

          {uploading && (
            <div className="mt-4 flex items-center justify-center gap-2 text-xs text-primary font-medium">
              <span className="material-symbols-outlined text-[18px] animate-spin">progress_activity</span>
              <span>Processing, extracting & indexing document...</span>
            </div>
          )}

          {errorMsg && (
            <div className="mt-4 p-3 bg-error-container text-on-error-container text-xs rounded-lg max-w-md mx-auto">
              ⚠️ {errorMsg}
            </div>
          )}
        </div>

        {/* Document List */}
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-sm font-bold text-on-surface uppercase tracking-wider">
              Indexed Documents ({filteredDocs.length})
            </h3>

            {/* Search input */}
            <div className="relative w-64">
              <span className="material-symbols-outlined absolute left-3 top-2.5 text-[18px] text-outline">
                search
              </span>
              <input
                type="text"
                placeholder="Filter documents..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg pl-9 pr-3 py-1.5 text-xs text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          {loading ? (
            <div className="text-center py-12 text-outline text-xs italic">Loading documents...</div>
          ) : filteredDocs.length === 0 ? (
            <div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-8 text-center text-outline text-xs">
              No documents found. Upload your first note or PDF above!
            </div>
          ) : (
            <div className="bg-surface-container-lowest border border-outline-variant rounded-xl overflow-hidden shadow-xs">
              <table className="w-full text-left text-xs">
                <thead className="bg-surface-container-low border-b border-outline-variant text-on-surface font-semibold">
                  <tr>
                    <th className="px-4 py-3">File Name</th>
                    <th className="px-4 py-3">Format</th>
                    <th className="px-4 py-3">Size</th>
                    <th className="px-4 py-3">Pages</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3">Date Added</th>
                    <th className="px-4 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline-variant">
                  {filteredDocs.map((doc) => (
                    <tr key={doc.id} className="hover:bg-surface-container/40 transition-colors">
                      <td className="px-4 py-3 font-medium text-on-surface flex items-center gap-2">
                        <span className="material-symbols-outlined text-[18px] text-primary">
                          {doc.file_type === 'pdf' ? 'picture_as_pdf' : 'description'}
                        </span>
                        <span className="truncate max-w-xs" title={doc.file_name}>
                          {doc.file_name}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-outline uppercase">{doc.file_type}</td>
                      <td className="px-4 py-3 text-outline">
                        {(doc.file_size / 1024).toFixed(1)} KB
                      </td>
                      <td className="px-4 py-3 text-outline">{doc.page_count}</td>
                      <td className="px-4 py-3">
                        <span
                          className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-medium ${
                            doc.status === 'indexed'
                              ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200'
                              : doc.status === 'failed'
                              ? 'bg-error-container text-on-error-container'
                              : 'bg-primary-container text-on-primary-container'
                          }`}
                        >
                          <span className="material-symbols-outlined text-[14px]">
                            {doc.status === 'indexed'
                              ? 'check_circle'
                              : doc.status === 'failed'
                              ? 'error'
                              : 'sync'}
                          </span>
                          <span className="capitalize">{doc.status}</span>
                        </span>
                      </td>
                      <td className="px-4 py-3 text-outline">
                        {new Date(doc.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <button
                          onClick={() => handleDelete(doc.id)}
                          className="p-1 text-on-surface-variant hover:text-error hover:bg-error-container/20 rounded transition-colors"
                          title="Delete Document"
                        >
                          <span className="material-symbols-outlined text-[18px]">delete</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
