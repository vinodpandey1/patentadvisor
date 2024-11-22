// components/ui/ClassificationDialog.tsx
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

interface ClassificationDialogProps {
  classification: string;
  onClose: () => void;
}

const ClassificationDialog: React.FC<ClassificationDialogProps> = ({ classification, onClose }) => {
  const handleCopy = () => {
    navigator.clipboard.writeText(classification);
    alert("Classification copied to clipboard!");
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent>
        <DialogTitle>Classification</DialogTitle>
        <DialogDescription>
          <p className="mb-4">{classification}</p>
          <Button
            variant="outline"
            onClick={handleCopy}
            className="flex items-center space-x-2"
          >
            <ClipboardCopyIcon className="w-4 h-4" />
            <span>Copy Classification</span>
          </Button>
        </DialogDescription>
        <DialogFooter>
          <Button onClick={onClose}>Close</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default ClassificationDialog;
