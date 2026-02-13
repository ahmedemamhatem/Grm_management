import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}


export const formatBreadCrumb = (segment) => {
  const map = {
    about: "من نحن",
    packages: "المساحات",
    contact: "تواصل معنا",
    "why-grm": "لماذا قرم",
    clients: "العملاء",
    profile: "الصفحة الشخصية",
    
  };

  if (map[segment]) return map[segment];

  return decodeURIComponent(segment);
};


export const convertEnToAr = (number) => {
  const enToArMap = {
    0: "٠",
    1: "١",
    2: "٢",
    3: "٣",
    4: "٤",
    5: "٥",
    6: "٦",
    7: "٧",
    8: "٨",
    9: "٩",
  };

  return number.toString().replace(/[0-9]/g, (match) => enToArMap[match]);
};
