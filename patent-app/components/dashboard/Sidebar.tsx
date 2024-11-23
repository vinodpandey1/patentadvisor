"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import React, { useState, useCallback } from "react";
import { twMerge } from "tailwind-merge";
import { Heading } from "./Heading";
import { Badge } from "./Badge";
import { IconLayoutSidebarRightCollapse } from "@tabler/icons-react";
import { isMobile } from "@/lib/utils";
import {
  IconMicrophone,
  IconFileText,
  IconMessage,
  IconPhoto,
  IconEye,
  IconBolt,
  IconMessage2,
  IconRobot,
  IconCurrencyDollar,
  IconPencil,
  IconLogout,
  IconChevronRight,
  IconLogin,
  IconHome,
} from "@tabler/icons-react";
import { User } from "@supabase/supabase-js";

type Navlink = {
  href: string;
  label: string;
  icon?: React.ReactNode | any;
  isExternal?: boolean;
};

const Navigation = React.memo(
  ({
    setOpen,
    user,
  }: {
    setOpen: React.Dispatch<React.SetStateAction<boolean>>;
    user: User | null;
  }) => {
    const pathname = usePathname();

    const isActive = useCallback(
      (href: string) => pathname === href,
      [pathname]
    );

    const otherLinks = [
      { href: "/", label: "Home", icon: IconHome },
      {
        href: "http://localhost:3000",
        label: "Documentation",
        icon: IconFileText,
      },
      {
        href: "http://localhost:3000/affiliates",
        label: "Affiliates Program",
        icon: IconCurrencyDollar,
      },
      {
        href: "http://localhost:3000/blog",
        label: "Blog",
        icon: IconPencil,
      },
      user
        ? { href: "/api/auth/signout", label: "Logout", icon: IconLogout }
        : { href: "/auth", label: "Login", icon: IconLogin },
    ];

    const renderLinks = useCallback(
      (links: Navlink[], heading: string, defaultExternal: boolean = false) => (
        <>
          <Heading as="p" className="text-sm md:text-sm lg:text-sm px-2 pt-4">
            {heading}
          </Heading>
          {links.map((link: Navlink) => {
            const isExternal = link.isExternal ?? defaultExternal;
            return (
              <Link
                key={link.href}
                href={link.href}
                prefetch={!isExternal}
                target={isExternal ? "_blank" : undefined}
                rel={isExternal ? "noopener noreferrer" : undefined}
                onClick={(e) => {
                  if (link.label === "Logout") {
                    e.preventDefault();
                    fetch(link.href, { method: "POST" }).then(() => {
                      window.location.href = "/auth";
                    });
                  } else if (isMobile()) {
                    setOpen(false);
                  }
                }}
                className={twMerge(
                  "text-primary hover:text-primary/50 transition duration-200 flex items-center space-x-2 py-2 px-2 rounded-md text-sm",
                  isActive(link.href) && "bg-white shadow-lg text-primary"
                )}
              >
                <link.icon
                  className={twMerge(
                    "h-4 w-4 flex-shrink-0",
                    isActive(link.href) && "text-sky-500"
                  )}
                />
                <span>{link.label}</span>
              </Link>
            );
          })}
        </>
      ),
      [isActive, setOpen, user]
    );

    return (
      <div className="flex flex-col space-y-1 my-10 relative z-40">
        {/*{renderLinks(navlinks, "Demo apps")}
        {renderLinks(landingPages, "Landing pages", true)}
        {renderLinks(freeTools, "Free tools", true)}
        {renderLinks(otherLinks, "Other", true)}*/}
      </div>
    );
  }
);

Navigation.displayName = "Navigation";

/*const SidebarHeader = React.memo(() => (
  <div className="flex space-x-2">
    <Link className="text-md text-black flex items-center" href="/">
      <Image
        src="/logo-text.png"
        alt="Logo"
        width={400}
        height={100}
        quality={100}
        className="w-48"
      />
    </Link>
  </div>
));*/

//SidebarHeader.displayName = "SidebarHeader";

export const Sidebar = ({ user }: { user: User | null }) => {
  const [open, setOpen] = useState(!isMobile());

  const handleSetOpen = useCallback(
    (value: boolean | ((prevState: boolean) => boolean)) => {
      setOpen(value);
    },
    []
  );

  return (
    <>
      <div
        className={`lg:block ${
          open ? "block" : "hidden"
        } transition-all duration-300 ease-in-out`}
      >
       {/*} <div className="px-6 z-40 py-10 bg-neutral-100 max-w-[14rem] lg:w-fit fixed lg:relative h-screen left-0 flex flex-col justify-between">
          <div className="flex-1 overflow-auto no-scrollbar pb-4">
            
            <Navigation setOpen={handleSetOpen} user={user} />
          </div>
          
        </div>*/}
      </div>
      <button
        className="fixed lg:hidden bottom-4 right-4 h-8 w-8 border border-neutral-200 rounded-full backdrop-blur-sm flex items-center justify-center z-40"
        onClick={() => setOpen(!open)}
      >
        <IconLayoutSidebarRightCollapse className="h-4 w-4 text-primary" />
      </button>
    </>
  );
};
