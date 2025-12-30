export function Footer() {
  return (
    <footer className="bg-zinc-50 border-t border-zinc-200 py-12">
      <div className="container px-6 mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 bg-zinc-900 rounded-md flex items-center justify-center">
            <div className="w-3 h-3 bg-orange-500 rounded-sm rotate-45" />
          </div>
          <span className="text-zinc-900 font-bold tracking-tight">Mohtion</span>
        </div>
        
        <div className="text-zinc-500 text-sm">
          © {new Date().getFullYear()} Mohtion Labs. All rights reserved.
        </div>

        <div className="flex gap-6">
          <a href="#" className="text-zinc-500 hover:text-zinc-900 transition-colors text-sm font-medium">GitHub</a>
          <a href="#" className="text-zinc-500 hover:text-zinc-900 transition-colors text-sm font-medium">Twitter</a>
          <a href="#" className="text-zinc-500 hover:text-zinc-900 transition-colors text-sm font-medium">Docs</a>
        </div>
      </div>
    </footer>
  );
}