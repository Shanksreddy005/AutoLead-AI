import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BrowserRouter as Router, Routes, Route, Link, useParams, useNavigate } from 'react-router-dom';
import { Activity, Users, FileText, CheckCircle, Mail, Globe, ArrowLeft, RefreshCw } from 'lucide-react';

const API_URL = 'http://localhost:8000';

function Dashboard() {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchLeads = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/leads`);
      setLeads(response.data);
    } catch (error) {
      console.error("Error fetching leads:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeads();
    const interval = setInterval(fetchLeads, 5000); // Polling every 5s for updates
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Activity className="text-indigo-600" size={32} />
              AutoLead AI Dashboard
            </h1>
            <p className="text-gray-500 mt-2">Real-time view of all processed leads</p>
          </div>
          <button onClick={fetchLeads} className="p-2 bg-white rounded-full shadow hover:bg-gray-50 text-gray-600">
            <RefreshCw size={20} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>

        <div className="bg-white rounded-xl shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Lead Info</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Company</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {leads.map((lead) => (
                <tr key={lead.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 font-bold">
                        {lead.name.charAt(0)}
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-900">{lead.name}</div>
                        <div className="text-sm text-gray-500 flex items-center gap-1">
                          <Mail size={14} /> {lead.email}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-gray-900">{lead.company_name}</div>
                    <a href={lead.company_url} target="_blank" rel="noreferrer" className="text-sm text-indigo-600 hover:text-indigo-900 flex items-center gap-1">
                      <Globe size={14} /> Website
                    </a>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium 
                      ${lead.status === 'Completed' ? 'bg-green-100 text-green-800' : 
                        lead.status.includes('Error') ? 'bg-red-100 text-red-800' : 
                        'bg-blue-100 text-blue-800 animate-pulse'}`}>
                      {lead.status === 'Completed' && <CheckCircle size={14} className="mr-1" />}
                      {lead.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm font-medium">
                    {lead.pdf_path ? (
                      <a href={`${API_URL}/${lead.pdf_path.replace(/\\/g, '/')}`} target="_blank" rel="noreferrer" className="text-indigo-600 hover:text-indigo-900 flex items-center gap-1">
                        <FileText size={16} /> View PDF Report
                      </a>
                    ) : (
                      <span className="text-gray-400 flex items-center gap-1"><FileText size={16} /> Pending...</span>
                    )}
                  </td>
                </tr>
              ))}
              {leads.length === 0 && !loading && (
                <tr>
                  <td colSpan="4" className="px-6 py-12 text-center text-gray-500">
                    <Users size={48} className="mx-auto text-gray-300 mb-4" />
                    No leads processed yet. Wait for a submission from the capture form!
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
      </Routes>
    </Router>
  );
}

export default App;
