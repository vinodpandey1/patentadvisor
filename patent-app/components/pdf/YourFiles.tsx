// components/pdf/YourFiles.tsx
import React, { useState } from "react";
import { formatDistanceToNow } from "date-fns";
import { Button } from "@/components/ui/button";
import { TrashIcon, ClipboardCopyIcon, BookOpenIcon, Volume2Icon } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";

import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";

interface YourFilesProps {
  documents: DocumentType[];
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

const YourFiles: React.FC<YourFilesProps> = ({ documents }) => {
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [selectedDoc, setSelectedDoc] = useState<DocumentType | null>(null);
  const itemsPerPage = 5;

  const sortedDocuments = [...documents].sort(
    (a, b) =>
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  const totalPages = Math.ceil(sortedDocuments.length / itemsPerPage);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const currentDocuments = sortedDocuments.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const handleDelete = async (documentId: string) => {
    const res = await fetch("/api/pdf/delete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ documentId }),
    });
    if (res.ok) {
      // Refresh the documents list or handle the UI update
      setSelectedDoc(null);
      // Assuming you have a way to refresh the documents list, e.g., refetching from the server
      window.location.reload();
    }
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    alert("Copied to clipboard!");
  };

  return (
    <div>
      <div className="space-y-1 mb-4 mt-4">
        <h4 className="text-sm font-medium leading-none">Your files</h4>
        <p className="text-sm text-muted-foreground">
          You can view and delete your uploaded files here.
        </p>
      </div>

      {documents && (
        <div className="overflow-x-auto w-full">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>File Name</TableHead>
                <TableHead className="text-center">Uploaded</TableHead>
                {/* Removed Size Column */}
                <TableHead className="text-center">Title</TableHead>
                <TableHead className="text-center">Summary</TableHead>
                <TableHead className="text-center">Summary Audio</TableHead>
                <TableHead className="text-center">Podcast Audio</TableHead>                
                {/*<TableHead>Actions</TableHead>*/}
              </TableRow>
            </TableHeader>
            <TableBody>
              {currentDocuments.map((doc: DocumentType) => (
                <TableRow key={doc.id}>
                  <TableCell>
                    <a
                      href={`/pdf/document/${doc.id}`}
                      className="text-primary hover:underline"
                    >
                      {doc.file_name}
                    </a>
                  </TableCell>
                  <TableCell className="text-center text-sm text-gray-500">
                    {formatDistanceToNow(new Date(doc.created_at))} ago
                  </TableCell>
                  <TableCell className="text-center text-sm text-gray-500">
                    {doc.patent_title}
                  </TableCell>
                  <TableCell className="text-center">
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button
                          variant="ghost"
                          className="p-2 hover:bg-gray-700"
                          onClick={() => setSelectedDoc(doc)}
                          aria-label="View Summary"
                        >
                          <BookOpenIcon className="w-4 h-4" />
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogTitle>Summary</DialogTitle>
                        <DialogDescription>
                          <p className="mb-4">{doc.pdf_summary}</p>
                          <Button
                            variant="outline"
                            onClick={() => handleCopy(doc.pdf_summary)}
                            className="flex items-center space-x-2"
                          >
                            <ClipboardCopyIcon className="w-4 h-4" />
                            <span>Copy Summary</span>
                          </Button>
                        </DialogDescription>
                        <DialogFooter>
                          <Button onClick={() => setSelectedDoc(null)} className="bg-[oklch(0.8_0.15_200.66)] text-white hover:bg-[oklch(0.7_0.15_200.66)]">Close</Button>
                        </DialogFooter>
                      </DialogContent>
                    </Dialog>
                  </TableCell>                  
                  <TableCell className="text-center">
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button
                          variant="ghost"
                          className="p-2 hover:bg-gray-700"
                          onClick={() => setSelectedDoc(doc)}
                          aria-label="Audio Summary"
                        >
                          <Volume2Icon className="w-4 h-4" />
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogTitle>Audio Summary</DialogTitle>
                        <DialogDescription>
                          <audio controls className="w-full">
                            <source src={doc.audio_url} type="audio/mpeg" />
                            Your browser does not support the audio element.
                          </audio>
                        </DialogDescription>
                        <DialogFooter>
                          <Button onClick={() => setSelectedDoc(null)} className="bg-[oklch(0.8_0.15_200.66)] text-white hover:bg-[oklch(0.7_0.15_200.66)]">Close</Button>
                        </DialogFooter>
                      </DialogContent>
                    </Dialog>
                  </TableCell>
                  <TableCell className="text-center">
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button
                          variant="ghost"
                          className="p-2 hover:bg-gray-700"
                          onClick={() => setSelectedDoc(doc)}
                          aria-label="Podcast Audio"
                        >
                          <Volume2Icon className="w-4 h-4" />
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogTitle>Podcast Audio</DialogTitle>
                        <DialogDescription>
                          <audio controls className="w-full">
                            <source src={doc.podcast_url} type="audio/mpeg" />
                            Your browser does not support the audio element.
                          </audio>
                        </DialogDescription>
                        <DialogFooter>
                          <Button onClick={() => setSelectedDoc(null)} className="bg-[oklch(0.8_0.15_200.66)] text-white hover:bg-[oklch(0.7_0.15_200.66)]">Close</Button>
                        </DialogFooter>
                      </DialogContent>
                    </Dialog>
                  </TableCell>
                  {/*<TableCell>
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button
                          className="hover:bg-primary/80 hover:text-white flex items-center space-x-1"
                          variant="ghost"
                          color="red"
                          onClick={() => setSelectedDoc(doc)}
                          aria-label="Delete Document"
                        >
                          <TrashIcon className="w-4 h-4" />
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogTitle>Confirm deletion</DialogTitle>
                        <DialogDescription>
                          Are you sure you want to delete this document? This
                          action cannot be undone.
                        </DialogDescription>
                        <DialogFooter>
                          <Button
                            className="bg-red-500 text-white hover:bg-red-400"
                            onClick={() => handleDelete(selectedDoc!.id)}
                          >
                            Delete
                          </Button>
                        </DialogFooter>
                      </DialogContent>
                    </Dialog>
                  </TableCell>*/}
                </TableRow>
              ))}
            </TableBody>
          </Table>

          <Pagination>
            <PaginationContent>
              <PaginationItem>
                <PaginationPrevious
                  href="#"
                  className="hover:bg-primary/80 hover:text-white"
                  onClick={() => handlePageChange(Math.max(1, currentPage - 1))}
                />
              </PaginationItem>
              {Array.from({ length: totalPages }, (_, i) => (
                <PaginationItem key={i}>
                  <PaginationLink
                    href="#"
                    className="hover:bg-primary/80 hover:text-white"
                    onClick={() => handlePageChange(i + 1)}
                    isActive={i + 1 === currentPage}
                  >
                    {i + 1}
                  </PaginationLink>
                </PaginationItem>
              ))}
              <PaginationItem>
                <PaginationNext
                  href="#"
                  className="hover:bg-primary/80 hover:text-white"
                  onClick={() =>
                    handlePageChange(Math.min(totalPages, currentPage + 1))
                  }
                />
              </PaginationItem>
            </PaginationContent>
          </Pagination>
        </div>
      )}
    </div>
  );
};

export default YourFiles;
