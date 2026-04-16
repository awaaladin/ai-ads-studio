"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { onboardBusiness } from '@/lib/api';
import { motion } from 'framer-motion';
import { ArrowRight, Loader2 } from 'lucide-react';

export default function Onboarding() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    business_name: '',
    industry: '',
    audience: '',
    tone: 'Professional',
    colors: '#8b5cf6',
    goal: 'Increase sales'
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const project = await onboardBusiness(formData);
      router.push(`/projects/${project.id}`);
    } catch (err) {
      console.error(err);
      alert('Failed to create project.');
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto py-12">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass p-8 md:p-12 rounded-3xl border-t border-t-white/10 shadow-2xl">
        <h1 className="text-3xl font-bold mb-2">Create New Project</h1>
        <p className="text-slate-400 mb-8">Tell us about your business to generate tailored marketing assets.</p>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300">Business Name</label>
            <input required type="text" className="w-full bg-slate-900/50 border border-slate-700 rounded-xl p-3 text-white focus:ring-2 focus:ring-violet-500 outline-none transition-all" value={formData.business_name} onChange={e => setFormData({...formData, business_name: e.target.value})} placeholder="e.g. Acme Corp" />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">Industry</label>
              <input type="text" className="w-full bg-slate-900/50 border border-slate-700 rounded-xl p-3 text-white focus:ring-2 focus:ring-violet-500 outline-none transition-all" value={formData.industry} onChange={e => setFormData({...formData, industry: e.target.value})} placeholder="e.g. Technology" />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">Target Audience</label>
              <input type="text" className="w-full bg-slate-900/50 border border-slate-700 rounded-xl p-3 text-white focus:ring-2 focus:ring-violet-500 outline-none transition-all" value={formData.audience} onChange={e => setFormData({...formData, audience: e.target.value})} placeholder="e.g. Small business owners" />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">Brand Tone</label>
              <select className="w-full bg-slate-900/50 border border-slate-700 rounded-xl p-3 text-white focus:ring-2 focus:ring-violet-500 outline-none transition-all" value={formData.tone} onChange={e => setFormData({...formData, tone: e.target.value})}>
                <option>Professional</option>
                <option>Playful</option>
                <option>Authoritative</option>
                <option>Friendly</option>
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">Primary Goal</label>
              <select className="w-full bg-slate-900/50 border border-slate-700 rounded-xl p-3 text-white focus:ring-2 focus:ring-violet-500 outline-none transition-all" value={formData.goal} onChange={e => setFormData({...formData, goal: e.target.value})}>
                <option>Increase sales</option>
                <option>Brand awareness</option>
                <option>Lead generation</option>
                <option>Event promotion</option>
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">Brand Color</label>
              <div className="flex h-[50px]">
                <input type="color" className="w-full h-full bg-transparent border-0 rounded-xl cursor-pointer" value={formData.colors} onChange={e => setFormData({...formData, colors: e.target.value})} />
              </div>
            </div>
          </div>

          <button disabled={loading} type="submit" className="w-full mt-8 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-semibold py-4 rounded-xl flex justify-center items-center gap-2 transition-all shadow-lg shadow-violet-500/25 disabled:opacity-50">
            {loading ? <Loader2 className="animate-spin" /> : <>Continue to Assets <ArrowRight size={20} /></>}
          </button>
        </form>
      </motion.div>
    </div>
  );
}
