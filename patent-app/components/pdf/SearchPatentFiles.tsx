// components/pdf/SearchPatentFiles.tsx

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
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
import { Input } from "@/components/ui/input";
import { SearchIcon, ClipboardCopyIcon, BookOpenIcon, Volume2Icon } from "lucide-react";
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { TriggerConfig } from "react-hook-form";

interface SearchPatentFilesProps {}

interface DocumentType {
  id: string;
  file_name: string;
  created_at: string;
  summary: string;
  classification: string;
  title: string;
  domain: string;
  sector: string;
  industry: string;
  grantdate: string;
  patentnumber: string;
  applicationarea: string;
  assignees: string;
  documentId: string;
  podcast_url: string;
  audio_url: string;
  abstract: string;
  // Add other fields if necessary
}

const SearchPatentFiles: React.FC<SearchPatentFilesProps> = () => {
  const [searchText, setSearchText] = useState<string>("");
  const [searchResults, setSearchResults] = useState<DocumentType[]>([]);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [selectedDoc, setSelectedDoc] = useState<DocumentType | null>(null);
  const itemsPerPage = 5;
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const totalPages = Math.ceil(searchResults.length / itemsPerPage);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const currentDocuments = searchResults.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const handleSearch = async () => {
    if (!searchText.trim()) {
      alert("Please enter text to search.");
      return;
    }

    setIsLoading(true);
    setSearchResults([]);
    setCurrentPage(1);

    try {
      const res = await fetch("/api/pdf/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: searchText }),
        credentials: "include", // Ensure cookies are sent
      });

      if (res.ok) {
        const data = await res.json();
        if (data.results && Array.isArray(data.results)) {
          setSearchResults(data.results);
        } else {
          console.error("Unexpected response structure:", data);
          alert("Unexpected response format from search API.");
        }
      } else {
        const errorData = await res.json();
        alert(`Failed to fetch search results: ${errorData.error}`);
      }
    } catch (error) {
      console.error("Error searching patents:", error);
      alert("An error occurred while searching.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    alert("Copied to clipboard!");
  };

  return (
    <div>
      <div className="space-y-1 mb-4 mt-4">
        <h4 className="text-sm font-medium leading-none">Search Patent Files</h4>
        <p className="text-sm text-muted-foreground">
          Search for patents related to the entered text and view the results below.
        </p>
      </div>

      {/* Search Input */}
      <div className="flex items-center space-x-1 mb-6">
        <Input
          type="text"
          placeholder="Enter search text..."
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          className="flex-1"
        />
        <Button
          onClick={handleSearch}
          disabled={isLoading}
          className="bg-[oklch(0.8_0.15_200.66)] text-white hover:bg-[oklch(0.7_0.15_200.66)]"
        >
          <SearchIcon className="w-4 h-4 mr-2" />
          Search
        </Button>
      </div>

      {/* Search Results */}
      {isLoading ? (
        <div className="flex justify-center items-center py-8">
          <span className="loading loading-ring loading-lg"></span>
        </div>
      ) : (
        <>
          {searchResults.length > 0 ? (
            <div className="overflow-x-auto w-full">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>File Name</TableHead>
                    <TableHead className="text-center">Title</TableHead>
                    <TableHead className="text-center">Domain</TableHead>
                    <TableHead className="text-center">Sector</TableHead>
                    <TableHead className="text-center">Industry</TableHead>
                    <TableHead className="text-center">Grant Date</TableHead>
                    <TableHead className="text-center w-64 whitespace-nowrap">Patent Number</TableHead>                    
                    <TableHead className="text-center">Assignee(s)</TableHead>
                    <TableHead className="text-center">Abstract</TableHead>
                    <TableHead className="text-center">Summary Audio</TableHead>
                    <TableHead className="text-center">Podcast Audio</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {currentDocuments.map((doc: DocumentType) => (
                    <TableRow key={doc.id}>
                      <TableCell>
                        <a
                          href={`/pdf/document/${doc.documentId}`}
                          className="text-primary hover:underline"
                        >
                          {doc.file_name}
                        </a>
                      </TableCell>
                      <TableCell className="text-left text-sm text-gray-500">
                        {doc.title}
                      </TableCell>
                      <TableCell className="text-center">{doc.domain}</TableCell>
                      <TableCell className="text-center">{doc.sector}</TableCell>
                      <TableCell className="text-center">{doc.industry}</TableCell>
                      <TableCell className="text-left">{doc.grantdate}</TableCell>
                      <TableCell className="text-left w-64 whitespace-nowrap">{doc.patentnumber}</TableCell>
                      <TableCell className="text-left">{doc.assignees}</TableCell>
                      <TableCell className="text-center">
                        {/* Summary Dialog */}
                        <Dialog>
                          <DialogTrigger asChild>
                            <Button
                              variant="ghost"
                              className="p-2 hover:bg-gray-700"
                              aria-label="View Summary"
                              onClick={() => setSelectedDoc(doc)} // Set selected document
                            >
                              <BookOpenIcon className="w-4 h-4" />
                            </Button>
                          </DialogTrigger>
                          {selectedDoc && selectedDoc.id === doc.id && (
                            <DialogContent>
                              <DialogTitle>Abstract</DialogTitle>
                              <DialogDescription>
                                <p className="mb-4">{selectedDoc.abstract}</p>
                                <Button
                                  variant="outline"
                                  onClick={() => handleCopy(selectedDoc.abstract)}
                                  className="flex items-center space-x-2"
                                >
                                  <ClipboardCopyIcon className="w-4 h-4" />
                                  <span>Copy Abstract</span>
                                </Button>
                              </DialogDescription>
                              <DialogFooter>
                                <Button onClick={() => setSelectedDoc(null)} className="bg-[oklch(0.8_0.15_200.66)] text-white hover:bg-[oklch(0.7_0.15_200.66)]">Close</Button>
                              </DialogFooter>
                            </DialogContent>
                          )}
                        </Dialog>
                      </TableCell>
                      <TableCell className="text-center">
                        {/* Audio Summary Dialog */}
                        <Dialog>
                          <DialogTrigger asChild>
                            <Button
                              variant="ghost"
                              className="p-2 hover:bg-gray-700"
                              aria-label="Convert Summary to Audio"
                              onClick={() => setSelectedDoc(doc)} // Set selected document
                            >
                              <Volume2Icon className="w-4 h-4" />
                            </Button>
                          </DialogTrigger>
                          {selectedDoc && selectedDoc.id === doc.id && (
                            <DialogContent>
                              <DialogTitle>Audio Summary</DialogTitle>
                              <DialogDescription>
                                <audio controls className="w-full">
                                  <source src={selectedDoc.audio_url} type="audio/mpeg" />
                                  Your browser does not support the audio element.
                                </audio>
                              </DialogDescription>
                              <DialogFooter>
                                <Button onClick={() => setSelectedDoc(null)} className="bg-[oklch(0.8_0.15_200.66)] text-white hover:bg-[oklch(0.7_0.15_200.66)]">Close</Button>
                              </DialogFooter>
                            </DialogContent>
                          )}
                        </Dialog>
                      </TableCell>
                      <TableCell className="text-center">
                        {/* Podcast Audio Dialog */}
                        <Dialog>
                          <DialogTrigger asChild>
                            <Button
                              variant="ghost"
                              className="p-2 hover:bg-gray-700"
                              aria-label="Podcast Audio"
                              onClick={() => setSelectedDoc(doc)} // Set selected document
                            >
                              <Volume2Icon className="w-4 h-4" />
                            </Button>
                          </DialogTrigger>
                          {selectedDoc && selectedDoc.id === doc.id && (
                            <DialogContent>
                              <DialogTitle>Podcast Audio</DialogTitle>
                              <DialogDescription>
                                <audio controls className="w-full">
                                  <source src={selectedDoc.podcast_url} type="audio/mpeg" />
                                  Your browser does not support the audio element.
                                </audio>
                              </DialogDescription>
                              <DialogFooter>
                                <Button onClick={() => setSelectedDoc(null)} className="bg-[oklch(0.8_0.15_200.66)] text-white hover:bg-[oklch(0.7_0.15_200.66)]">Close</Button>
                              </DialogFooter>
                            </DialogContent>
                          )}
                        </Dialog>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {/* Pagination */}
              <Pagination>
                <PaginationContent>
                  <PaginationItem>
                    <PaginationPrevious
                      href="#"
                      className="hover:bg-primary/80 hover:text-white"
                      onClick={(e) => {
                        e.preventDefault();
                        handlePageChange(Math.max(1, currentPage - 1));
                      }}
                    />
                  </PaginationItem>
                  {Array.from({ length: totalPages }, (_, i) => (
                    <PaginationItem key={i}>
                      <PaginationLink
                        href="#"
                        className="hover:bg-primary/80 hover:text-white"
                        onClick={(e) => {
                          e.preventDefault();
                          handlePageChange(i + 1);
                        }}
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
                      onClick={(e) => {
                        e.preventDefault();
                        handlePageChange(Math.min(totalPages, currentPage + 1));
                      }}
                    />
                  </PaginationItem>
                </PaginationContent>
              </Pagination>
            </div>
          ) : (
            <p className="text-center mt-4">No search results found.</p>
          )}
        </>
      )}
    </div>
  );
};

export default SearchPatentFiles;
