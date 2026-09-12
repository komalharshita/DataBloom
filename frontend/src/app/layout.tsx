import type { Metadata } from "next";
import { Bodoni_Moda, DM_Sans } from "next/font/google";
import "./globals.css";
import CustomCursor from "../components/CustomCursor";
import LenisProvider from "../components/LenisProvider";

const bodyFont = DM_Sans({
  variable: "--font-body",
  weight: ["400", "500", "600", "700"],
  subsets: ["latin"],
});

const headingFont = Bodoni_Moda({
  variable: "--font-heading",
  weight: ["600", "700"],
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "DataBloom | Turn data into a story",
  description: "Upload data, ask a question, and discover the story inside your numbers.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${bodyFont.variable} ${headingFont.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col"><LenisProvider><CustomCursor />{children}</LenisProvider></body>
    </html>
  );
}
