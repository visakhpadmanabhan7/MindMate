"use client";

import { useState, useEffect, useCallback, createContext, useContext } from "react";
import { X, CheckCircle2, AlertCircle, Info } from "lucide-react";

type ToastType = "success" | "error" | "info";

interface Toast {
  id: number;
  message: string;
  type: ToastType;
}

interface ToastContextType {
  toast: (message: string, type?: ToastType) => void;
}

const ToastContext = createContext<ToastContextType>({ toast: () => {} });

export function useToast() {
  return useContext(ToastContext);
}

let nextId = 0;

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((message: string, type: ToastType = "success") => {
    const id = nextId++;
    setToasts((prev) => [...prev, { id, message, type }]);
  }, []);

  const removeToast = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ toast: addToast }}>
      {children}
      <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 max-w-sm">
        {toasts.map((t) => (
          <ToastItem key={t.id} toast={t} onDismiss={() => removeToast(t.id)} />
        ))}
      </div>
    </ToastContext.Provider>
  );
}

function ToastItem({ toast, onDismiss }: { toast: Toast; onDismiss: () => void }) {
  useEffect(() => {
    const timer = setTimeout(onDismiss, 4000);
    return () => clearTimeout(timer);
  }, [onDismiss]);

  const Icon = toast.type === "success" ? CheckCircle2 : toast.type === "error" ? AlertCircle : Info;
  const colors = {
    success: "border-green-500/30 bg-green-500/10 text-green-700 dark:text-green-400",
    error: "border-destructive/30 bg-destructive/10 text-destructive",
    info: "border-primary/30 bg-primary/10 text-primary",
  };

  return (
    <div
      className={`flex items-start gap-3 rounded-xl border px-4 py-3 shadow-lg backdrop-blur-sm animate-in slide-in-from-right-5 fade-in-0 ${colors[toast.type]}`}
    >
      <Icon className="h-4 w-4 mt-0.5 shrink-0" />
      <p className="text-sm flex-1">{toast.message}</p>
      <button onClick={onDismiss} className="shrink-0 opacity-60 hover:opacity-100">
        <X className="h-3.5 w-3.5" />
      </button>
    </div>
  );
}
