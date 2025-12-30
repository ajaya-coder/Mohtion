"use client";
import React from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

export const BackgroundBeams = ({ className }: { className?: string }) => {
  return (
    <div
      className={cn(
        "absolute inset-0 z-0 h-full w-full bg-neutral-950 overflow-hidden",
        className
      )}
    >
        <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(ellipse_at_center,transparent_20%,#000)]" />
       {/* Animated Beams */}
       {[...Array(5)].map((_, i) => (
           <motion.div
                key={i}
                initial={{ opacity: 0, x: -100, y: -100, rotate: 45 }}
                animate={{ opacity: [0, 1, 0], x: 400, y: 400 }}
                transition={{
                    duration: 5 + Math.random() * 5,
                    repeat: Infinity,
                    delay: Math.random() * 5,
                    ease: "easeInOut",
                }}
                className="absolute w-[2px] h-[300px] bg-gradient-to-b from-transparent via-orange-500/50 to-transparent blur-sm"
                style={{
                    left: `${Math.random() * 100}%`,
                    top: `${Math.random() * 100}%`,
                }}
           />
       ))}
    </div>
  );
};
