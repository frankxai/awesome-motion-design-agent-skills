import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "Motion lab | Awesome Motion Design Agent Skills",
  description: "Try interruptible interface motion, a GSAP sequence, and an editable Remotion video. Every example includes its source.",
  robots: { index: false, follow: true },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
