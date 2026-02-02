import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}


export const formatBreadCrumb = (segment) => {
  const map = {
    about: "من نحن",
    booking: "الحجز",
    contact: "تواصل معنا",
    "why-grm": "لماذا قوم",
  };

  if (map[segment]) return map[segment];

  return segment
    .replace(/-/g, " ")
    .replace(/\b\w/g, (l) => l.toUpperCase());
};
