// Please read the @/lib/types/toolconfig file for more details on each field.
import { ToolConfig } from "@/lib/types/toolconfig";

export const toolConfig: ToolConfig = {
  ////// Base config
  company: {
    name: "AI Patent Advisor",
    theme: "infotechtrends",
    homeUrl: "/apps/pdf",
    appUrl: "/apps/pdf",
    description:
      "Design your patent PDF 10x faster using our AI Patent Advisor",
    logo: "https://cdn3.iconfinder.com/data/icons/aami-web-internet/64/aami4-68-512.png",
    navbarLinks: [
      { label: "App", href: `/apps/pdf` },
      { label: "Home", href: "/" },
    ],
  },

  ////// SEO stuff
  metadata: {
    title: "AI Patent Advisor",
    description:
      "Design your patent PDF 10x faster using our AI Patent Advisor",
    og_image: "http://localhost:3000/og.png",
    canonical: "http://localhost:3000/apps/pdf",
  },

  ////// Paywall
  paywall: true,
  credits: 5,

  ////// Location
  toolPath: "(apps)/pdf",

  ////// AI config
  aiModel: "gpt-4o",
  messagesToInclude: 10,

  ////// UI config
  navbarLanding: {
    bgColor: "base-100",
    textColor: "base-content",
    buttonColor: "primary",
  },

  navbarApp: {
    bgColor: "white",
    textColor: "base-content",
    buttonColor: "primary",
  },

  footerApp: {
    bgColor: "primary/80",
    textColor: "white",
  },
};
