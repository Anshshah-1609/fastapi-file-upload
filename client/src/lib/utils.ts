import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export const cn = (...inputs: ClassValue[]) => {
  return twMerge(clsx(inputs));
};

export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
};

export const formatTime = (seconds: string): string => {
  const numSeconds = parseFloat(seconds);
  if (numSeconds < 1) {
    return `${Math.round(numSeconds * 1000)}ms`;
  } else if (numSeconds < 60) {
    return `${numSeconds.toFixed(2)}s`;
  } else {
    const minutes = Math.floor(numSeconds / 60);
    const secs = (numSeconds % 60).toFixed(2);
    return `${minutes}m ${secs}s`;
  }
};
