"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Terminal, Check, X, GitPullRequest, Search, Zap } from "lucide-react";
import clsx from "clsx";

const LOGS = [
  { type: "info", text: "Scanning repository...", icon: Search, color: "text-blue-400" },
  { type: "success", text: "Found target: Complexity > 15 (auth.py)", icon: Zap, color: "text-amber-400" },
  { type: "info", text: "Refactoring with Claude Sonnet...", icon: Terminal, color: "text-purple-400" },
  { type: "info", text: "Verifying changes with pytest...", icon: Terminal, color: "text-slate-400" },
  { type: "success", text: "Tests passed (142/142)!", icon: Check, color: "text-green-400" },
  { type: "success", text: "PR Created: mohtion/bounty-8f2a", icon: GitPullRequest, color: "text-green-400" },
];

export function TerminalDemo() {
  const [lines, setLines] = useState<number>(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setLines((prev) => (prev < LOGS.length ? prev + 1 : 0));
    }, 1200);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="w-full max-w-lg mx-auto bg-slate-900 rounded-xl overflow-hidden border border-slate-800 shadow-2xl shadow-indigo-500/10">
      {/* Window Controls */}
      <div className="flex items-center gap-2 px-4 py-3 bg-slate-900 border-b border-slate-800">
        <div className="w-3 h-3 rounded-full bg-red-500/20 border border-red-500/50" />
        <div className="w-3 h-3 rounded-full bg-yellow-500/20 border border-yellow-500/50" />
        <div className="w-3 h-3 rounded-full bg-green-500/20 border border-green-500/50" />
        <div className="ml-2 text-xs font-mono text-slate-500">mohtion-worker — 85x24</div>
      </div>

      {/* Terminal Content */}
      <div className="p-4 font-mono text-sm h-[280px] flex flex-col gap-3 bg-slate-950/50">
        {LOGS.slice(0, lines + 1).map((log, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center gap-3"
          >
            <log.icon className={clsx("w-4 h-4", log.color)} />
            <span className={clsx(log.type === "success" ? "text-slate-200" : "text-slate-400")}>
              {log.text}
            </span>
          </motion.div>
        ))}
        {lines < LOGS.length && (
          <motion.div
            animate={{ opacity: [0, 1] }}
            transition={{ repeat: Infinity, duration: 0.8 }}
            className="w-2 h-4 bg-indigo-500/50"
          />
        )}
      </div>
    </div>
  );
}
