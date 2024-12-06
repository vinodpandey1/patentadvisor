"use client";

import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { UploadCloudIcon } from "lucide-react";
import Check from "@/components/alerts/Check";

const UploadAndTriggerDialog: React.FC = () => {
  const [isMounted, setIsMounted] = useState<boolean>(false);
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [file, setFile] = useState<File | null>(null);
  const [fileName, setFileName] = useState<string>(""); // For displaying purposes
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [isTriggering, setIsTriggering] = useState<boolean>(false);
  const [triggerMessage, setTriggerMessage] = useState<string | null>(null);
  const [triggerError, setTriggerError] = useState<string | null>(null);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) return null;

  // Handle file selection with client-side validation
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files && e.target.files[0];
    if (selectedFile) {
      // Validate file type
      if (selectedFile.type !== "application/pdf") {
        alert("Only PDF files are allowed.");
        return;
      }

      // Validate file size (e.g., max 10MB)
      const maxSizeMB = 10;
      const fileSizeMB = selectedFile.size / (1024 * 1024);
      if (fileSizeMB > maxSizeMB) {
        alert(`File size exceeds the maximum limit of ${maxSizeMB} MB.`);
        return;
      }

      setFile(selectedFile);
      setFileName(selectedFile.name);
    }
  };

  // Handle upload to 'upload' directory
  const handleUploadToCloudflare = async (): Promise<{ patentId: string; fileUrl: string }> => {
    if (!file) throw new Error("No file selected.");

    const uploadApiUrl = "/api/pdf/uploadToUploadDirectory"; // Existing API route

    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(uploadApiUrl, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(`Cloudflare Upload Error: ${errorData.error}`);
    }

    const data = await response.json();
    return { patentId: data.patentId, fileUrl: data.url };
  };

  // Handle trigger pipeline via the updated API route
  const handleTriggerPipeline = async (patentId: string) => {
    const triggerApiUrl = `/api/pdf/triggerPipeline`;

    const res = await fetch(triggerApiUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ patentId }),
    });

    if (res.status === 200) {
      setTriggerMessage("Pipeline triggered successfully.");
    } else {
      // Capture the error message from the API
      const errorData = await res.json();
      setTriggerError(`Pipeline API Error: ${errorData.error || res.statusText}`);
    }
  };

  // Handle the entire process
  const handleProcess = async () => {
    if (!file) {
      alert("Please select a file to upload.");
      return;
    }

    setIsUploading(true);
    setTriggerMessage(null);
    setTriggerError(null);

    try {
      // Upload to Cloudflare
      const { patentId } = await handleUploadToCloudflare();
      setIsUploading(false);

      // Trigger the pipeline
      setIsTriggering(true);
      await handleTriggerPipeline(patentId);
      setIsTriggering(false);

      if (!triggerError) {
        setIsOpen(false); // Close the dialog on success
      }
    } catch (error: any) {
      console.error(error);
      setIsUploading(false);
      setIsTriggering(false);
      setTriggerError(error.message || "An unexpected error occurred.");
    }
  };

  return (
    <Dialog
      open={isOpen}
      onOpenChange={(open) => {
        if (!isUploading && !isTriggering) setIsOpen(open);
      }}
    >
      <DialogTrigger asChild>
        <Button
          variant="outline"
          className="bg-primary hover:bg-primary/80 text-white"
        >
          <UploadCloudIcon className="w-4 h-4 mr-2" />
          Upload & Trigger Pipeline
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Upload Patent PDF & Trigger Pipeline</DialogTitle>
          <DialogDescription>
            Upload a Patent PDF file to Cloudflare and trigger the processing pipeline.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="flex items-center">
            <Label htmlFor="file-upload" className="mr-4">
              Select PDF:
            </Label>
            <Input
              type="file"
              id="file-upload"
              accept=".pdf"
              onChange={handleFileChange}
            />
          </div>
          {fileName && (
            <p className="text-sm text-gray-700">Selected File: {fileName}</p>
          )}
        </div>
        {(isUploading || isTriggering) && (
          <div className="flex flex-col items-center justify-center py-4">
            <span className="loading loading-ring loading-lg"></span>
            <p className="mt-4 text-sm text-black">
              {isUploading
                ? "Uploading, please wait..."
                : "Triggering pipeline..."}
            </p>
          </div>
        )}
        {triggerMessage && <Check>{triggerMessage}</Check>}
        {triggerError && (
          <p className="mt-2 text-red-600">{triggerError}</p>
        )}
        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            onClick={handleProcess}
            disabled={isUploading || isTriggering}
            className="bg-blue-500 hover:bg-blue-600 text-white"
          >
            {isUploading
              ? "Uploading..."
              : isTriggering
              ? "Triggering..."
              : "Upload & Trigger"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default UploadAndTriggerDialog;
