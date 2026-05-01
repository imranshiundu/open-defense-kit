import { useState, useEffect } from 'react'
import { Shield, LayoutDashboard, Terminal, Activity, Target, Network, Settings, Globe, Play, Download, Search } from 'lucide-react'

function App() {
  const [categories, setCategories] = useState([]);
  const [tools, setTools] = useState([]);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [targetScope, setTargetScope] = useState('*.example.com');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    Promise.all([
      fetch('http://localhost:8000/api/categories').then(res => res.json()),
      fetch('http://localhost:8000/api/tools').then(res => res.json())
    ])
      .then(([catsData, toolsData]) => {
        setCategories(catsData);
        setTools(toolsData);
      })
      .catch(err => console.error("Error fetching data:", err));
  }, []);

  const filteredTools = tools.filter(t => 
    t.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
    t.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-background text-text flex flex-col font-sans">
      {/* Top Navbar */}
      <header className="border-b border-divider bg-background sticky top-0 z-50">
        <div className="max-w-[1400px] mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 border border-divider flex items-center justify-center rounded">
              <Shield className="w-6 h-6 text-primary" strokeWidth={1.5} />
            </div>
            <div className="flex flex-col">
              <span className="font-display font-bold text-lg tracking-tight uppercase leading-none">Open Defense Kit</span>
              <span className="text-[10px] text-muted font-mono tracking-widest uppercase mt-1">Audit & Defense System</span>
            </div>
          </div>
          
          <nav className="flex items-center space-x-1 border border-divider p-1 rounded">
            <button 
              onClick={() => setActiveTab('dashboard')}
              className={`px-4 py-1.5 rounded text-sm font-medium transition-all flex items-center gap-2 ${activeTab === 'dashboard' ? 'bg-primary text-black' : 'text-muted hover:text-primary hover:bg-surfaceHover'}`}
            >
              <LayoutDashboard className="w-4 h-4" />
              Overview
            </button>
            <button 
              onClick={() => setActiveTab('tools')}
              className={`px-4 py-1.5 rounded text-sm font-medium transition-all flex items-center gap-2 ${activeTab === 'tools' ? 'bg-primary text-black' : 'text-muted hover:text-primary hover:bg-surfaceHover'}`}
            >
              <Terminal className="w-4 h-4" />
              Registry
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-[1400px] w-full mx-auto px-6 py-8">
        
        {/* Universal Target Scope Bar (Always visible) */}
        <div className="mb-8 p-4 border border-divider rounded-lg bg-surface flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3 w-full sm:w-auto">
            <Target className="w-5 h-5 text-muted" />
            <div className="flex flex-col flex-1 sm:w-64">
              <label className="text-[10px] uppercase font-mono text-muted mb-1">Authorized Target Scope</label>
              <input 
                type="text" 
                value={targetScope}
                onChange={(e) => setTargetScope(e.target.value)}
                className="bg-transparent border-b border-dividerHover focus:border-primary outline-none text-sm font-mono pb-1 transition-colors"
                placeholder="IP, Domain, or CIDR"
              />
            </div>
          </div>
          <div className="flex items-center gap-3 border border-divider px-3 py-1.5 rounded bg-background">
            <div className="w-2 h-2 rounded-full bg-success animate-pulse"></div>
            <span className="text-xs font-mono text-muted uppercase">System Armed</span>
          </div>
        </div>

        {activeTab === 'dashboard' && (
          <div className="space-y-8 animate-in fade-in duration-500">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="card">
                <div className="flex items-center justify-between mb-2 text-muted">
                  <span className="text-xs uppercase tracking-wider font-mono">Modules</span>
                  <Terminal className="w-4 h-4" />
                </div>
                <div className="text-3xl font-display">{tools.length || '--'}</div>
              </div>
              <div className="card">
                <div className="flex items-center justify-between mb-2 text-muted">
                  <span className="text-xs uppercase tracking-wider font-mono">Categories</span>
                  <LayoutDashboard className="w-4 h-4" />
                </div>
                <div className="text-3xl font-display">{categories.length || '--'}</div>
              </div>
              <div className="card">
                <div className="flex items-center justify-between mb-2 text-muted">
                  <span className="text-xs uppercase tracking-wider font-mono">Installed</span>
                  <Download className="w-4 h-4" />
                </div>
                <div className="text-3xl font-display">{tools.filter(t => t.installed).length}</div>
              </div>
              <div className="card">
                <div className="flex items-center justify-between mb-2 text-muted">
                  <span className="text-xs uppercase tracking-wider font-mono">Active Jobs</span>
                  <Activity className="w-4 h-4" />
                </div>
                <div className="text-3xl font-display">0</div>
              </div>
            </div>

            {/* Quick Categories */}
            <div>
              <h2 className="text-sm font-mono uppercase tracking-widest text-muted mb-4 flex items-center gap-2">
                <Network className="w-4 h-4" /> Tactical Vectors
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                {categories.slice(0, 12).map((cat, i) => (
                  <div key={cat.id || i} className="border border-divider bg-surface hover:bg-surfaceHover hover:border-dividerHover cursor-pointer p-4 rounded transition-colors flex flex-col items-center justify-center text-center gap-2 group">
                    <span className="text-muted group-hover:text-primary transition-colors">
                      {i % 4 === 0 ? <Globe className="w-5 h-5" /> : i % 3 === 0 ? <Terminal className="w-5 h-5" /> : i % 2 === 0 ? <Shield className="w-5 h-5" /> : <Settings className="w-5 h-5" />}
                    </span>
                    <span className="text-xs font-medium">{cat.label}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'tools' && (
          <div className="space-y-6 animate-in fade-in duration-500">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
              <h2 className="text-xl font-display uppercase tracking-wider">Module Registry</h2>
              <div className="relative w-full sm:w-72">
                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
                <input 
                  type="text"
                  placeholder="Search modules..."
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  className="w-full bg-surface border border-divider rounded-md pl-9 pr-4 py-2 text-sm focus:border-primary outline-none transition-colors"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {filteredTools.map(tool => (
                <div key={tool.id} className="card flex flex-col p-5 group">
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="font-bold text-base truncate pr-2 font-display">{tool.title}</h3>
                    {tool.installed ? (
                      <div className="w-2 h-2 rounded-full bg-primary mt-1 shrink-0" title="Installed"></div>
                    ) : (
                      <div className="w-2 h-2 rounded-full bg-divider mt-1 shrink-0" title="Not Installed"></div>
                    )}
                  </div>
                  
                  <p className="text-xs text-muted mb-4 line-clamp-2 flex-grow leading-relaxed">{tool.description || 'No description available for this module.'}</p>
                  
                  <div className="flex flex-wrap gap-1 mb-5">
                    <span className="badge">{tool.category}</span>
                  </div>

                  <div className="flex gap-2 mt-auto">
                    {tool.installed ? (
                      <button className="btn-primary flex-1 py-1.5 text-xs uppercase tracking-wider font-mono">Execute</button>
                    ) : (
                      <button className="btn-secondary flex-1 py-1.5 text-xs uppercase tracking-wider font-mono">Install</button>
                    )}
                    {tool.projectUrl && (
                      <a href={tool.projectUrl} target="_blank" rel="noreferrer" className="btn-secondary px-3 py-1.5" title="Documentation">
                        <Globe className="w-3 h-3" />
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

      </main>
    </div>
  )
}

export default App
