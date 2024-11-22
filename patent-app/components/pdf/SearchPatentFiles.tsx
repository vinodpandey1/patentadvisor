// components/pdf/SearchPatentFiles.tsx
import React, { useState, useEffect } from "react";
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
import { formatDistanceToNow } from "date-fns";
import {
    Dialog,
    DialogTrigger,
    DialogContent,
    DialogTitle,
    DialogDescription,
    DialogFooter,
  } from "@/components/ui/dialog";

interface SearchPatentFilesProps {}

interface DocumentType {
  id: string;
  file_name: string;
  created_at: string;
  summary: string;
  classification: string;
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
      });

      if (res.ok) {
        const data = await res.json();
        setSearchResults(data.results);
      } else {
        alert("Failed to fetch search results.");
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
        <Button onClick={handleSearch} disabled={isLoading}
        className="bg-[oklch(0.8_0.15_200.66)] text-white hover:bg-[oklch(0.7_0.15_200.66)]">
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
                    <TableHead className="text-center">Uploaded</TableHead>
                    <TableHead className="text-center">Summary</TableHead>
                    <TableHead className="text-center">Classification</TableHead>
                    <TableHead className="text-center">Convert Summary to Audio</TableHead>
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
                              <p className="mb-4">{doc.summary}</p>
                              <Button
                                variant="outline"
                                onClick={() => handleCopy(doc.summary)}
                                className="flex items-center space-x-2"
                              >
                                <ClipboardCopyIcon className="w-4 h-4" />
                                <span>Copy Summary</span>
                              </Button>
                            </DialogDescription>
                            <DialogFooter>
                              <Button onClick={() => setSelectedDoc(null)}>Close</Button>
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
                              aria-label="View Classification"
                            >
                              <BookOpenIcon className="w-4 h-4" />
                            </Button>
                          </DialogTrigger>
                          <DialogContent>
                            <DialogTitle>Classification</DialogTitle>
                            <DialogDescription>
                              <p className="mb-4">{doc.classification}</p>
                              <Button
                                variant="outline"
                                onClick={() => handleCopy(doc.classification)}
                                className="flex items-center space-x-2"
                              >
                                <ClipboardCopyIcon className="w-4 h-4" />
                                <span>Copy Classification</span>
                              </Button>
                            </DialogDescription>
                            <DialogFooter>
                              <Button onClick={() => setSelectedDoc(null)}>Close</Button>
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
                              aria-label="Convert Summary to Audio"
                            >
                              <Volume2Icon className="w-4 h-4" />
                            </Button>
                          </DialogTrigger>
                          <DialogContent>
                            <DialogTitle>Audio Summary</DialogTitle>
                            <DialogDescription>
                              <audio controls className="w-full">
                                <source src={`/api/pdf/synthesize/${doc.id}`} type="audio/mpeg" />
                                Your browser does not support the audio element.
                              </audio>
                            </DialogDescription>
                            <DialogFooter>
                              <Button onClick={() => setSelectedDoc(null)}>Close</Button>
                            </DialogFooter>
                          </DialogContent>
                        </Dialog>
                      </TableCell>
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
          ) : (
            <p className="text-center mt-4">No search results found.</p>
          )}
        </>
      )}
    </div>
  );
};

export default SearchPatentFiles;
