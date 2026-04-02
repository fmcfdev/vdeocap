import axios from "axios";

export const api = axios.create({
   // URL do seu FastAPI que rodamos no passo anterior
   baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
   headers: {
      "Content-Type": "application/json",
   },
});
