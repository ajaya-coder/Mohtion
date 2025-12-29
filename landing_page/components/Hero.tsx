"use client";

import { motion } from "framer-motion";
import { ArrowRight, Github } from "lucide-react";
import { TerminalDemo } from "./TerminalDemo";

export function Hero() {
  return (
    <section className="relative pt-32 pb-24 overflow-hidden">
      {/* Background Grid */}
      <div className="absolute inset-0 grid-bg opacity-20 -z-10" />

      <div className="container px-6 mx-auto">
        <div className="flex flex-col lg:flex-row items-center gap-16">
          {/* Text Content */}
          <div className="flex-1 text-center lg:text-left">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <div className="inline-flex items-center gap-2 px-3 py-1 mb-8 text-xs font-medium text-indigo-300 rounded-full bg-indigo-500/10 border border-indigo-500/20">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
                </span>
                MVP Production Validated
              </div>

              <h1 className="text-5xl lg:text-7xl font-bold tracking-tighter text-white mb-6">
                Pay Down Tech Debt <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400 glow-text">
                  While You Sleep.
                </span>
              </h1>

              <p className="text-lg text-slate-400 mb-8 leading-relaxed max-w-2xl mx-auto lg:mx-0">
                Mohtion is the autonomous agent that scans your repositories, refactors complex code, runs your tests, and opens PRs. Zero supervision required.
              </p>

              <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4">
                <button className="group relative px-8 py-4 bg-slate-50 text-slate-950 font-semibold rounded-lg hover:bg-white transition-all hover:scale-105 active:scale-95 flex items-center gap-2">
                  <Github className="w-5 h-5" />
                  Install GitHub App
                  <div className="absolute inset-0 rounded-lg ring-2 ring-white/20 group-hover:ring-white/40 transition-all" />
                </button>
                <button className="px-8 py-4 text-slate-400 font-medium hover:text-white transition-colors flex items-center gap-2 group">
                  Read Documentation
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </button>
              </div>
            </motion.div>
          </div>

          {/* Visual Content */}
          <div className="flex-1 w-full max-w-lg lg:max-w-xl">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="relative"
            >
              <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-2xl blur opacity-20" />
              <TerminalDemo />
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
}
