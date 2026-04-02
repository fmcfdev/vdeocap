import { UploadForm } from "@/components/dashboard/UploadForm";

export default function HomePage() {
   return (
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-80px)] p-6">
         <div className="w-full max-w-4xl space-y-8 text-center">
            <div className="space-y-2">
               <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl">
                  Legendas Inteligentes com IA
               </h1>
               <p className="text-xl text-muted-foreground">
                  Transcreva, traduza e estilize seus vídeos em segundos.
               </p>
            </div>

            {/* Nosso Componente de Upload que criamos antes */}
            <UploadForm />
         </div>
      </div>
   );
}
