import { api } from "@/lib/api";
import { UploadFormData } from "@/schemas/upload-schema";

export const videoService = {
   upload: async (data: UploadFormData) => {
      const formData = new FormData();

      // Mapeamento exato para o que o seu FastAPI espera
      formData.append("file", data.video[0]);
      formData.append("idioma", data.language);
      formData.append("formato_video", data.format);
      formData.append("tamanho_fonte", data.fontSize);
      formData.append("cor_fonte", data.fontColor);
      formData.append("cor_fundo", data.bgColor);

      const response = await api.post("/upload", formData, {
         headers: {
            "Content-Type": "multipart/form-data",
         },
      });

      return response.data;
   },

   getStatus: async (taskId: string) => {
      const response = await api.get(`/status/${taskId}`);
      return response.data;
   },
};
