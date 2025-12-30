"use client";
import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { Search, Terminal, GitPullRequest, CheckCircle2, AlertCircle, ArrowRight } from "lucide-react";

// --- Visual Components ---

const ScannerVisual = () => (
  <div className="relative w-full h-40 bg-zinc-900 rounded-lg overflow-hidden font-mono text-[10px] p-3 flex flex-col gap-1.5 border border-zinc-800">
    <div className="flex items-center gap-2 text-zinc-500 border-b border-zinc-800 pb-1.5">
      <Search className="w-3 h-3" />
      <span>scan.log</span>
    </div>
    <div className="flex flex-col gap-1">
        <div className="text-zinc-500">[0.01s] CLONING REPO...</div>
        <div className="text-zinc-400">[0.42s] ANALYZING AST...</div>
        <motion.div 
            initial={{ opacity: 0, x: -5 }}
            animate={{ opacity: 1, x: 0 }}
            className="text-orange-400 bg-orange-400/10 px-1.5 py-0.5 rounded flex items-center gap-1.5"
        >
            <AlertCircle className="w-3 h-3" />
            COMPLEXITY: 18 (HIGH)
        </motion.div>
    </div>
    <motion.div 
        className="absolute top-0 left-0 w-full h-1 bg-orange-500/30 blur-sm"
        animate={{ top: ["0%", "100%", "0%"] }}
        transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
    />
  </div>
);

const RefactorVisual = () => (
  <div className="relative w-full h-40 bg-zinc-900 rounded-lg overflow-hidden border border-zinc-800 p-3 font-mono text-[10px]">
    <div className="text-zinc-500 mb-2 flex justify-between items-center">
      <span>AI REFACTOR</span>
      <span className="text-orange-500/50">SONNET 3.5</span>
    </div>
    <div className="space-y-0.5">
        <div className="text-red-400/50 line-through">- return x * y + z</div>
        <div className="text-green-400 bg-green-400/10 px-1">+ return calculate_product(x, y) + z</div>
        <div className="text-green-400 bg-green-400/10 px-1">+ # Refactored for clarity</div>
    </div>
  </div>
);

const VerifyVisual = () => (
  <div className="relative w-full h-40 bg-zinc-950 rounded-lg overflow-hidden border border-zinc-800 p-3 font-mono text-[10px] flex flex-col justify-end">
    <div className="text-zinc-500 mb-auto">$ pytest --quiet</div>
    <div className="flex gap-1.5 flex-wrap">
        {[1,2,3,4,5,6].map(i => (
            <motion.div 
                key={i}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: i * 0.1, repeat: Infinity, repeatDelay: 2 }}
                className="text-green-500"
            >
                .
            </motion.div>
        ))}
        <span className="text-green-400 ml-1">PASSED</span>
    </div>
    <div className="w-full bg-zinc-800 h-1 rounded-full mt-2">
        <motion.div 
            className="h-full bg-green-500"
            animate={{ width: ["0%", "100%"] }}
            transition={{ duration: 2, repeat: Infinity }}
        />
    </div>
  </div>
);

const BountyVisual = () => (
    <div className="relative w-full h-40 bg-white border border-zinc-200 rounded-lg p-3 flex flex-col items-center justify-center">
        <div className="flex items-center gap-2 mb-3 text-zinc-800 font-bold text-xs">
            <GitPullRequest className="w-4 h-4 text-purple-600" />
            <span>Refactor auth.py</span>
        </div>
        <div className="px-4 py-1.5 bg-green-600 text-white rounded text-[10px] font-bold shadow-lg shadow-green-600/20">
            MERGE PR
        </div>
        <div className="mt-2 text-[8px] text-zinc-400">
            Verified by Mohtion Bot
        </div>
    </div>
);

// --- Content ---

const STEPS = [
  {
    id: 1,
    title: "Reconnaissance",
    desc: "Scans codebases for technical debt and complexity.",
    visual: <ScannerVisual />,
  },
  {
    id: 2,
    title: "Refactoring",
    desc: "LLM agents apply best-practice transformations.",
    visual: <RefactorVisual />,
  },
  {
    id: 3,
    title: "Verification",
    desc: "Tests run in isolated sandboxes to ensure safety.",
    visual: <VerifyVisual />,
  },
  {
    id: 4,
    title: "Bounty Claim",
    desc: "Validated improvements are submitted as Pull Requests.",
    visual: <BountyVisual />,
  },
];

export function CommandCenter() {
  const [activeStep, setActiveStep] = useState(1);

  useEffect(() => {
    const timer = setInterval(() => {
      setActiveStep((s) => (s % 4) + 1);
    }, 3000);
    return () => clearInterval(timer);
  }, []);

  return (
    <section className="py-32 bg-zinc-100/50 border-y border-zinc-200 relative overflow-hidden" id="how-it-works">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-[radial-gradient(#cbd5e1_1px,transparent_1px)] [background-size:20px_20px] opacity-50" />
      
      <div className="container mx-auto px-6 relative z-10">
        
        <div className="text-center max-w-2xl mx-auto mb-20">
            <h2 className="text-4xl font-bold tracking-tight text-zinc-900">
                The Autonomous Pipeline
            </h2>
            <p className="mt-4 text-zinc-500">
                Mohtion handles the entire lifecycle of technical debt reduction.
            </p>
        </div>

        <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-4">
            {STEPS.map((step) => (
                <div key={step.id} className="relative">
                    {/* Connection Arrow (Desktop) */}
                    {step.id < 4 && (
                        <div className="hidden md:flex absolute top-1/2 -right-4 translate-x-1/2 -translate-y-1/2 z-20 items-center justify-center">
                            <ArrowRight className={cn(
                                "w-5 h-5 transition-colors duration-500",
                                activeStep === step.id ? "text-orange-500 animate-pulse" : "text-zinc-200"
                            )} />
                        </div>
                    )}

                    <div className={cn(
                        "h-full p-6 rounded-2xl bg-white border transition-all duration-500 flex flex-col gap-4",
                        activeStep === step.id 
                            ? "border-orange-500 shadow-xl shadow-orange-500/5 ring-1 ring-orange-500/20" 
                            : "border-zinc-200 opacity-60 grayscale-[0.5]"
                    )}>
                        <div className="flex items-center gap-3">
                            <span className={cn(
                                "w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold transition-colors",
                                activeStep === step.id ? "bg-orange-500 text-white" : "bg-zinc-100 text-zinc-400"
                            )}>
                                {step.id}
                            </span>
                            <h3 className="text-sm font-bold text-zinc-900">{step.title}</h3>
                        </div>
                        
                        <p className="text-xs text-zinc-500 leading-relaxed h-10">
                            {step.desc}
                        </p>

                        <div className="mt-auto">
                            {step.visual}
                        </div>
                    </div>
                </div>
            ))}
        </div>

        <div className="mt-16 text-center">
            <div className="inline-flex items-center gap-8 px-6 py-3 bg-white rounded-full border border-zinc-200 shadow-sm">
                {STEPS.map((step) => (
                    <div 
                        key={step.id}
                        className={cn(
                            "w-2 h-2 rounded-full transition-all duration-500",
                            activeStep === step.id ? "bg-orange-500 scale-150" : "bg-zinc-200"
                        )}
                    />
                ))}
            </div>
        </div>

      </div>
    </section>
  );
}
