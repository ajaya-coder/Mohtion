"use client";
import { motion } from "framer-motion";

export function TechStack() {
  const techs = [
    { name: "Python", logo: "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" },
    { name: "Claude AI", logo: "https://avatars.githubusercontent.com/u/76263028?s=200&v=4" },
    { name: "GitHub", logo: "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/github/github-original.svg" },
    { name: "FastAPI", logo: "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/fastapi/fastapi-original.svg" },
    { name: "Docker", logo: "https://cdn.jsdelivr.net/gh/devicons/devicon/icons/docker/docker-original.svg" },
  ];

  return (
    <section className="py-12 bg-zinc-50 border-y border-zinc-100 relative overflow-hidden">
      {/* Background Grid */}
      <div className="absolute inset-0 bg-[radial-gradient(#e5e7eb_1px,transparent_1px)] [background-size:16px_16px] opacity-50" />
      
      <div className="container mx-auto px-6 relative z-10">
        <p className="text-center text-[10px] font-bold text-zinc-800 tracking-[0.2em] uppercase mb-8">
          Built with Industry Leading Tech
        </p>
        <div className="flex flex-wrap items-center justify-center gap-8 md:gap-16 transition-all duration-700">
          {techs.map((tech) => (
            <motion.div 
              key={tech.name} 
              className="flex items-center gap-2"
              whileHover={{ y: -2 }}
            >
              <img src={tech.logo} alt={tech.name} className="h-6 w-auto object-contain" />
              <span className="text-zinc-950 font-bold text-sm tracking-tight">{tech.name}</span>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
