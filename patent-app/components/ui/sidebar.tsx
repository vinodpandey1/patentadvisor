// components/ui/Sidebar.tsx
"use client";

import * as React from "react";
import * as CollapsiblePrimitive from "@radix-ui/react-collapsible";
import { cn } from "@/lib/utils";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  onSelect: (option: string) => void;
  options: string[];
  selectedOption: string;
}

const Sidebar = React.forwardRef<HTMLDivElement, SidebarProps>(
  ({ isOpen, onToggle, onSelect, options, selectedOption }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "flex flex-col bg-gray-800 text-white w-64 transition-transform duration-300",
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <h2 className="text-lg font-semibold">Menu</h2>
          <button
            onClick={onToggle}
            className="p-2 rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-white"
          >
            {isOpen ? <ChevronLeft size={20} /> : <ChevronRight size={20} />}
          </button>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          {options.map((option) => (
            <button
              key={option}
              onClick={() => onSelect(option)}
              className={cn(
                "w-full text-left px-3 py-2 rounded-md hover:bg-gray-700",
                option === selectedOption && "bg-gray-700"
              )}
            >
              {option}
            </button>
          ))}
        </nav>
      </div>
    );
  }
);
Sidebar.displayName = "Sidebar";

export default Sidebar;
