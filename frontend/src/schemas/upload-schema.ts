import * as z from "zod";

const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100MB
const ACCEPTED_VIDEO_TYPES = ["video/mp4", "video/webm", "video/quicktime"];

export const uploadSchema = z.object({
   video: z
      .custom<FileList>()
      .refine((files) => files?.length === 1, "O vídeo é obrigatório.")
      .refine(
         (files) => files?.[0]?.size <= MAX_FILE_SIZE,
         `O tamanho máximo é 100MB.`,
      )
      .refine(
         (files) => ACCEPTED_VIDEO_TYPES.includes(files?.[0]?.type),
         "Formato inválido. Use MP4, WebM ou MOV.",
      ),
   language: z.string().min(1, "Selecione o idioma."),
   format: z.string().min(1, "Selecione o formato."),
   fontSize: z.string().min(1, "Selecione o tamanho da fonte."),
   fontColor: z.string().regex(/^#[0-9A-F]{6}$/i, "Cor inválida."),
   bgColor: z.string().regex(/^#[0-9A-F]{6}$/i, "Cor inválida."),
});

export type UploadFormData = z.infer<typeof uploadSchema>;
