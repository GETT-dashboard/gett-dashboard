import { Inter } from "next/font/google";
import "./globals.css";

import { Suspense } from 'react'

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "GETT Dashboard",
  description: "Gender Equality Tracking Tool",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={inter.className}>
          <Suspense>
            {children}
          </Suspense>
          </body>
    </html>
  );
}
