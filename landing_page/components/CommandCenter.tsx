"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion, useInView } from "framer-motion";
import { cn } from "@/lib/utils";
import { Search, Terminal, GitPullRequest, CheckCircle2, AlertCircle, FileDiff, Layers, Bot, Code } from "lucide-react";

// --- Visual Components for each card ---

const ScannerVisual = () => (
  <div className="w-full h-28 bg-zinc-900 rounded-lg overflow-hidden font-mono text-[9px] p-2 flex flex-col gap-1 border border-zinc-800">
    <div className="flex items-center gap-1 text-zinc-500 border-b border-zinc-800 pb-1">
      <Search className="w-2.5 h-2.5" />
      <span>scan.log</span>
    </div>
    <div className="flex flex-col gap-0.5">
        <div className="text-zinc-500">[0.01s] CLONING REPO...</div>
        <div className="text-zinc-400">[0.42s] ANALYZING AST...</div>
        <motion.div initial={{ opacity: 0, x: -5 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.5 }} className="text-orange-400 bg-orange-400/10 px-1 py-0.5 rounded flex items-center gap-1">
            <AlertCircle className="w-2.5 h-2.5" />
            COMPLEXITY: 18 (auth.py)
        </motion.div>
    </div>
    <motion.div 
        className="absolute top-0 left-0 w-full h-0.5 bg-orange-500/30 blur-sm"
        animate={{ top: ["0%", "100%", "0%"] }}
        transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
    />
  </div>
);

const RefactorVisual = () => (
    <div className="w-full h-28 bg-zinc-900 rounded-lg border border-zinc-800 p-2 font-mono text-[9px] space-y-0.5">
        <div className="text-red-400/50 line-through">- return x*y+z &gt; 10 ? "a" : "b"</div>
        <div className="text-green-400">+ const is_over_threshold = (x*y*z) &gt; 10;</div>
        <div className="text-green-400">+ return is_over_threshold ? "a" : "b";</div>
  </div>
);

const VerifyVisual = () => (
  <div className="w-full h-28 bg-zinc-950 rounded-lg border border-zinc-800 p-2 font-mono text-[9px] flex flex-col justify-end">
    <div className="text-zinc-500 mb-auto">$ pytest --quiet</div>
    <div className="flex gap-1 flex-wrap">
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
    <div className="w-full bg-zinc-800 h-0.5 rounded-full mt-1">
        <motion.div 
            className="h-full bg-green-500"
            animate={{ width: ["0%", "100%"] }}
            transition={{ duration: 2, repeat: Infinity }}
        />
    </div>
  </div>
);

const BountyVisual = () => (
    <div className="w-full h-28 bg-white border border-zinc-200 rounded-lg p-2 flex flex-col items-center justify-center">
        <div className="flex items-center gap-1 mb-2 text-zinc-800 font-bold text-[10px]">
            <GitPullRequest className="w-3.5 h-3.5 text-purple-600" />
            <span>Refactor auth.py</span>
        </div>
        <div className="px-3 py-1 bg-green-600 text-white rounded text-[8px] font-bold shadow-lg shadow-green-600/20">
            MERGE PR
        </div>
        <div className="mt-1 text-[7px] text-zinc-400">
            ✓ Verified by Mohtion Bot
        </div>
    </div>
);

// --- Content ---

const STEPS = [
  { id: 1, title: "Reconnaissance", desc: "Deep AST analysis identifies debt.", visual: <ScannerVisual />, subPanel: <div className="p-2 bg-zinc-100 rounded-md text-[9px]"><Layers className="w-3.5 h-3.5 inline mr-1 text-zinc-400"/>Targets Found: <span className="font-bold">3</span></div> },
  { id: 2, title: "Refactoring", desc: "LLM agents apply best-practice transformations.", visual: <RefactorVisual />, subPanel: <div className="p-2 bg-zinc-100 rounded-md text-[9px]"><FileDiff className="w-3.5 h-3.5 inline mr-1 text-zinc-400"/>Diff: <span className="font-bold">-2 / +3 lines</span></div> },
  { id: 3, title: "Verification", desc: "Sandboxed tests ensure safety.", visual: <VerifyVisual />, subPanel: <div className="p-2 bg-zinc-100 rounded-md text-[9px]"><CheckCircle2 className="w-3.5 h-3.5 inline mr-1 text-zinc-400"/>Coverage: <span className="font-bold">98.7%</span></div> },
  { id: 4, title: "Bounty Claim", desc: "Validated PRs are submitted for review.", visual: <BountyVisual />, subPanel: <div className="p-2 bg-zinc-100 rounded-md text-[9px]"><Bot className="w-3.5 h-3.5 inline mr-1 text-zinc-400"/>Agent: <span className="font-bold">mohtion-bot</span></div> },
];

export function CommandCenter() {
  const [activeStep, setActiveStep] = useState(1);
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  useEffect(() => {
    if (!isInView) return;
    
    const timer = setInterval(() => { setActiveStep((s) => (s % 4) + 1); }, 2500);
    return () => clearInterval(timer);
  }, [isInView]);

  return (
    <section ref={ref} className="py-20 bg-zinc-100 border-y border-zinc-200 relative overflow-hidden" id="how-it-works">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-[radial-gradient(#cbd5e1_1px,transparent_1px)] [background-size:20px_20px] opacity-50" />
      
      <div className="container mx-auto px-6 relative z-10">
        
        <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-3xl font-bold tracking-tight text-zinc-900">A Fully Autonomous Pipeline</h2>
            <p className="mt-3 text-base text-zinc-500">Mohtion operates like a senior engineer, handling the entire lifecycle of technical debt reduction without human intervention.</p>
        </div>

        <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-4 relative"> {/* Changed to md:grid-cols-2 */}
            {STEPS.map((step, i) => (
                <div key={step.id} className={cn(
                    "p-4 rounded-2xl bg-white border-2 transition-all duration-500 flex flex-col gap-3",
                    activeStep === step.id ? "border-orange-500 shadow-xl shadow-orange-500/10" : "border-zinc-200 opacity-70"
                )}>
                    <div className="flex items-center gap-2">
                        <span className={cn("w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold transition-colors", activeStep === step.id ? "bg-orange-500 text-white" : "bg-zinc-100 text-zinc-500")}>{step.id}</span>
                        <h3 className="text-lg font-bold text-zinc-900">{step.title}</h3>
                    </div>
                    <p className="text-sm text-zinc-500 leading-relaxed min-h-[30px]">{step.desc}</p>
                    <div className="mt-auto flex flex-col gap-2">
                        {step.visual}
                        {step.subPanel}
                    </div>
                </div>
            ))}
            {/* No need for arrows, flow is implied by numbering */}
        </div>

        <div className="mt-10 text-center">
            <div className="inline-flex items-center gap-6 px-4 py-2 bg-white rounded-full border border-zinc-200 shadow-sm">
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