import React from 'react';
import type { CitationItem } from '../api';

interface SourceViewerProps {
  citation: CitationItem | null;
  onClose: () => void;
}

export const SourceViewer: React.FC<SourceViewerProps> = ({ citation, onClose }) => {
  if (!citation) return null;

  return (
    <div className="fixed inset-0 z-50 bg-on-surface/20 backdrop-blur-xs flex justify-end">
      <div className="w-full max-w-lg bg-surface h-full shadow-2xl border-l border-outline-variant flex flex-col animate-in slide-in-from-right duration-200">
        {/* Header */}
        <div className="px-6 py-4 border-b border-outline-variant flex justify-between items-center bg-surface-container-low">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-[22px] text-primary">
              menu_book
            </span>
            <span className="font-semibold text-base text-on-surface truncate">
              Source Citation
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded hover:bg-surface-container text-on-surface-variant transition-colors"
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        {/* Content */}
        <div className="p-6 flex-1 overflow-y-auto space-y-6">
          {/* File Metadata */}
          <div className="bg-surface-container-lowest border border-outline-variant p-4 rounded-xl space-y-2">
            <div className="flex items-center gap-2 text-primary font-semibold text-sm">
              <span className="material-symbols-outlined text-[18px]">description</span>
              <span>{citation.file_name}</span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs text-on-surface-variant pt-2 border-t border-outline-variant/60">
              <div>
                <span className="text-outline">Page Number:</span>{' '}
                <span className="font-medium text-on-surface">
                  {citation.page_number ? `Page ${citation.page_number}` : 'N/A'}
                </span>
              </div>
              <div>
                <span className="text-outline">Section:</span>{' '}
                <span className="font-medium text-on-surface">
                  {citation.section_title || 'N/A'}
                </span>
              </div>
              <div>
                <span className="text-outline">Match Similarity:</span>{' '}
                <span className="font-medium text-primary">
                  {(citation.similarity * 100).toFixed(1)}%
                </span>
              </div>
              <div>
                <span className="text-outline">Chunk ID:</span>{' '}
                <span className="font-mono text-[10px] text-on-surface truncate block">
                  {citation.chunk_id}
                </span>
              </div>
            </div>
          </div>

          {/* Citation Reason */}
          <div>
            <h4 className="text-xs font-semibold text-outline uppercase tracking-wider mb-1">
              Citation Purpose
            </h4>
            <p className="text-sm text-on-surface bg-surface-container-low p-3 rounded-lg border border-outline-variant/50">
              {citation.reason}
            </p>
          </div>

          {/* Highlighted Passage */}
          <div>
            <h4 className="text-xs font-semibold text-outline uppercase tracking-wider mb-2">
              Retrieved Passage Snippet
            </h4>
            <div className="bg-surface-container-lowest p-4 rounded-xl border border-primary/30 shadow-xs relative">
              <div className="absolute top-2 right-2 px-2 py-0.5 bg-primary-container text-on-primary-container text-[10px] font-medium rounded">
                Verified Passage
              </div>
              <p className="text-sm text-on-surface leading-relaxed whitespace-pre-wrap font-sans">
                {citation.snippet}
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-outline-variant bg-surface-container-low flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-on-surface text-surface rounded-lg text-sm font-medium hover:bg-inverse-surface transition-colors"
          >
            Close Viewer
          </button>
        </div>
      </div>
    </div>
  );
};
