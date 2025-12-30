"use client";
import { motion } from "framer-motion";
import { ArrowRight, Github, Sparkles } from "lucide-react";
import dynamic from "next/dynamic";

const BackgroundBeams = dynamic(
  () => import("@/components/ui/background-beams").then((mod) => mod.BackgroundBeams),
  { ssr: false }
);

export function CTA() {
  return (
    <section className="py-24 bg-zinc-50">
      <div className="container mx-auto px-6">
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="relative rounded-3xl overflow-hidden bg-zinc-900 px-8 py-20 text-center shadow-2xl"
        >
          {/* Animated Background */}
          <BackgroundBeams className="absolute inset-0" />
          
          <div className="relative z-10 max-w-2xl mx-auto">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-orange-500/10 border border-orange-500/20 text-orange-400 text-xs font-bold mb-6">
              <Sparkles className="w-3 h-3" />
              STAY AHEAD OF THE DEBT
            </div>
            
            <h2 className="text-3xl md:text-5xl font-bold text-white tracking-tight mb-6">
              Ready to clear your <br />
              <span className="text-orange-500">technical debt?</span>
            </h2>
            
            <p className="text-zinc-400 text-lg mb-10 leading-relaxed">
              Join the public beta and let Mohtion handle the cleanup while you focus on building new features.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <button className="w-full sm:w-auto px-8 py-4 bg-white text-zinc-950 font-bold rounded-xl hover:bg-zinc-100 transition-all flex items-center justify-center gap-2 group">
                <Github className="w-5 h-5" />
                Install on GitHub
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </button>
              <button className="w-full sm:w-auto px-8 py-4 bg-zinc-800 text-white font-semibold rounded-xl hover:bg-zinc-700 transition-all">
                Join the Waitlist
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
