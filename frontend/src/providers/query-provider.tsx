"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState, ReactNode } from "react";

export function QueryProvider({ children }: { children: ReactNode }) {
   // Criamos o client dentro de um state para garantir que cada aba tenha seu próprio cache
   const [queryClient] = useState(
      () =>
         new QueryClient({
            defaultOptions: {
               queries: {
                  staleTime: 60 * 1000, // Mantém os dados "frescos" por 1 minuto
                  retry: 1, // Se a API falhar, tenta apenas mais uma vez
               },
            },
         }),
   );

   return (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
   );
}
