import "./globals.css";

export const metadata = {
  title: "Email Assistant",
  description: "Triage your inbox and draft replies in your voice — you approve every send.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
