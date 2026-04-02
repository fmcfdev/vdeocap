export interface VideoStatusResponse {
   task_id: string;
   status: "pending" | "processing" | "completed" | "failed";
   message: string;
   progress: number;
   output_url?: string;
   error?: string;
}
