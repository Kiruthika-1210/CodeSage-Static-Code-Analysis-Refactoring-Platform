import React, { useState } from "react";

function VersionHistory({ versions, onSaveVersion, canSave }) {
  const [selectedVersion, setSelectedVersion] = useState(null);

  return (
    <div className="mt-8 p-6 rounded-2xl bg-[#0d0d0f] border border-[#1a1a1d] shadow-xl text-white">

      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="flex items-center gap-2 text-xl font-semibold text-[#d4a44d]">
          Version History
          <span className="px-2 py-0.5 rounded-full text-xs bg-[#1a1a1d] border border-[#262629] text-gray-300">
            {versions.length}
          </span>
        </h2>

        <button
          onClick={onSaveVersion}
          disabled={!canSave}
          className={`px-4 py-1 rounded-lg text-sm font-medium transition
            ${
              canSave
                ? "text-black bg-yellow-500 hover:bg-yellow-400"
                : "bg-neutral-700 text-neutral-400 cursor-not-allowed"
            }`}
        >
          💾 Save Version
        </button>
      </div>

      {/* Timeline */}
      {versions.length === 0 ? (
        <p className="text-gray-500 text-sm">
          No versions saved yet.
        </p>
      ) : (
        <div className="space-y-4">
          {versions.map((version) => (
            <div
              key={version.id}
              className="flex justify-between items-center p-4 rounded-xl
                         bg-[#101012] border border-[#1f1f22]"
            >
              <div>
                <p className="font-medium text-gray-200">{version.id}</p>
                <p className="text-sm text-gray-500">
                  {version.timestamp}
                </p>
              </div>

              <button
                onClick={() => setSelectedVersion(version)}
                className="px-4 py-1 rounded-lg text-sm font-medium
                           text-[#d4a44d] border border-[#d4a44d]/60
                           hover:bg-black transition"
              >
                View Details
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {selectedVersion && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
          <div className="w-[90%] max-w-3xl bg-[#0d0d0f]
                          border border-[#1a1a1d]
                          rounded-2xl p-6 shadow-2xl relative">

            <button
              onClick={() => setSelectedVersion(null)}
              className="absolute top-4 right-4 text-gray-400 hover:text-white"
            >
              ✕
            </button>

            <h3 className="text-lg font-semibold mb-4 text-[#d4a44d]">
              {selectedVersion.id} Details
            </h3>

            <div className="grid grid-cols-2 gap-4 mb-6 text-sm">
              <div>
                <p className="text-gray-400">Complexity</p>
                <p>
                  {selectedVersion.complexity
                    ? `${selectedVersion.complexity.bigO} (${selectedVersion.complexity.score}/100)`
                    : "—"}
                </p>
              </div>
              <div>
                <p className="text-gray-400">Score</p>
                <p>
                  {selectedVersion.score
                    ? `${selectedVersion.score.final}/100`
                    : "—"}
                </p>
              </div>
            </div>

            <div className="mb-4">
              <p className="text-gray-400 mb-1">Code Snapshot</p>
              <pre className="bg-[#101012] border border-[#1f1f22]
                              rounded-lg p-4 text-sm text-gray-300 overflow-x-auto">
{selectedVersion.code}
              </pre>
            </div>

            <div className="mb-4">
              <p className="text-gray-400 mb-1">Issues</p>
              {selectedVersion.issues.length === 0 ? (
                <p className="text-green-400 text-sm">No issues 🎉</p>
              ) : (
                <ul className="list-disc list-inside text-sm text-gray-300">
                  {selectedVersion.issues.map((issue, idx) => (
                    <li key={idx}>
                      {issue.type} — {issue.message}
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div>
              <p className="text-gray-400 mb-1">Diff</p>
              <pre className="bg-[#101012] border border-[#1f1f22]
                              rounded-lg p-4 text-sm text-gray-300 overflow-x-auto">
{selectedVersion.diff}
              </pre>
            </div>

          </div>
        </div>
      )}
    </div>
  );
}

export default VersionHistory;
