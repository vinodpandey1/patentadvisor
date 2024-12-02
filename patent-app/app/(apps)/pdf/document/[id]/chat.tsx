// app/pdf/document/[id]/chat.tsx

"use client";

import { useState, useEffect } from "react";
// import { ChatWindow } from "@/components/chat/ChatWindow"; // Commented out
import ChatWelcome from "@/components/chat/ChatWelcome";
import { Switch } from "@/components/ui/switch";
import { Modal } from "@/components/ui/Modal"; // Ensure correct imports via index.ts
import { Button } from "@/components/ui/button";
import { useSwipeable } from "react-swipeable";

// Swiper React components
import { Swiper, SwiperSlide } from "swiper/react";

// Swiper styles
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/pagination";

// Swiper modules
import { Navigation, Pagination, A11y } from "swiper/modules";

interface ImageData {
  src: string;
  alt: string;
  description: string;
}

interface ChatProps {
  currentDoc: any;
  initialMessages: any[];
  userId: string; // Added userId prop
}

export default function DocumentClient({
  currentDoc,
  initialMessages,
  userId, // Destructure userId
}: ChatProps) {
  const documentId = currentDoc.id;
  const pdfUrl = currentDoc.file_url;

  // Helper function to remove file extension
  const removeFileExtension = (filename: string): string => {
    return filename.substring(0, filename.lastIndexOf(".")) || filename;
  };

  // Extract patentId from file_name
  const patentId = removeFileExtension(currentDoc.file_name || "N/A");

  // State to toggle PDF display
  const [showPdf, setShowPdf] = useState(true);

  // State to toggle Image Gallery display
  const [showImages, setShowImages] = useState(true); // Set to 'true' by default or as desired

  // State for Image Gallery Modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState<number | null>(null);

  // State to store fetched images
  const [images, setImages] = useState<ImageData[]>([]);
  const [imagesLoading, setImagesLoading] = useState<boolean>(false);
  const [imagesError, setImagesError] = useState<string | null>(null);

  // Fetch images from the new API route using patentId
  useEffect(() => {
    const fetchImages = async () => {
      setImagesLoading(true);
      setImagesError(null);

      try {
        const response = await fetch(`/api/pdf/patentImages?patentId=${encodeURIComponent(patentId)}`);
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || "Failed to fetch patent images.");
        }

        const data = await response.json();
        // Ensure that data.images is an array
        if (Array.isArray(data.images)) {
          setImages(data.images);
        } else {
          // If data.images is not an array, set to empty array
          setImages([]);
          console.warn("Received images is not an array:", data.images);
        }
      } catch (error: any) {
        console.error("Error fetching patent images:", error);
        setImagesError(error.message || "An error occurred while fetching patent images.");
      } finally {
        setImagesLoading(false);
      }
    };

    if (showImages && patentId !== "N/A") {
      fetchImages();
    } else {
      // If not showing images or invalid patentId, clear images
      setImages([]);
      setImagesError(null);
    }
  }, [patentId, showImages]);

  // Handlers for opening and closing the modal
  const openModal = (index: number) => {
    setCurrentImageIndex(index);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setCurrentImageIndex(null);
  };

  // Handlers for navigating between images
  const prevImage = () => {
    if (currentImageIndex !== null) {
      setCurrentImageIndex(
        currentImageIndex === 0 ? images.length - 1 : currentImageIndex - 1
      );
    }
  };

  const nextImage = () => {
    if (currentImageIndex !== null) {
      setCurrentImageIndex(
        currentImageIndex === images.length - 1 ? 0 : currentImageIndex + 1
      );
    }
  };

  // Swipe handlers for touch devices within modal
  const handlers = useSwipeable({
    onSwipedLeft: () => nextImage(),
    onSwipedRight: () => prevImage(),
    preventDefault: true, // Updated property name
    trackMouse: true,
  });

  // Keyboard navigation for accessibility
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (isModalOpen) {
        if (e.key === "ArrowLeft") {
          prevImage();
        } else if (e.key === "ArrowRight") {
          nextImage();
        } else if (e.key === "Escape") {
          closeModal();
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isModalOpen, currentImageIndex, images.length]);

  // New State for Python Chat API
  const [pythonChatMessages, setPythonChatMessages] = useState<any[]>([]);
  const [pythonQuery, setPythonQuery] = useState<string>("");
  const [pythonIsLoading, setPythonIsLoading] = useState<boolean>(false);

  const handlePythonSend = async () => {
    if (!pythonQuery.trim()) {
      alert("Please enter a query for the Python Chat API.");
      return;
    }

    // Add the human message to pythonChatMessages
    const newHumanMessage = { role: "human", content: pythonQuery };
    setPythonChatMessages([...pythonChatMessages, newHumanMessage]);

    setPythonIsLoading(true);

    try {
      const response = await fetch("/api/pdf/pythonChat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          userId: userId, // Use the passed userId
          documentId: documentId, // If needed, otherwise you can pass patentId
          query: pythonQuery,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error("Python Chat API Error:", errorData.error);
        alert(`Failed to get response from Python Chat API: ${errorData.error}`);
        return;
      }

      const data = await response.json();

      // Add the AI response to pythonChatMessages
      const newAiMessage = { role: "ai", content: data.answer };
      setPythonChatMessages([...pythonChatMessages, newHumanMessage, newAiMessage]);
    } catch (error) {
      console.error("Error communicating with Python Chat API:", error);
      alert("An error occurred while communicating with the Python Chat API.");
    } finally {
      setPythonIsLoading(false);
      setPythonQuery("");
    }
  };

  return (
    <div className="bg-white min-h-screen">
      {/* Toggle Switches for PDF and Image Gallery Display */}
      <div className="mb-8 flex justify-center items-center space-x-8 px-4">
        {/* Toggle for PDF Display */}
        <div className="flex items-center space-x-2">
          <Switch
            id="show_pdf"
            checked={showPdf}
            onCheckedChange={(checked) => setShowPdf(checked === true)}
          />
          <label
            htmlFor="show_pdf"
            className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
          >
            Show PDF
          </label>
        </div>

        {/* Toggle for Image Gallery Display */}
        <div className="flex items-center space-x-2">
          <Switch
            id="show_images"
            checked={showImages}
            onCheckedChange={(checked) => setShowImages(checked === true)}
          />
          <label
            htmlFor="show_images"
            className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
          >
            Show Document Images
          </label>
        </div>
      </div>

      {/* Image Gallery Carousel */}
      {showImages && (
        <div className="w-full px-4 mb-8">
          <div className="bg-gray-50 p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4 text-center">
              Extracted Images
            </h2>

            {/* Loading and Error States */}
            {imagesLoading && <p className="text-center">Loading images...</p>}
            {imagesError && (
              <p className="text-center text-red-500">Error: {imagesError}</p>
            )}

            {/* Swiper Carousel */}
            {!imagesLoading && !imagesError && images.length > 0 && (
              <Swiper
                // Install Swiper modules
                modules={[Navigation, Pagination, A11y]}
                spaceBetween={30} // Increased space between slides from 20 to 30
                slidesPerView={1}
                navigation
                pagination={{ clickable: true }}
                breakpoints={{
                  // when window width is >= 640px
                  640: {
                    slidesPerView: 2,
                  },
                  // when window width is >= 768px
                  768: {
                    slidesPerView: 3,
                  },
                  // when window width is >= 1024px
                  1024: {
                    slidesPerView: 4,
                  },
                }}
                className="mySwiper"
              >
                {images.map((image, index) => (
                  <SwiperSlide key={index}>
                    <div
                      className="cursor-pointer transform transition-transform duration-300 hover:scale-105 border border-gray-200 rounded-lg overflow-hidden shadow-md"
                      onClick={() => openModal(index)}
                    >
                      <img
                        src={image.src}
                        alt={image.alt}
                        className="w-full h-40 object-cover"
                        loading="lazy"
                      />
                    </div>
                  </SwiperSlide>
                ))}
              </Swiper>
            )}

            {/* No Images Available */}
            {!imagesLoading && !imagesError && images.length === 0 && (
              <p className="text-center text-gray-700">No images available for this patent.</p>
            )}
          </div>
        </div>
      )}

      {/* Main Grid Layout for Chats and PDF Viewer */}
      <div
        className={`px-4 grid w-full gap-8 ${
          showPdf ? "lg:grid-cols-2" : "grid-cols-1"
        }`}
      >
        {/* Existing Chat Window - Commented Out */}
        {/*
        <div className="h-[90vh] overflow-hidden rounded-lg shadow-md">
          <ChatWindow
            endpoint="/api/pdf/chat"
            placeholder="Ask me anything about the document..."
            emptyStateComponent={<ChatWelcome />}
            chatId={currentDoc.conversation_id}
            initialMessages={initialMessages}
            documentId={documentId}
          />
        </div>
        */}

        {/* New Python Chat API Section */}
        <div className="h-[90vh] overflow-hidden rounded-lg shadow-md">
          <div className="flex flex-col h-full">
            {/* Chat Header */}
            <div className="p-4 bg-gray-100 border-b border-gray-300">
              <h2 className="text-xl font-semibold">Python Chat API</h2>
            </div>

            {/* Chat Messages */}
            <div className="flex-1 p-4 overflow-y-auto bg-gray-50">
              {pythonChatMessages.map((msg, index) => (
                <div
                  key={index}
                  className={`mb-4 flex ${
                    msg.role === "human" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`${
                      msg.role === "human" ? "bg-blue-500 text-white" : "bg-gray-300 text-black"
                    } rounded-lg p-2 max-w-xs`}
                  >
                    {msg.content}
                  </div>
                </div>
              ))}
            </div>

            {/* Chat Input */}
            <div className="p-4 bg-white flex items-center space-x-2">
              <input
                type="text"
                value={pythonQuery}
                onChange={(e) => setPythonQuery(e.target.value)}
                placeholder="Ask the Python Chat API..."
                className="flex-1 border border-gray-300 rounded p-2"
              />
              <Button
                onClick={handlePythonSend}
                disabled={pythonIsLoading}
                className="bg-green-500 text-white px-4 py-2 rounded"
              >
                {pythonIsLoading ? "Sending..." : "Ask"}
              </Button>
            </div>
          </div>
        </div>

        {/* PDF Viewer */}
        {showPdf && (
          <div className="h-[90vh] hidden md:flex flex-col overflow-hidden rounded-lg shadow-md">
            <iframe
              src={pdfUrl}
              className="w-full h-full"
              style={{ border: "none" }}
              title="PDF Viewer"
            ></iframe>
          </div>
        )}
      </div>

      {/* Image Gallery Modal */}
      <Modal isOpen={isModalOpen} onClose={closeModal}>
        {currentImageIndex !== null && (
          <div {...handlers} className="flex flex-col items-center">
            <div className="relative w-full max-w-3xl">
              <img
                src={images[currentImageIndex].src}
                alt={images[currentImageIndex].alt}
                className="w-full h-auto object-contain rounded"
              />

              {/* Previous Button */}
              <Button
                variant="ghost"
                className="absolute top-1/2 left-0 transform -translate-y-1/2 bg-white bg-opacity-50 hover:bg-opacity-75 rounded-full p-2"
                onClick={prevImage}
                aria-label="Previous Image"
              >
                ❮
              </Button>

              {/* Next Button */}
              <Button
                variant="ghost"
                className="absolute top-1/2 right-0 transform -translate-y-1/2 bg-white bg-opacity-50 hover:bg-opacity-75 rounded-full p-2"
                onClick={nextImage}
                aria-label="Next Image"
              >
                ❯
              </Button>
            </div>

            {/* Image Description */}
            <p className="text-center text-gray-700 mt-4">
              {images[currentImageIndex].description}
            </p>

            {/* Close Button */}
            <Button
              onClick={closeModal}
              className="mt-4 bg-[oklch(0.8_0.15_200.66)] text-white hover:bg-[oklch(0.7_0.15_200.66)]"
            >
              Close
            </Button>
          </div>
        )}
      </Modal>
    </div>
  );
}
