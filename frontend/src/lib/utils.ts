import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const MOOD_COLORS: Record<string, string> = {
  happy: "oklch(0.65 0.17 145)",
  grateful: "oklch(0.65 0.17 145)",
  hopeful: "oklch(0.62 0.10 170)",
  calm: "oklch(0.60 0.12 185)",
  tired: "oklch(0.58 0.06 250)",
  stressed: "oklch(0.68 0.14 85)",
  numb: "oklch(0.55 0.04 80)",
  sad: "oklch(0.55 0.15 255)",
  lonely: "oklch(0.50 0.12 270)",
  anxious: "oklch(0.72 0.16 85)",
  angry: "oklch(0.55 0.22 25)",
  overwhelmed: "oklch(0.60 0.18 35)",
  neutral: "oklch(0.55 0.08 155)",
};

export function getMoodColor(mood: string): string {
  return MOOD_COLORS[mood] ?? "oklch(0.55 0.08 155)";
}
