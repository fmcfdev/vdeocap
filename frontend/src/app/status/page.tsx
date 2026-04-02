"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { videoService } from "@/services/api-service";
import { Progress } from "@/components/ui/progress";
import {
   Card,
   CardContent,
   CardHeader,
   CardTitle,
   CardDescription,
} from "@/components/ui/card";
import {
   Loader2,
   CheckCircle2,
   AlertCircle,
   Download,
   ArrowLeft,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import type { VideoStatusResponse } from "@/types/api";

// 1. Criamos um subcomponente que contém a lógica do status
function StatusContent() {
   const searchParams = useSearchParams();
   const taskId = searchParams.get("id");

   // React Query para Polling Automático
   const { data, error } = useQuery<VideoStatusResponse>({
      queryKey: ["video-status", taskId],
      queryFn: () => videoService.getStatus(taskId!),
      enabled: !!taskId, // Só roda se tiver ID
      refetchInterval: (query) => {
         // Se estiver pronto, falhou ou deu erro na API, para de perguntar
         if (
            query.state.data?.status === "completed" ||
            query.state.data?.status === "failed" ||
            query.state.data?.error
         ) {
            return false;
         }
         return 2000; // Pergunta a cada 2 segundos
      },
   });

   // TELA DE ERRO 1: Sem ID na URL
   if (!taskId) {
      return (
         <Card className="w-full max-w-[95%] sm:max-w-md border-destructive shadow-xl mx-auto">
            <CardHeader className="text-center space-y-2">
               <AlertCircle className="w-12 h-12 text-destructive mx-auto" />
               <CardTitle className="text-xl sm:text-2xl font-bold">
                  Link Inválido
               </CardTitle>
               <CardDescription>
                  Nenhum ID de processamento foi informado.
               </CardDescription>
            </CardHeader>
            <CardContent>
               <Link href="/">
                  <Button className="w-full" variant="outline">
                     <ArrowLeft className="w-4 h-4 mr-2" /> Voltar para o Início
                  </Button>
               </Link>
            </CardContent>
         </Card>
      );
   }

   const status = data?.status || "pending";
   const progress = data?.progress || 0;
   const hasApiError = !!data?.error;

   // TELA DE ERRO 2: ID não encontrado no Backend ou Erro no Processamento
   if (hasApiError || status === "failed") {
      return (
         <Card className="w-full max-w-[95%] sm:max-w-md border-destructive shadow-xl mx-auto">
            <CardHeader className="text-center space-y-2">
               <AlertCircle className="w-12 h-12 text-destructive mx-auto" />
               <CardTitle className="text-xl sm:text-2xl font-bold">
                  Erro no Processamento
               </CardTitle>
               <CardDescription className="text-xs sm:text-sm break-all opacity-70">
                  ID: {taskId}
               </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
               <div className="text-center text-sm font-medium text-destructive px-2">
                  {data?.error ||
                     data?.message ||
                     "Ocorreu um erro inesperado."}
               </div>
               <Link href="/">
                  <Button className="w-full" variant="outline">
                     <ArrowLeft className="w-4 h-4 mr-2" /> Tentar Novamente
                  </Button>
               </Link>
            </CardContent>
         </Card>
      );
   }

   // TELA DE SUCESSO OU PROCESSAMENTO (Caminho Feliz)
   return (
      <Card className="w-full max-w-[95%] sm:max-w-md border-vega-border shadow-xl mx-auto">
         <CardHeader className="text-center space-y-1 sm:space-y-2">
            <CardTitle className="text-xl sm:text-2xl font-bold tracking-tight">
               Processando seu Vídeo
            </CardTitle>
            <CardDescription className="text-xs sm:text-sm break-all opacity-70">
               ID: {taskId}
            </CardDescription>
         </CardHeader>

         <CardContent className="space-y-6">
            {/* Ícones de Estado */}
            <div className="flex justify-center py-2 sm:py-4">
               <div className="transform scale-90 sm:scale-100">
                  {(status === "processing" || status === "pending") && (
                     <Loader2 className="w-12 h-12 animate-spin text-primary" />
                  )}
                  {status === "completed" && (
                     <CheckCircle2 className="w-12 h-12 text-green-500" />
                  )}
               </div>
            </div>

            {/* Barra de Progresso */}
            <div className="space-y-2">
               <div className="flex justify-between text-sm font-medium">
                  <span>
                     {status === "completed" ? "Concluído" : "Progresso da IA"}
                  </span>
                  <span>{progress}%</span>
               </div>
               <Progress value={progress} className="h-2" />
            </div>

            {/* Mensagens Dinâmicas */}
            <div
               className={`text-center text-sm font-medium px-2 ${
                  status === "processing" || status === "pending"
                     ? "animate-pulse text-muted-foreground"
                     : "text-foreground"
               }`}
            >
               {data?.message || "Iniciando comunicação com a IA..."}
            </div>

            {/* Botão de Download */}
            {status === "completed" && (
               <Button className="w-full h-12 sm:h-11 bg-green-600 hover:bg-green-700 text-white font-bold transition-all shadow-lg">
                  <a
                     href={`http://localhost:8000/download/${taskId}`}
                     target="_blank"
                     rel="noopener noreferrer"
                     download={`vdeocap-${taskId}.mp4`}
                     className="flex items-center justify-center"
                  >
                     <Download className="mr-2 h-5 w-5" />
                     Baixar Vídeo Legendado
                  </a>
               </Button>
            )}
         </CardContent>
      </Card>
   );
}

// 2. Exportamos a página com o <Suspense> exigido pelo Next.js
export default function StatusPage() {
   return (
      <div className="flex items-center justify-center min-h-[calc(100vh-64px)] p-4 sm:p-6">
         <Suspense
            fallback={
               <div className="flex flex-col items-center justify-center space-y-4">
                  <Loader2 className="w-10 h-10 animate-spin text-primary" />
                  <p className="text-sm text-muted-foreground font-medium">
                     Carregando status...
                  </p>
               </div>
            }
         >
            <StatusContent />
         </Suspense>
      </div>
   );
}
