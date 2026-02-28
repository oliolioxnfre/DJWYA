import Image from "next/image";
import { AnimatedText } from "@/components/ui/AnimatedText";
import { LoginButton } from "@/components/auth/LoginButton";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 lg:p-24 relative overflow-hidden bg-black selection:bg-brand-pink/30">
      {/* Background gradients/glows */}
      <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-brand-purple/20 rounded-full blur-[150px] -z-10 pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-brand-neon/20 rounded-full blur-[150px] -z-10 pointer-events-none" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-brand-pink/10 rounded-full blur-[200px] -z-10 pointer-events-none" />

      <div className="text-center z-10 w-full max-w-7xl mx-auto flex flex-col items-center space-y-12">
        <div className="flex flex-col items-center space-y-8">
          <Image
            src="/logo.png"
            alt="DJWYA Logo"
            width={300}
            height={300}
            className="drop-shadow-[0_0_30px_rgba(139,92,246,0.5)] transition-transform duration-500 hover:scale-110"
            priority
          />
          <AnimatedText />
        </div>

        <div className="flex flex-col items-center space-y-6 pt-12">
          <p className="text-zinc-400 max-w-lg text-lg text-center font-sans">
            Discover your Sonic DNA and find the festivals that match your exact vibe.
          </p>
          <LoginButton />
        </div>
      </div>
    </main>
  );
}
