import { Navbar } from "@/components/Navbar";
import { Hero } from "@/components/Hero";
import { TechStack } from "@/components/TechStack";
import { CommandCenter } from "@/components/CommandCenter";
import { AgentWorkflow } from "@/components/AgentWorkflow";
import { CTA } from "@/components/CTA";
import { Footer } from "@/components/Footer";

export default function Home() {
  return (
    <main className="min-h-screen bg-zinc-50 selection:bg-orange-100 selection:text-orange-900">
      <Navbar />
      <Hero />
      <TechStack />
      <CommandCenter />
      <AgentWorkflow />
      <CTA />
      <Footer />
    </main>
  );
}
