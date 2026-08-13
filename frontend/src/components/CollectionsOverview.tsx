import React, { useState } from 'react';
import { api } from '../api';
import type { CollectionItem, DocumentRecord } from '../api';

interface CollectionsOverviewProps {
  collections: CollectionItem[];
  documents: DocumentRecord[];
  onRefreshCollections: () => void;
  onSelectCollectionForChat: (colId: string) => void;
  onToggleMobileMenu?: () => void;
}

export const CollectionsOverview: React.FC<CollectionsOverviewProps> = ({
  collections,
  documents,
  onRefreshCollections,
  onSelectCollectionForChat,
  onToggleMobileMenu,
}) => {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setSubmitting(true);
    try {
      await api.createCollection(name, description);
      setName('');
      setDescription('');
      setShowCreateModal(false);
      onRefreshCollections();
    } catch (err) {
      console.error("Failed to create collection", err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteCollection = async (id: string) => {
    if (!confirm("Delete this collection? (Notes inside will remain intact)")) return;
    try {
      await api.deleteCollection(id);
      onRefreshCollections();
    } catch (e) {
      console.error("Failed to delete collection", e);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-screen w-full ml-0 md:ml-[250px] bg-surface overflow-y-auto">
      {/* Top Header */}
      <header className="h-16 border-b border-outline-variant bg-surface flex justify-between items-center px-4 md:px-8 z-10 sticky top-0">
        <div className="flex items-center gap-2.5">
          <button
            onClick={onToggleMobileMenu}
            className="md:hidden p-1.5 rounded-lg text-on-surface hover:bg-surface-container transition-colors"
            aria-label="Toggle navigation menu"
          >
            <span className="material-symbols-outlined text-[24px]">menu</span>
          </button>
          <div>
            <h2 className="text-sm md:text-base font-bold text-on-surface">Collections Overview</h2>
            <p className="text-[11px] md:text-xs text-outline hidden sm:block">Organize notes and documents into topic collections</p>
          </div>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-1.5 px-3 py-1.5 md:px-4 md:py-2 bg-on-surface text-surface rounded-lg text-xs font-medium hover:bg-inverse-surface transition-colors shadow-xs"
        >
          <span className="material-symbols-outlined text-[16px]">create_new_folder</span>
          <span className="hidden sm:inline">New Collection</span>
        </button>
      </header>

      <div className="p-4 md:p-8 max-w-5xl w-full mx-auto space-y-6 md:space-y-8">
        {collections.length === 0 ? (
          <div className="bg-surface-container-lowest border border-outline-variant rounded-2xl p-12 text-center space-y-3">
            <div className="w-12 h-12 rounded-full bg-secondary-container text-on-secondary-container flex items-center justify-center mx-auto">
              <span className="material-symbols-outlined text-[24px]">folder_off</span>
            </div>
            <h3 className="text-base font-semibold text-on-surface">No Collections Created</h3>
            <p className="text-xs text-outline max-w-md mx-auto">
              Create collections to group related notes together (e.g. "DBMS Notes", "OS Revision", "Machine Learning").
            </p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="mt-2 px-4 py-2 bg-primary text-on-primary rounded-lg text-xs font-medium hover:bg-primary-container transition-colors"
            >
              Create First Collection
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {collections.map((col) => {
              const colDocs = documents.filter((d) => d.collection_id === col.id);
              return (
                <div
                  key={col.id}
                  className="bg-surface-container-lowest border border-outline-variant rounded-xl p-5 hover:border-primary transition-all flex flex-col justify-between space-y-4 shadow-xs"
                >
                  <div className="space-y-2">
                    <div className="flex justify-between items-start">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-primary-container text-on-primary-container flex items-center justify-center font-bold">
                          <span className="material-symbols-outlined text-[18px]">folder</span>
                        </div>
                        <h4 className="font-bold text-sm text-on-surface truncate" title={col.name}>
                          {col.name}
                        </h4>
                      </div>

                      <button
                        onClick={() => handleDeleteCollection(col.id)}
                        className="p-1 text-on-surface-variant hover:text-error hover:bg-error-container/20 rounded transition-colors"
                        title="Delete Collection"
                      >
                        <span className="material-symbols-outlined text-[18px]">delete</span>
                      </button>
                    </div>

                    <p className="text-xs text-outline line-clamp-2">
                      {col.description || 'No description provided.'}
                    </p>
                  </div>

                  <div className="pt-3 border-t border-outline-variant/60 flex justify-between items-center text-xs">
                    <span className="text-outline font-medium">
                      {colDocs.length} {colDocs.length === 1 ? 'Note' : 'Notes'}
                    </span>

                    <button
                      onClick={() => onSelectCollectionForChat(col.id)}
                      className="flex items-center gap-1 text-primary font-medium hover:underline"
                    >
                      <span>Chat with Collection</span>
                      <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Create Collection Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-on-surface/20 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-surface border border-outline-variant rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 animate-in fade-in zoom-in duration-150">
            <div className="flex justify-between items-center">
              <h3 className="text-base font-bold text-on-surface">Create New Collection</h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="p-1 text-on-surface-variant hover:bg-surface-container rounded"
              >
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-on-surface mb-1">Collection Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. DBMS Semester 4"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg px-3 py-2 text-sm text-on-surface focus:outline-none focus:border-primary"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-on-surface mb-1">Description (Optional)</label>
                <textarea
                  placeholder="Short summary of topics in this collection..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={3}
                  className="w-full bg-surface-container-lowest border border-outline-variant rounded-lg px-3 py-2 text-sm text-on-surface focus:outline-none focus:border-primary resize-none"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 border border-outline-variant rounded-lg text-xs font-medium text-on-surface hover:bg-surface-container"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-primary text-on-primary rounded-lg text-xs font-medium hover:bg-primary-container transition-colors disabled:opacity-50"
                >
                  {submitting ? 'Creating...' : 'Create Collection'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
