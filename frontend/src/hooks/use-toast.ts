
import { useToast as useToastOriginal, toast as toastOriginal } from "@/components/ui/use-toast";

export const useToast = useToastOriginal;
export const toast = toastOriginal;

export type { ToastProps, ToastActionElement } from "@/components/ui/toast";
