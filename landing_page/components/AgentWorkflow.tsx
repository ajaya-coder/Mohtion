"use client";
import React, { useRef } from "react";
import { ContainerScroll } from "@/components/ui/container-scroll-animation";
import { motion, useInView } from "framer-motion";
import { Check } from "lucide-react";

const TerminalLog = () => {
    const containerRef = useRef(null);
    const isInView = useInView(containerRef, { once: true, margin: "-100px" });

    return (
        <div ref={containerRef} className="w-full h-full bg-zinc-900 font-mono text-xs text-zinc-400 p-4 overflow-y-scroll scrollbar-hide">
            <div className="flex flex-col gap-2">
                <p>$ mohtion start --repo=your/project</p>
                <p className="text-green-400 flex items-center gap-2"><Check className="h-4 w-4" /> Mohtion agent initialized.</p>
                <br />
                <p>[1/4] SCANNING REPOSITORY...</p>
                <p>&gt; Cloning repository...</p>
                <p>&gt; Analyzing Abstract Syntax Tree...</p>
                <motion.div initial={{ opacity: 0 }} animate={isInView ? { opacity: 1 } : { opacity: 0 }} transition={{ delay: 0.5 }}>
                    <p className="text-orange-400">WARN: High cyclomatic complexity found in `auth.py` (score: 18)</p>
                </motion.div>
                <motion.div initial={{ opacity: 0 }} animate={isInView ? { opacity: 1 } : { opacity: 0 }} transition={{ delay: 1 }}>
                    <p className="text-orange-400">WARN: Deprecated library usage in `utils.py`</p>
                </motion.div>
                <br />
                <motion.div initial={{ opacity: 0 }} animate={isInView ? { opacity: 1 } : { opacity: 0 }} transition={{ delay: 1.5 }}>
                    <p>[2/4] REFACTORING CODE...</p>
                    <p>&gt; Generating patch for `auth.py` with Claude 3.5 Sonnet...</p>
                    <div className="p-2 bg-zinc-800 rounded-md my-2 text-[10px]">
                        <p className="text-red-400/70">-    if user and user.is_admin and user.has_permissions and not user.is_banned:</p>
                        <p className="text-green-400/80">+    if is_authorized(user):</p>
                    </div>
                    <p className="text-green-400 flex items-center gap-2"><Check className="h-4 w-4" /> Patch generated successfully.</p>
                </motion.div>
                <br/>
                <motion.div initial={{ opacity: 0 }} animate={isInView ? { opacity: 1 } : { opacity: 0 }} transition={{ delay: 3 }}>
                    <p>[3/4] VERIFYING CHANGES...</p>
                    <p>&gt; Running test suite in sandboxed environment...</p>
                    <p className="text-green-400">....................................</p>
                    <p className="text-green-400 flex items-center gap-2"><Check className="h-4 w-4" /> 142 tests passed.</p>
                </motion.div>
                <br/>
                <motion.div initial={{ opacity: 0 }} animate={isInView ? { opacity: 1 } : { opacity: 0 }} transition={{ delay: 4 }}>
                    <p>[4/4] CREATING PULL REQUEST...</p>
                    <p>&gt; Pushing changes to `mohtion/bounty-auth-refactor`</p>
                    <p className="text-purple-400 flex items-center gap-2"><Check className="h-4 w-4" /> Pull Request opened: <span className="underline">https://github.com/your/project/pull/123</span></p>
                </motion.div>
                <br/>
                <motion.div initial={{ opacity: 0 }} animate={isInView ? { opacity: 1 } : { opacity: 0 }} transition={{ delay: 5 }}>
                    <p className="text-green-400 flex items-center gap-2"><Check className="h-4 w-4" /> WORK COMPLETE. AGENT SLEEPING.</p>
                </motion.div>
            </div>
        </div>
    );
};

export function AgentWorkflow() {
  return (
    <div className="flex flex-col overflow-hidden bg-zinc-900" id="features">
      <ContainerScroll
        titleComponent={
          <>
            <h1 className="text-4xl font-semibold text-zinc-100 dark:text-white">
              Watch the Agent Work, <br />
              <span className="text-4xl md:text-[6rem] font-bold mt-1 leading-none text-transparent bg-clip-text bg-gradient-to-r from-orange-500 to-amber-500">
                Live and Unedited.
              </span>
            </h1>
          </>
        }
      >
        <TerminalLog />
      </ContainerScroll>
    </div>
  );
}