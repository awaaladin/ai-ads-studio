"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getProjects } from '@/lib/api';
import { Plus, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Home() {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getProjects()
      .then(setProjects)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight">Your Campaigns</h1>
          <p className="text-slate-400 mt-2">Manage your AI-generated marketing assets.</p>
        </div>
        <Link href="/onboarding">
          <motion.button 
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center gap-2 bg-violet-600 hover:bg-violet-700 px-6 py-3 rounded-full font-medium transition-colors shadow-lg shadow-violet-500/20"
          >
            <Plus size={20} /> New Project
          </motion.button>
        </Link>
      </header>

      {loading ? (
        <div className="animate-pulse flex space-x-4">
          <div className="flex-1 space-y-4 py-1">
            <div className="h-20 bg-slate-800 rounded-2xl"></div>
            <div className="h-20 bg-slate-800 rounded-2xl"></div>
          </div>
        </div>
      ) : projects.length === 0 ? (
        <div className="glass rounded-3xl p-12 text-center border-dashed border-2 border-slate-700">
          <h3 className="text-2xl font-semibold mb-2">No projects yet</h3>
          <p className="text-slate-400 mb-6">Create your first business profile to get started.</p>
          <Link href="/onboarding" className="text-violet-400 hover:text-violet-300 inline-flex items-center gap-2 font-medium">
            Start onboarding <ArrowRight size={16} />
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {projects.map((project, i) => (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              key={project.id}
            >
              <Link href={`/projects/${project.id}`}>
                <div className="glass rounded-2xl p-6 hover:border-violet-500/50 transition-colors group cursor-pointer h-full border-t border-t-white/10 shadow-xl shadow-black/50">
                  <div className="w-12 h-12 rounded-xl mb-4" style={{ backgroundColor: project.colors || '#8b5cf6' }}></div>
                  <h3 className="text-xl font-semibold mb-1 group-hover:text-violet-400 transition-colors">{project.business_name}</h3>
                  <p className="text-slate-400 text-sm line-clamp-2">{project.industry} • {project.goal}</p>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
