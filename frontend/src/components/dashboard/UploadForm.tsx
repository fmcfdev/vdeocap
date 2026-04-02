"use client";

import { useRef } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { uploadSchema, type UploadFormData } from "@/schemas/upload-schema";
import { Button } from "@/components/ui/button";
import {
   Card,
   CardContent,
   CardHeader,
   CardTitle,
   CardDescription,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
   Select,
   SelectContent,
   SelectItem,
   SelectTrigger,
   SelectValue,
} from "@/components/ui/select";
import { UploadCloud, CloudCheck } from "lucide-react";
import { useUploadVideo } from "@/hooks/use-upload";

export function UploadForm() {
   const { mutate, isPending } = useUploadVideo();
   const colorInputRef = useRef<HTMLInputElement>(null);

   const {
      register,
      handleSubmit,
      setValue,
      watch,
      formState: { errors },
   } = useForm<UploadFormData>({
      resolver: zodResolver(uploadSchema),
      // CORREÇÃO 1: Definir strings vazias ou padrões evita o erro de "uncontrolled"
      defaultValues: {
         fontColor: "#FFFF00",
         bgColor: "#000000", // NOVO: Valor padrão para o fundo
         fontSize: "media",
         language: "pt",
         format: "vertical",
      },
   });

   const selectedColor = watch("fontColor") || "#FFFF00";
   const selectedBg = watch("bgColor") || "#000000"; // NOVO: Monitora a cor de fundo
   const selectedSize = watch("fontSize") || "media";
   const videoFile = watch("video");
   const hasVideo = videoFile && videoFile.length > 0;
   const selectedVideoName = hasVideo ? videoFile[0].name : "";

   const sizeMap = {
      pequena: "text-sm",
      media: "text-lg",
      grande: "text-2xl",
   };

   const labelsIdioma: Record<string, string> = {
      pt: "Português",
      en: "Inglês",
      es: "Espanhol",
   };

   const labelsFormato: Record<string, string> = {
      vertical: "Vertical (9:16)",
      horizontal: "Horizontal (16:9)",
   };

   const labelsTamanho: Record<string, string> = {
      pequena: "Pequena",
      media: "Média",
      grande: "Grande",
   };

   const onSubmit = (data: UploadFormData) => {
      mutate(data);
   };

   return (
      <Card className="w-full max-w-2xl mx-auto border-vega-border bg-vega-card/50 backdrop-blur-sm shadow-2xl">
         <CardHeader className="text-center space-y-2 px-4 sm:px-6">
            <div className="flex items-center justify-center gap-2">
               <UploadCloud className="w-6 h-6 sm:w-7 sm:h-7 text-primary shrink-0" />
               <CardTitle className="text-2xl sm:text-3xl font-extrabold tracking-tight">
                  VdeoCap
               </CardTitle>
            </div>
            <CardDescription className="text-sm sm:text-base max-w-[450px] mx-auto">
               Suba seu vídeo para gerar legendas automáticas.
            </CardDescription>
         </CardHeader>

         <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
               {/* Campo de Arquivo */}
               <div className="space-y-2 w-full">
                  <Label
                     htmlFor="video"
                     className="text-sm sm:text-base font-medium px-1"
                  >
                     Arquivo de Vídeo
                  </Label>
                  <div
                     className={`relative group cursor-pointer border-2 border-dashed rounded-xl transition-all duration-200 
      ${
         errors.video
            ? "border-destructive/50 bg-destructive/5"
            : hasVideo
              ? "border-primary/50 bg-primary/5" // Mantém a cor do seu tema, mas deixa "ativo"
              : "border-muted-foreground/25 hover:border-primary/50 hover:bg-primary/5"
      }`}
                  >
                     <Input
                        id="video"
                        type="file"
                        accept="video/*"
                        {...register("video")}
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                     />
                     <div className="flex flex-col items-center justify-center py-8 px-4 text-center space-y-3">
                        {hasVideo ? (
                           // --- ESTADO: COM VÍDEO SELECIONADO ---
                           <>
                              <div className="bg-primary/10 p-3 rounded-full group-hover:scale-110 transition-transform duration-200">
                                 <CloudCheck className="w-8 h-8 text-primary" />
                              </div>
                              <div className="space-y-1">
                                 <p className="text-sm sm:text-base font-semibold">
                                    Vídeo Selecionado
                                 </p>
                                 <p className="text-xs bg-primary/10 rounded-md p-1.5 text-primary font-mono truncate max-w-[250px] mx-auto">
                                    {selectedVideoName}
                                 </p>
                                 <p className="text-[10px] text-muted-foreground underline pt-1">
                                    Clique ou arraste outro para trocar
                                 </p>
                              </div>
                           </>
                        ) : (
                           // --- ESTADO: PADRÃO (VAZIO) ---
                           <>
                              <div className="bg-primary/10 p-3 rounded-full group-hover:scale-110 transition-transform duration-200">
                                 <UploadCloud className="w-8 h-8 text-primary" />
                              </div>
                              <div className="space-y-1">
                                 <p className="text-sm sm:text-base font-semibold">
                                    Clique para enviar ou arraste o vídeo
                                 </p>
                                 <p className="text-xs text-muted-foreground">
                                    MP4, WebM ou QuickTime (Máx. 100MB)
                                 </p>
                              </div>
                           </>
                        )}
                     </div>
                  </div>
                  {errors.video && (
                     <p className="text-xs font-medium text-destructive mt-1 px-1">
                        {errors.video.message?.toString()}
                     </p>
                  )}
               </div>

               {/* Grid Linha 1: Idioma e Formato (2 Colunas, 100% largura) */}
               <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6 w-full">
                  {/* Idioma */}
                  <div className="space-y-2 w-full flex flex-col">
                     <Label className="text-sm sm:text-base font-medium text-left">
                        Idioma
                     </Label>
                     {/* CORREÇÃO 2: value={watch("language")} mantém o estado controlado e tipado */}
                     <Select
                        onValueChange={(v) => setValue("language", v || "")}
                        value={watch("language")}
                     >
                        <SelectTrigger
                           className={`w-full h-12 sm:h-10 ${errors.language ? "border-destructive" : ""}`}
                        >
                           <SelectValue placeholder="Selecione o idioma">
                              {labelsIdioma[watch("language")]}
                           </SelectValue>
                        </SelectTrigger>
                        <SelectContent>
                           <SelectItem value="pt">Português</SelectItem>
                           <SelectItem value="en">Inglês</SelectItem>
                           <SelectItem value="es">Espanhol</SelectItem>
                        </SelectContent>
                     </Select>
                  </div>

                  {/* Formato */}
                  <div className="space-y-2 w-full flex flex-col">
                     <Label className="text-sm sm:text-base font-medium text-left">
                        Formato
                     </Label>
                     <Select
                        onValueChange={(v) => setValue("format", v || "")}
                        value={watch("format")}
                     >
                        <SelectTrigger
                           className={`w-full h-12 sm:h-10 ${errors.format ? "border-destructive" : ""}`}
                        >
                           <SelectValue placeholder="Selecione o formato">
                              {labelsFormato[watch("format")]}
                           </SelectValue>
                        </SelectTrigger>
                        <SelectContent>
                           <SelectItem value="vertical">
                              Vertical (9:16)
                           </SelectItem>
                           <SelectItem value="horizontal">
                              Horizontal (16:9)
                           </SelectItem>
                        </SelectContent>
                     </Select>
                  </div>
               </div>

               {/* Grid Linha 2: Tamanho, Fundo e Cor (3 Colunas, 100% largura) */}
               <div className="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-6 w-full">
                  {/* Tamanho da Fonte */}
                  <div className="space-y-2 w-full flex flex-col">
                     <Label className="text-sm sm:text-base font-medium text-left">
                        Tamanho
                     </Label>
                     <Select
                        onValueChange={(v) => setValue("fontSize", v || "")}
                        value={watch("fontSize")}
                     >
                        <SelectTrigger
                           className={`w-full h-12 sm:h-10 ${errors.fontSize ? "border-destructive" : ""}`}
                        >
                           <SelectValue placeholder="Selecione o tamanho">
                              {labelsTamanho[watch("fontSize")]}
                           </SelectValue>
                        </SelectTrigger>
                        <SelectContent>
                           <SelectItem value="pequena">Pequena</SelectItem>
                           <SelectItem value="media">Média</SelectItem>
                           <SelectItem value="grande">Grande</SelectItem>
                        </SelectContent>
                     </Select>
                  </div>

                  {/* Fundo da Fonte (Toggle Personalizado Estilo Pílula) */}
                  <div className="space-y-2 w-full flex flex-col">
                     <Label className="text-sm sm:text-base font-medium text-left">
                        Fundo da Fonte
                     </Label>
                     <div className="flex w-full h-12 sm:h-10 bg-muted/80 p-1 rounded-full shadow-inner border border-border/40">
                        <button
                           type="button" // Essencial para não submeter o formulário
                           onClick={() => setValue("bgColor", "#000000")}
                           className={`flex-1 flex items-center justify-center text-sm font-semibold rounded-full transition-all duration-300 ${
                              selectedBg === "#000000"
                                 ? "bg-black text-white shadow-sm"
                                 : "text-muted-foreground hover:text-foreground"
                           }`}
                        >
                           Preto
                        </button>
                        <button
                           type="button"
                           onClick={() => setValue("bgColor", "#FFFFFF")}
                           className={`flex-1 flex items-center justify-center text-sm font-semibold rounded-full transition-all duration-300 ${
                              selectedBg === "#FFFFFF"
                                 ? "bg-white text-black shadow-sm"
                                 : "text-muted-foreground hover:text-foreground"
                           }`}
                        >
                           Branco
                        </button>
                     </div>
                  </div>

                  {/* Cor da Fonte */}
                  <div className="space-y-2 w-full flex flex-col">
                     <Label className="text-sm sm:text-base font-medium text-left">
                        Cor da Fonte
                     </Label>
                     <div className="flex gap-2 w-full">
                        {/* Seletor Visual */}
                        <div
                           className="w-12 h-12 sm:h-10 shrink-0 rounded-md border border-vega-border overflow-hidden relative shadow-sm hover:ring-2 hover:ring-primary/20 transition-all"
                           style={{ backgroundColor: selectedColor }}
                        >
                           <Input
                              type="color"
                              ref={colorInputRef} // Conectamos a referência aqui!
                              value={selectedColor}
                              onChange={(e) =>
                                 setValue(
                                    "fontColor",
                                    e.target.value.toUpperCase(),
                                 )
                              }
                              className="absolute inset-0 opacity-0 w-full h-full"
                           />
                        </div>

                        {/* Input de Texto Hex */}
                        <Input
                           type="text"
                           {...register("fontColor")}
                           value={selectedColor}
                           readOnly
                           placeholder="#FFFFFF"
                           onClick={() => colorInputRef.current?.click()} // O clique mágico aqui!
                           className="flex-1 h-12 sm:h-10 uppercase font-mono bg-muted/30 hover:bg-muted/50 transition-colors focus-visible:ring-0"
                        />
                     </div>
                  </div>
               </div>

               {/* Preview de Legenda (Mantido no final conforme solicitado antes) */}
               <div className="w-full bg-slate-900 rounded-xl overflow-hidden border border-vega-border relative aspect-video flex items-end justify-center pb-6 shadow-inner mt-2">
                  <div className="absolute top-2">
                     <span className="text-[10px] uppercase tracking-widest text-slate-400 font-bold">
                        Pré-visualização de Contraste
                     </span>
                  </div>
                  <div
                     className={`px-3 py-1 rounded-sm transition-all duration-200 font-bold tracking-wide shadow-lg ${sizeMap[selectedSize as keyof typeof sizeMap]}`}
                     style={{
                        backgroundColor:
                           selectedBg === "#000000"
                              ? "rgba(0, 0, 0, 0.85)"
                              : "rgba(255, 255, 255, 0.85)",
                        color: selectedColor,
                     }}
                  >
                     Exemplo de Legenda Automática
                  </div>
               </div>

               <Button
                  type="submit"
                  disabled={isPending}
                  className="w-full h-12 font-bold text-lg"
               >
                  {isPending ? "Enviando..." : "Gerar Vídeo Legendado"}
               </Button>
            </form>
         </CardContent>
      </Card>
   );
}
