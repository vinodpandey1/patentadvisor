import { DashboardLayout } from "@/components/dashboard/Layout";
import { toolConfig } from "./toolConfig";
import Navbar from "@/components/navbars/Navbar-1";


export const metadata = {
  title: toolConfig.metadata.title,
  description: toolConfig.metadata.description,
  openGraph: {
    images: [toolConfig.metadata.og_image],
  },
  alternates: {
    canonical: toolConfig.metadata.canonical,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return( 
  <>
  <Navbar
          companyConfig={toolConfig.company!}
          navbarConfig={toolConfig.navbarLanding!}
  />
  <DashboardLayout toolConfig={toolConfig}>{children}</DashboardLayout>
  </>);
}
