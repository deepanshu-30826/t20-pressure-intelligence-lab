import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "T20 Pressure Intelligence Lab | Elite Cricket Analytics Terminal",
  description: "Official Rajasthan Royals SupeRR Selector Analytics Suite • Context-Only Structural Pressure Engine",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      </head>
      <body className="bg-[#060A13] text-[#F1F5F9] min-h-screen antialiased bg-ambient selection:bg-[#3B82F6] selection:text-white">
        {children}
      </body>
    </html>
  );
}
