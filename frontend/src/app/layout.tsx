import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "SmartWaste — AI Waste Segregation",
  description: "AI-powered waste segregation for a cleaner tomorrow.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-surface-900 text-slate-100 antialiased`}>
        {children}
      </body>
    </html>
  );
}
