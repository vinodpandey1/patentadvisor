/// Core Website config
export const companyConfig = {
  ////// Base config used mainly for layout (@/components/navbar/Navbar-1.tsx and @/components/footer/Footer-1.tsx)
  company: {
    name: "GenAI - Group 16",
    theme: "infotechtrends",
    homeUrl: "http://localhost:3000/",
    appUrl: "/",
    description: "AI Powered Patent Advisor",
    logo: "/logo.png",
    navbarLinks: [
      { label: "Home", href: "http://localhost:3000/" },
    ],
  },

  ////// UI config
  navbarLanding: {
    bgColor: "base-100",
    textColor: "base-content",
    buttonColor: "primary",
  },

  footerLanding: {
    bgColor: "base-200",
    textColor: "base-content",
  },
};

/// Core Website config
export const companyName = "Gen AI - Group 16";
export const defaultTitle =
  "AI Patent Advisor";
export const defaultDescription =
  "Design your patent PDF 10x faster using our AI Patent Advisor ";
export const defaultKeywords =
  "openai, gpt-3, llama, replicate, groq, mixtral, ai app, boilerplate, api endpoint, next.js, react, starter kit, boilerplate, ai, artificial intelligence, node.js, express, stripe";
export const defaultOgImage = "/og.png";
export const favicon = "/favicon.ico";

// LEGAL STUFF
export const privacyPolicyUrl = "http://localhost:3000/privacy";
export const tosUrl = "http://localhost:3000/terms";

// Auth
export const authImage = "/hero.webp";

// Inside routing
export const homePage = "/home";
const getRedirectUrl = () => {
  const baseUrl = process.env.PRODUCTION_URL || "http://localhost:3000";
  return `${baseUrl}/auth/confirm?next=/home`;
};

export const redirectTo = getRedirectUrl();
