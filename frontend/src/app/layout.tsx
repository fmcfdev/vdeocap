import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { QueryProvider } from "@/providers/query-provider";
import { Toaster } from "@/components/ui/sonner";
import { ThemeProvider } from "@/components/layout/theme-provider";
import { Navbar } from "@/components/layout/navbar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
   title: "Vdeocap | Legendas Automáticas com IA",
   description: "Transforme seus vídeos com legendas e traduções automáticas.",
};

export default function RootLayout({
   children,
}: Readonly<{
   children: React.ReactNode;
}>) {
   return (
      // Removido o className="dark" fixo para o ThemeProvider assumir o controle
      <html lang="pt-BR" suppressHydrationWarning>
         <body className={inter.className}>
            <ThemeProvider
               attribute="class"
               defaultTheme="system"
               enableSystem
               disableTransitionOnChange
            >
               <QueryProvider>
                  <div className="relative min-h-screen flex flex-col">
                     {/* Menu Superior Fixo */}
                     <Navbar />

                     {/* Conteúdo da Página */}
                     <main className="flex-1 bg-background">{children}</main>

                     {/* Feedback de notificações */}
                     <Toaster position="top-right" richColors closeButton />
                  </div>
               </QueryProvider>
            </ThemeProvider>
         </body>
      </html>
   );
}
