"use client";

import { motion } from "framer-motion";
import { Github } from "lucide-react";

export function Navbar() {
  return (
    <motion.header 
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="fixed top-0 left-0 right-0 z-50 flex justify-center p-4"
    >
      <nav className="flex items-center justify-between w-full max-w-7xl px-6 py-3 bg-white/70 backdrop-blur-xl border border-zinc-200 rounded-2xl shadow-sm">
        {/* Brand */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-zinc-900 rounded-lg flex items-center justify-center">
            <div className="w-4 h-4 bg-orange-500 rounded-sm rotate-45" />
          </div>
          <span className="text-xl font-bold tracking-tighter text-zinc-900">Mohtion</span>
        </div>

        {/* Links */}
        <div className="hidden md:flex items-center gap-8">
          <a href="#features" className="text-sm font-medium text-zinc-500 hover:text-zinc-900 transition-colors">Features</a>
          <a href="#how-it-works" className="text-sm font-medium text-zinc-500 hover:text-zinc-900 transition-colors">Process</a>
          <a href="#docs" className="text-sm font-medium text-zinc-500 hover:text-zinc-900 transition-colors">Documentation</a>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-4">
          <a 
            href="https://github.com/JulianCruzet/Mohtion" 
            target="_blank"
            className="hidden sm:flex items-center gap-2 text-sm font-medium text-zinc-600 hover:text-zinc-900"
          >
            <Github className="w-4 h-4" />
            GitHub
          </a>
          <button className="px-5 py-2 bg-zinc-900 text-white text-sm font-semibold rounded-lg hover:bg-zinc-800 transition-colors">
            Get Started
          </button>
        </div>
      </nav>
    </motion.header>
  );
}
