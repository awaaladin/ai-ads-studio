"use client";

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { getProject, getCreatives, generateCreatives } from '@/lib/api';
import { motion } from 'framer-motion';
import { Wand2, Download, UploadCloud, Loader2 } from 'lucide-react';

export default function ProjectView() {
  const params = useParams();
  const projectId = params.id as string;
  
  const [project, setProject] = useState<any>(null);
  const [creatives, setCreatives] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [file, setFile] = useState<File | null>(null);

  useEffect(() => {
    Promise.all([getProject(projectId), getCreatives(projectId)])
      .then(([projData, creativesData]) => {
        setProject(projData);
        setCreatives(creativesData);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [projectId]);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const res = await generateCreatives(projectId, file);
      setCreatives([res, ...creatives]);
      setFile(null);
    } catch (err) {
      console.error(err);
      alert('Failed to generate creatives.');
    }
    setGenerating(false);
  };

  if (loading) return <div className="animate-pulse space-y-4 max-w-4xl mx-auto"><div className="h-10 bg-slate-800 rounded w-1/3"></div><div className="h-64 bg-slate-800 rounded-3xl"></div></div>;
  if (!project) return <div>Project not found.</div>;

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <header className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-xl" style={{ backgroundColor: project.colors || '#8b5cf6' }}></div>
        <div>
          <h1 className="text-3xl font-extrabold">{project.business_name}</h1>
          <p className="text-slate-400">{project.industry} • Goal: {project.goal}</p>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Upload & Generate Section */}
        <div className="lg:col-span-1 space-y-6">
          <div className="glass p-6 rounded-3xl">
            <h3 className="text-xl font-bold mb-4">Generate Assets</h3>
            <p className="text-sm text-slate-400 mb-6">Upload an image, PDF or video to provide context for generation.</p>
            
            <label className="border-2 border-dashed border-slate-600 hover:border-violet-500 rounded-2xl p-8 flex flex-col items-center justify-center text-center cursor-pointer transition-colors mb-6 group">
              <UploadCloud className="text-slate-400 group-hover:text-violet-400 mb-2 transition-colors" size={32} />
              <span className="text-sm font-medium">{file ? file.name : 'Click to select asset'}</span>
              <span className="text-xs text-slate-500 mt-1">PDF, JPG, PNG or MP4</span>
              <input type="file" className="hidden" onChange={e => setFile(e.target.files?.[0] || null)} />
            </label>

            <button 
              onClick={handleGenerate} 
              disabled={generating}
              className="w-full bg-violet-600 hover:bg-violet-700 rounded-xl py-3 font-semibold flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
            >
              {generating ? <Loader2 className="animate-spin" size={18} /> : <Wand2 size={18} />}
              {generating ? 'Generating Magic...' : 'Generate New Assets'}
            </button>
          </div>
        </div>

        {/* Results Section */}
        <div className="lg:col-span-2 space-y-6">
          <h2 className="text-2xl font-bold">Ad Creatives</h2>
          {creatives.length === 0 ? (
            <div className="glass p-12 rounded-3xl text-center border-dashed border-2 border-slate-700">
              <p className="text-slate-400">No creatives generated yet. Try uploading an asset and hit generate!</p>
            </div>
          ) : (
            <div className="space-y-6">
              {creatives.map((c, i) => (
                <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} key={c.id} className="glass p-6 rounded-3xl space-y-6 overflow-hidden relative">
                  
                  <div className="space-y-4 relative z-10">
                    <div>
                      <h4 className="text-sm font-bold tracking-wider text-violet-400 uppercase mb-2">Ad Copy</h4>
                      <p className="bg-slate-900/50 p-4 rounded-xl text-slate-200 whitespace-pre-wrap font-medium">{c.copy}</p>
                    </div>

                    {c.social_posts && c.social_posts.length > 0 && (
                      <div>
                        <h4 className="text-sm font-bold tracking-wider text-blue-400 uppercase mb-2">Social Posts</h4>
                        <div className="space-y-2">
                          {c.social_posts.map((post: string, j: number) => (
                            <div key={j} className="bg-slate-900/50 p-3 rounded-xl text-slate-300 text-sm">{post}</div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {c.pdf_brochure_url && (
                      <div className="pt-4 border-t border-white/5">
                        <a href={c.pdf_brochure_url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-white px-5 py-2.5 rounded-lg text-sm font-medium transition-colors">
                          <Download size={16} /> Download PDF Brochure
                        </a>
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
