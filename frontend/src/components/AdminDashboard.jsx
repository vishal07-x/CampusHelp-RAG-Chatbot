import React, { useState, useEffect } from 'react';
import { 
  Upload, 
  FileText, 
  Trash2, 
  RefreshCw, 
  BarChart3, 
  History, 
  CheckCircle2, 
  AlertCircle, 
  Clock, 
  Database,
  Layers,
  Search,
  ShieldAlert,
  ArrowUpRight,
  TrendingUp,
  FileCheck2,
  FolderOpen
} from 'lucide-react';
import { 
  uploadDocuments, 
  getDocuments, 
  deleteDocument, 
  reindexDocument, 
  getAdminAnalytics, 
  getAdminLogs 
} from '../api/client';
import { useAuth } from '../context/AuthContext';

export const AdminDashboard = ({ onOpenAuth }) => {
  const { user, isAdmin, isAuthenticated } = useAuth();
  const [activeAdminTab, setActiveAdminTab] = useState('documents'); // 'documents', 'analytics', 'logs'
  
  // Documents state
  const [documents, setDocuments] = useState([]);
  const [docsLoading, setDocsLoading] = useState(false);
  const [uploadFiles, setUploadFiles] = useState([]);
  const [department, setDepartment] = useState('Academics');
  const [category, setCategory] = useState('Regulations');
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(null);
  const [actionMessage, setActionMessage] = useState(null);

  // Analytics & Logs state
  const [analytics, setAnalytics] = useState(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [logs, setLogs] = useState([]);
  const [logsLoading, setLogsLoading] = useState(false);

  // Load documents
  const fetchDocuments = async () => {
    setDocsLoading(true);
    try {
      const data = await getDocuments();
      setDocuments(data.documents || []);
    } catch (e) {
      console.error('Failed to load documents:', e);
    } finally {
      setDocsLoading(false);
    }
  };

  // Load analytics
  const fetchAnalytics = async () => {
    setAnalyticsLoading(true);
    try {
      const data = await getAdminAnalytics();
      setAnalytics(data);
    } catch (e) {
      console.error('Failed to load analytics:', e);
    } finally {
      setAnalyticsLoading(false);
    }
  };

  // Load audit logs
  const fetchLogs = async () => {
    setLogsLoading(true);
    try {
      const data = await getAdminLogs(50, 0);
      setLogs(data.logs || []);
    } catch (e) {
      console.error('Failed to load query logs:', e);
    } finally {
      setLogsLoading(false);
    }
  };

  useEffect(() => {
    if (isAdmin) {
      if (activeAdminTab === 'documents') fetchDocuments();
      if (activeAdminTab === 'analytics') fetchAnalytics();
      if (activeAdminTab === 'logs') fetchLogs();
    }
  }, [isAdmin, activeAdminTab]);

  // Handle PDF Upload
  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!uploadFiles.length) return;

    setUploading(true);
    setUploadProgress('Extracting pages, generating embeddings & indexing in Qdrant...');
    setActionMessage(null);

    const formData = new FormData();
    for (let i = 0; i < uploadFiles.length; i++) {
      formData.append('files', uploadFiles[i]);
    }
    formData.append('department', department);
    formData.append('category', category);

    try {
      const results = await uploadDocuments(formData);
      setActionMessage({
        type: 'success',
        text: `Processed ${results.length} document(s) successfully!`,
      });
      setUploadFiles([]);
      fetchDocuments();
    } catch (err) {
      console.error('Upload failed:', err);
      setActionMessage({
        type: 'error',
        text: err.response?.data?.detail || 'Document upload and indexing failed.',
      });
    } finally {
      setUploading(false);
      setUploadProgress(null);
    }
  };

  // Handle Document Delete
  const handleDelete = async (docId, docName) => {
    if (!window.confirm(`Are you sure you want to delete '${docName}'? This removes all vector embeddings and chunks permanently.`)) {
      return;
    }
    try {
      await deleteDocument(docId);
      setActionMessage({ type: 'success', text: `Document '${docName}' deleted.` });
      fetchDocuments();
    } catch (err) {
      setActionMessage({ type: 'error', text: 'Failed to delete document.' });
    }
  };

  // Handle Document Re-index
  const handleReindex = async (docId, docName) => {
    try {
      setActionMessage({ type: 'info', text: `Re-indexing '${docName}'...` });
      await reindexDocument(docId);
      setActionMessage({ type: 'success', text: `Successfully re-indexed '${docName}'!` });
      fetchDocuments();
    } catch (err) {
      setActionMessage({ type: 'error', text: 'Re-indexing failed.' });
    }
  };

  if (!isAuthenticated || !isAdmin) {
    return (
      <div className="flex-1 flex items-center justify-center p-6 bg-slate-50">
        <div className="max-w-md w-full bg-white p-8 rounded-2xl border border-slate-200 shadow-sm text-center">
          <div className="w-12 h-12 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center mx-auto mb-4 border border-amber-200">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-slate-800 mb-2">Administrator Access Required</h3>
          <p className="text-xs text-slate-500 mb-6">
            Document management, vector re-indexing, and query audit analytics are reserved for college administrators.
          </p>
          <button
            onClick={() => onOpenAuth('login')}
            className="w-full py-2.5 px-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow-sm transition-all"
          >
            Sign In with Administrator Account
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto bg-slate-50 p-4 sm:p-6 lg:p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        
        {/* Header & Subtabs */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-200 gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Institutional Admin Center</h1>
            <p className="text-xs text-slate-500 mt-0.5">Manage institutional PDFs, monitor retrieval latencies & inspect query logs.</p>
          </div>

          <div className="flex items-center space-x-2 bg-slate-200/80 p-1 rounded-xl text-xs font-medium">
            <button
              onClick={() => setActiveAdminTab('documents')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg transition-all ${
                activeAdminTab === 'documents'
                  ? 'bg-white text-indigo-700 font-semibold shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <FileCheck2 className="w-3.5 h-3.5" />
              <span>Documents ({documents.length})</span>
            </button>
            <button
              onClick={() => setActiveAdminTab('analytics')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg transition-all ${
                activeAdminTab === 'analytics'
                  ? 'bg-white text-indigo-700 font-semibold shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <BarChart3 className="w-3.5 h-3.5" />
              <span>Analytics</span>
            </button>
            <button
              onClick={() => setActiveAdminTab('logs')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg transition-all ${
                activeAdminTab === 'logs'
                  ? 'bg-white text-indigo-700 font-semibold shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <History className="w-3.5 h-3.5" />
              <span>Query Logs</span>
            </button>
          </div>
        </div>

        {/* Global Notifications / Alerts */}
        {actionMessage && (
          <div className={`p-3 rounded-xl border text-xs flex items-center justify-between ${
            actionMessage.type === 'success' 
              ? 'bg-emerald-50 text-emerald-800 border-emerald-200' 
              : actionMessage.type === 'error'
              ? 'bg-rose-50 text-rose-800 border-rose-200'
              : 'bg-indigo-50 text-indigo-800 border-indigo-200'
          }`}>
            <div className="flex items-center space-x-2">
              {actionMessage.type === 'success' ? <CheckCircle2 className="w-4 h-4 text-emerald-600" /> : <AlertCircle className="w-4 h-4" />}
              <span>{actionMessage.text}</span>
            </div>
            <button onClick={() => setActionMessage(null)} className="text-xs font-bold px-2 py-0.5">✕</button>
          </div>
        )}

        {/* TAB 1: DOCUMENTS MANAGEMENT & UPLOAD */}
        {activeAdminTab === 'documents' && (
          <div className="space-y-6">
            
            {/* Upload Card */}
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
              <h3 className="text-sm font-bold text-slate-800 flex items-center space-x-2 mb-3">
                <Upload className="w-4 h-4 text-indigo-600" />
                <span>Upload New Institutional Documents (PDF)</span>
              </h3>

              <form onSubmit={handleFileUpload} className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-slate-600 mb-1">Department</label>
                    <select
                      value={department}
                      onChange={(e) => setDepartment(e.target.value)}
                      className="w-full text-xs bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                    >
                      <option value="Academics">Academics</option>
                      <option value="Finance">Finance & Fees</option>
                      <option value="Examinations">Examinations</option>
                      <option value="Placements">Placements</option>
                      <option value="Facilities">Campus & Facilities</option>
                      <option value="Admissions">Admissions</option>
                      <option value="General">General</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-600 mb-1">Document Category</label>
                    <select
                      value={category}
                      onChange={(e) => setCategory(e.target.value)}
                      className="w-full text-xs bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                    >
                      <option value="Regulations">Academic Regulations</option>
                      <option value="Fees">Fee Structures</option>
                      <option value="Policies">Campus Policies</option>
                      <option value="Curriculum">Curriculum & Syllabus</option>
                      <option value="Notices">Important Notices</option>
                      <option value="Guidelines">Guidelines & Manuals</option>
                    </select>
                  </div>
                </div>

                {/* File picker */}
                <div className="border-2 border-dashed border-slate-300 hover:border-indigo-400 rounded-2xl p-6 text-center bg-slate-50/50 hover:bg-indigo-50/20 transition-all cursor-pointer">
                  <input
                    type="file"
                    multiple
                    accept=".pdf"
                    onChange={(e) => setUploadFiles(Array.from(e.target.files))}
                    className="hidden"
                    id="pdf-upload-input"
                  />
                  <label htmlFor="pdf-upload-input" className="cursor-pointer">
                    <FolderOpen className="w-10 h-10 text-indigo-500 mx-auto mb-2 stroke-1" />
                    <p className="text-xs font-semibold text-slate-700">
                      {uploadFiles.length > 0 
                        ? `${uploadFiles.length} file(s) selected: ${uploadFiles.map(f => f.name).join(', ')}`
                        : "Click to select or drop college PDF documents here"}
                    </p>
                    <p className="text-[11px] text-slate-400 mt-1">Accepts multiple .pdf files up to 20MB each</p>
                  </label>
                </div>

                {/* Ingestion progress */}
                {uploadProgress && (
                  <div className="p-3 bg-indigo-50 rounded-xl text-xs text-indigo-700 flex items-center space-x-2 animate-pulse">
                    <RefreshCw className="w-4 h-4 animate-spin text-indigo-600" />
                    <span>{uploadProgress}</span>
                  </div>
                )}

                <div className="flex justify-end">
                  <button
                    type="submit"
                    disabled={uploading || uploadFiles.length === 0}
                    className={`flex items-center space-x-2 px-5 py-2.5 rounded-xl text-xs font-semibold text-white shadow-sm transition-all ${
                      uploadFiles.length > 0 && !uploading
                        ? 'bg-indigo-600 hover:bg-indigo-700 shadow-indigo-200'
                        : 'bg-slate-300 cursor-not-allowed'
                    }`}
                  >
                    <Upload className="w-4 h-4" />
                    <span>{uploading ? 'Ingesting & Indexing...' : 'Upload & Index Documents'}</span>
                  </button>
                </div>
              </form>
            </div>

            {/* Document List Table */}
            <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
              <div className="px-5 py-3.5 border-b border-slate-200 flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-slate-800">Indexed Institutional Documents</h3>
                  <p className="text-[11px] text-slate-400">All documents actively participating in hybrid vector & keyword retrieval.</p>
                </div>
                <button
                  onClick={fetchDocuments}
                  className="p-1.5 text-slate-400 hover:text-indigo-600 rounded-lg hover:bg-slate-100 transition-colors"
                >
                  <RefreshCw className={`w-4 h-4 ${docsLoading ? 'animate-spin' : ''}`} />
                </button>
              </div>

              {documents.length === 0 ? (
                <div className="text-center py-12 text-slate-400 text-xs">
                  <FileText className="w-8 h-8 mx-auto mb-2 text-slate-300 stroke-1" />
                  <p>No documents uploaded yet. Use the upload form above to add college resources.</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs text-slate-700">
                    <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200 uppercase text-[10px] tracking-wider">
                      <tr>
                        <th className="px-5 py-3">Document Name</th>
                        <th className="px-4 py-3">Department</th>
                        <th className="px-4 py-3">Pages</th>
                        <th className="px-4 py-3">Chunks</th>
                        <th className="px-4 py-3">Status</th>
                        <th className="px-4 py-3 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {documents.map((doc) => (
                        <tr key={doc.id} className="hover:bg-slate-50/80 transition-colors">
                          <td className="px-5 py-3 font-medium text-slate-900">
                            <div className="flex items-center space-x-2">
                              <FileText className="w-4 h-4 text-indigo-500 flex-shrink-0" />
                              <span className="truncate max-w-xs">{doc.original_name}</span>
                            </div>
                          </td>
                          <td className="px-4 py-3 text-slate-600">
                            <span className="px-2 py-0.5 bg-slate-100 text-slate-700 rounded-md font-medium text-[11px]">
                              {doc.department}
                            </span>
                          </td>
                          <td className="px-4 py-3 font-semibold text-slate-800">{doc.total_pages}</td>
                          <td className="px-4 py-3 font-semibold text-indigo-600">{doc.total_chunks}</td>
                          <td className="px-4 py-3">
                            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold ${
                              doc.status === 'INDEXED' 
                                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' 
                                : 'bg-rose-50 text-rose-700 border border-rose-200'
                            }`}>
                              {doc.status}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-right space-x-2">
                            <button
                              onClick={() => handleReindex(doc.id, doc.original_name)}
                              title="Re-index document"
                              className="p-1 text-slate-400 hover:text-indigo-600 rounded-md hover:bg-slate-100"
                            >
                              <RefreshCw className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={() => handleDelete(doc.id, doc.original_name)}
                              title="Delete document"
                              className="p-1 text-slate-400 hover:text-rose-600 rounded-md hover:bg-slate-100"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
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
        )}

        {/* TAB 2: SYSTEM ANALYTICS */}
        {activeAdminTab === 'analytics' && (
          <div className="space-y-6">
            {analyticsLoading && !analytics ? (
              <div className="p-12 text-center text-xs text-slate-400 animate-pulse">Loading system metrics...</div>
            ) : analytics ? (
              <>
                {/* Metric Summary Cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
                    <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Total Documents</div>
                    <div className="text-2xl font-bold text-slate-900 mt-1">{analytics.total_documents}</div>
                    <div className="text-[11px] text-emerald-600 mt-1 font-medium">{analytics.total_chunks} total vector chunks</div>
                  </div>

                  <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
                    <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Total Queries Handled</div>
                    <div className="text-2xl font-bold text-slate-900 mt-1">{analytics.total_queries}</div>
                    <div className="text-[11px] text-indigo-600 mt-1 font-medium">{analytics.total_users} registered users</div>
                  </div>

                  <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
                    <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Avg Response Time</div>
                    <div className="text-2xl font-bold text-slate-900 mt-1">{(analytics.avg_total_latency_ms / 1000).toFixed(2)}s</div>
                    <div className="text-[11px] text-slate-500 mt-1">Retrieval: {analytics.avg_retrieval_latency_ms}ms</div>
                  </div>

                  <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
                    <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Satisfaction Rate</div>
                    <div className="text-2xl font-bold text-slate-900 mt-1">{analytics.feedback_satisfaction_rate}%</div>
                    <div className="text-[11px] text-emerald-600 mt-1 font-medium">👍 {analytics.positive_feedback_count} • 👎 {analytics.negative_feedback_count}</div>
                  </div>
                </div>

                {/* Distributions */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* By Department */}
                  <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
                    <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-3">Documents by Department</h4>
                    <div className="space-y-2">
                      {Object.entries(analytics.department_distribution || {}).map(([dept, count]) => (
                        <div key={dept} className="flex items-center justify-between text-xs">
                          <span className="text-slate-600 font-medium">{dept}</span>
                          <span className="font-bold text-indigo-600">{count} doc(s)</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* By Category */}
                  <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
                    <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-3">Documents by Category</h4>
                    <div className="space-y-2">
                      {Object.entries(analytics.category_distribution || {}).map(([cat, count]) => (
                        <div key={cat} className="flex items-center justify-between text-xs">
                          <span className="text-slate-600 font-medium">{cat}</span>
                          <span className="font-bold text-indigo-600">{count} doc(s)</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </>
            ) : null}
          </div>
        )}

        {/* TAB 3: QUERY AUDIT LOGS */}
        {activeAdminTab === 'logs' && (
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
            <div className="px-5 py-3.5 border-b border-slate-200 flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-slate-800">Student Query Audit Trail</h3>
                <p className="text-[11px] text-slate-400">Chronological audit log of student queries, retrieval latencies, and citations.</p>
              </div>
              <button
                onClick={fetchLogs}
                className="p-1.5 text-slate-400 hover:text-indigo-600 rounded-lg hover:bg-slate-100 transition-colors"
              >
                <RefreshCw className={`w-4 h-4 ${logsLoading ? 'animate-spin' : ''}`} />
              </button>
            </div>

            {logs.length === 0 ? (
              <div className="text-center py-12 text-slate-400 text-xs">No query activity recorded yet.</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-700">
                  <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200 uppercase text-[10px] tracking-wider">
                    <tr>
                      <th className="px-5 py-3">Timestamp</th>
                      <th className="px-4 py-3">Student Query</th>
                      <th className="px-4 py-3">Total Latency</th>
                      <th className="px-4 py-3">Citations</th>
                      <th className="px-4 py-3">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {logs.map((log) => (
                      <tr key={log.id} className="hover:bg-slate-50/80 transition-colors">
                        <td className="px-5 py-3 text-slate-400 font-mono text-[11px]">
                          {new Date(log.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                        </td>
                        <td className="px-4 py-3 font-medium text-slate-900 max-w-sm truncate">
                          {log.query_text}
                        </td>
                        <td className="px-4 py-3 text-slate-600 font-mono">
                          {(log.total_latency_ms / 1000).toFixed(2)}s
                        </td>
                        <td className="px-4 py-3 text-indigo-600 font-semibold">
                          {log.retrieved_sources ? log.retrieved_sources.length : 0} source(s)
                        </td>
                        <td className="px-4 py-3">
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                            {log.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
};
