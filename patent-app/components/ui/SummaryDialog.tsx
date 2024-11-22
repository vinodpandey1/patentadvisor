// components/ui/SummaryDialog.tsx
import React from "react";
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ClipboardCopyIcon } from "lucide-react";

interface SummaryDialogProps {
  summary: string;
  onClose: () => void;
}

const SummaryDialog: React.FC<SummaryDialogProps> = ({ summary, onClose }) => {
  const handleCopy = () => {
    navigator.clipboard.writeText(summary);
    alert("Summary copied to clipboard!");
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent>
        <DialogTitle>Summary</DialogTitle>
        <DialogDescription>
          <p className="mb-4">{summary}</p>
          <Button
            variant="outline"
            onClick={handleCopy}
            className="flex items-center space-x-2 bg-[oklch(0.8_0.15_200.66)] text-white hover:bg-[oklch(0.7_0.15_200.66)]"
          >
            <ClipboardCopyIcon className="w-4 h-4" />
            <span>Copy Summary</span>
          </Button>
        </DialogDescription>
        <DialogFooter>
          <Button onClick={onClose}>Close</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default SummaryDialog;
