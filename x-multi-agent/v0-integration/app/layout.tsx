import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Pzhisen Agent Console",
  description: "tok.mom chat proxy + X posting for Pzhisen",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body style={{ margin: 0, background: "#f6f4ef", color: "#111" }}>
        {children}
      </body>
    </html>
  );
}
