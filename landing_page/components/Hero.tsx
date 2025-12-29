"use client";

import { motion } from "framer-motion";
import { TerminalDemo } from "./TerminalDemo";
import { ArrowRight, Terminal } from "lucide-react";

export function Hero() {
  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center bg-white overflow-hidden pt-32 pb-16">
      
      {/* 1. Base Grid Pattern (Subtle) */}
      <div className="absolute inset-0 z-0 w-full h-full bg-white bg-[radial-gradient(#e5e7eb_1px,transparent_1px)] [background-size:16px_16px] [mask-image:radial-gradient(ellipse_50%_50%_at_50%_50%,#000_70%,transparent_100%)]"></div>

      {/* 2. Top-Right Aurora (Orange) */}
      <div className="absolute top-[-20%] right-[-10%] w-[600px] h-[600px] rounded-full bg-orange-200/50 blur-[80px] z-0 pointer-events-none" />

      {/* 3. Bottom-Left Aurora (Blue) */}
      <div className="absolute bottom-[-20%] left-[-10%] w-[600px] h-[600px] rounded-full bg-blue-100/50 blur-[80px] z-0 pointer-events-none" />

      <div className="relative z-10 container px-6 mx-auto flex flex-col items-center text-center">
        
        {/* Badge */}
        <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-white/60 bg-white/50 backdrop-blur-sm shadow-sm mb-6 z-20"
        >
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-orange-500"></span>
            </span>
            <span className="text-xs font-semibold text-zinc-600 tracking-wide uppercase">Mohtion Public Beta</span>
        </motion.div>

        {/* Headline */}
        <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-4xl md:text-6xl lg:text-7xl font-bold tracking-tighter text-zinc-900 mb-4 max-w-4xl z-20"
        >
          Pay Down Tech Debt <br/>
          <span className="text-orange-500">While You Sleep.</span>
        </motion.h1>

        {/* Subhead */}
        <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-base md:text-lg text-zinc-500 max-w-2xl mb-8 leading-relaxed z-20"
        >
          The autonomous agent that monitors your repositories, identifies complexity, and opens Pull Requests with verified fixes.
        </motion.p>

        {/* Buttons */}
        <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="flex flex-col sm:flex-row items-center gap-4 mb-12 z-20"
        >
            <button className="px-8 py-3 bg-zinc-900 text-white rounded-lg font-medium hover:bg-zinc-800 transition-colors shadow-lg shadow-zinc-900/20 flex items-center gap-2 text-sm">
                <Terminal className="w-4 h-4" />
                Install GitHub App
            </button>
            <button className="px-8 py-3 bg-white/80 backdrop-blur-sm text-zinc-600 border border-zinc-200 rounded-lg font-medium hover:bg-white transition-colors flex items-center gap-2 group text-sm">
                Read Documentation
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
        </motion.div>

        {/* Terminal Visual */}
        <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 40 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.6 }}
            className="w-full max-w-2xl relative z-10"
        >
            {/* Glow under terminal */}
            <div className="absolute -inset-2 bg-gradient-to-r from-orange-500/20 to-blue-500/20 rounded-3xl blur-2xl opacity-40" />
            <TerminalDemo />
        </motion.div>

      </div>
    </section>
  );
}
