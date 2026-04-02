import { useMutation } from "@tanstack/react-query";
import { videoService } from "@/services/api-service";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { AxiosError } from "axios";

// Definimos a interface do erro que o seu FastAPI retorna (ex: { detail: "Erro X" })
interface ApiError {
   detail: string;
}

export function useUploadVideo() {
   const router = useRouter();

   return useMutation({
      mutationFn: videoService.upload,
      onSuccess: (data) => {
         toast.success("Vídeo recebido! Iniciando processamento...");
         // Redireciona para a página de status com o ID da tarefa
         router.push(`/status?id=${data.task_id}`);
      },
      onError: (error: AxiosError<ApiError>) => {
         // Aqui usamos o optional chaining de forma segura e tipada
         const message =
            error.response?.data?.detail || "Erro ao conectar com o servidor.";
         toast.error(message);
         console.error("Upload Error:", message);
      },
   });
}
