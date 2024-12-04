"use client";

import React, { useState } from "react";
import PdfAppInfo from "@/components/pdf/PdfAppInfo";
import UploadDialog from "./UploadDialog";
import UploadAndTriggerDialog from "@/components/pdf/UploadAndTriggerDialog"; // New Component
import YourFiles from "./YourFiles";
import SearchPatentFiles from "./SearchPatentFiles"; // New component
import { useRouter } from "next/navigation";
import Login from "@/components/input/login";
import Sidebar from "@/components/ui/sidebar"; // Ensure correct casing
import { cn } from "@/lib/utils";

interface InputCaptureProps {
  userEmail?: string;
  documents?: DocumentType[];
  credits?: number;
}

interface DocumentType {
  id: string;
  file_name: string;
  created_at: string;
  size?: number;
  pdf_summary: string;
  classification: string;
  patent_id: string;
  patent_title: string;
  audio_url: string;
  podcast_url: string;
}

const sidebarOptions = [
  "My Patents",
  "Search Patent",
  "Upload Patent",
  "Upload & Trigger Pipeline" // New Sidebar Option
  // Add more options as needed
];

export default function PdfLayout({
  userEmail,
  documents,
  credits,
}: InputCaptureProps) {
  const [fileUrl, setFileUrl] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [response, setResponse] = useState<any>(null);
  const [status, setStatus] = useState<string>("Idle");
  const router = useRouter();

  // Sidebar state
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(true);
  const [selectedOption, setSelectedOption] = useState<string>("My Patents");

  const handleUpload = async (url: string | null, id: string | null) => {
    setStatus("Adding document...");
    setFileUrl(url);
    setDocumentId(id);
    if (url) {
      setStatus("Generating embeddings...");

      const res = await fetch("/api/pdf/vectorize", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          fileUrl: url,
          documentId: id,
        }),
      });

      const data = await res.json();
      setResponse(data);

      if (data?.id) {
        router.push(`/pdf/document/${data.id}`);
      } else {
        setStatus("Failed to generate embeddings.");
      }

      setStatus("Idle");
    } else {
      setFileName(null);
    }
  };

  const handleUrlSubmit = async () => {
    if (!fileUrl || !fileName) {
      alert("File URL and name are required.");
      return;
    }

    setStatus("Adding document...");

    const addDocumentResponse = await fetch("/api/pdf/externaldoc", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url: fileUrl, fileName }),
    });

    const addDocumentData = await addDocumentResponse.json();

    if (addDocumentData.error) {
      setStatus("Failed to add document.");
      setResponse(addDocumentData);
      return;
    }

    setDocumentId(addDocumentData.documentId);
    setFileUrl(addDocumentData.url);
    setStatus("Generating embeddings...");

    const res = await fetch("/api/pdf/vectorize", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        fileUrl: addDocumentData.url,
        fileName,
        documentId: addDocumentData.documentId,
      }),
    });

    const data = await res.json();
    setResponse(data);

    if (data?.id) {
      router.push(`/pdf/document/${data.id}`);
    } else {
      setStatus("Failed to generate embeddings.");
    }

    setStatus("Idle");
  };

  // Handle sidebar option selection
  const handleSelectOption = (option: string) => {
    setSelectedOption(option);
    // Optionally close the sidebar on mobile or based on preference
    // setIsSidebarOpen(false);
  };

  // Render content based on selected sidebar option
  const renderContent = () => {
    if (!userEmail) {
      return <Login />;
    }

    switch (selectedOption) {
      case "Upload Patent":
        return (
          <>
            <div className="mt-4 flex justify-center">
              <UploadDialog
                fileUrl={fileUrl}
                fileName={fileName}
                setFileUrl={setFileUrl}
                setFileName={setFileName}
                handleUpload={handleUpload}
                handleUrlSubmit={handleUrlSubmit}
                status={status}
                response={response}
              />
            </div>
            {/*{documents && documents.length > 0 && (
              <YourFiles documents={documents} />
            )}*/}
          </>
        );
      case "Upload & Trigger Pipeline":
        return (
          <>
            <div className="mt-4 flex justify-center">
              <UploadAndTriggerDialog />
            </div>
            {/* Add any additional components or information if needed */}
          </>
        );
      case "My Patents":
        return documents && documents.length > 0 ? (
          <YourFiles documents={documents} />
        ) : (
          <p className="text-center mt-4">No documents uploaded.</p>
        );      
      case "Search Patent":
        return <SearchPatentFiles />;
      // Add more cases as needed
      default:
        return <p>Select an option from the sidebar.</p>;
    }
  };

  return (
    <section className="relative min-h-screen flex">
      {/* Sidebar */}
      <Sidebar
        isOpen={isSidebarOpen}
        onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
        onSelect={handleSelectOption}
        options={sidebarOptions}
        selectedOption={selectedOption}
      />

      {/* Main Content */}
      <div
        className={cn(
          "flex-1 flex flex-col transition-all duration-300",
          isSidebarOpen ? "ml-16" : "ml-8"
        )}
      >
        {/* Optionally, add a top bar or other elements here */}
        <main className="flex-1 p-8 overflow-auto">
          {renderContent()}
        </main>
        {/* Footer can remain unchanged */}
      </div>
    </section>
  );
}
