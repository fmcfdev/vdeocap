"use client";

import { Menu, Video, Moon, Sun, Monitor, History } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
   Sheet,
   SheetContent,
   SheetHeader,
   SheetTitle,
   SheetTrigger,
} from "@/components/ui/sheet";
import { useTheme } from "next-themes";
import Link from "next/link";
import { ThemeToggle } from "./theme-toggle";

export function Navbar() {
   const { setTheme } = useTheme();

   return (
      <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
         <div className="container flex h-16 items-center justify-between px-4 sm:px-8">
            {/* Logo e Nome VdeoCap */}
            <Link
               href="/"
               className="flex items-center gap-2 transition-opacity hover:opacity-90"
            >
               <div className="bg-primary p-1.5 rounded-lg shadow-sm">
                  <Video className="w-5 h-5 sm:w-6 sm:h-6 text-primary-foreground" />
               </div>
               <span className="font-bold text-lg sm:text-xl tracking-tight">
                  VdeoCap
               </span>
            </Link>

            {/* Lado Direito: Toggle e Menu */}
            <div className="flex items-center gap-3">
               <ThemeToggle />

               <Sheet>
                  {/* Trigger do Menu Mobile/Desktop */}
                  <SheetTrigger className="inline-flex items-center justify-center rounded-md p-2 hover:bg-accent transition-colors">
                     <Menu className="h-6 w-6" />
                  </SheetTrigger>

                  {/* Sidebar Conteúdo */}
                  <SheetContent
                     side="left"
                     className="w-[280px] sm:w-[350px] p-0"
                  >
                     <SheetHeader className="p-6 text-left border-b bg-muted/30">
                        <SheetTitle className="flex items-center gap-2">
                           <Video className="w-5 h-5 text-primary" />
                           <span className="font-bold text-xl">VdeoCap</span>
                        </SheetTitle>
                     </SheetHeader>

                     <div className="p-4">
                        <nav className="flex flex-col gap-2">
                           <Button
                              variant="secondary"
                              className="w-full justify-start gap-3 h-11 px-4 font-medium"
                           >
                              <Monitor className="h-5 w-5 shrink-0" />
                              <span>Novo Projeto</span>
                           </Button>
                        </nav>
                     </div>
                  </SheetContent>
               </Sheet>
            </div>
         </div>
      </header>
   );
}
