// app/pdf/document/[id]/chat.tsx

"use client";

import React, { useState, useEffect } from "react";
import { Switch } from "@/components/ui/switch";
import { Modal } from "@/components/ui/Modal";
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

// Import the AgenticChatWindow component
import AgenticChatWindow from "@/components/chat/AgenticChatWindow";

// Import existing components and utilities
import { DocumentType } from "@/lib/types";
import { getPolarityLabel, getSubjectivityLabel } from "@/lib/utils/sentiment";

interface ImageData {
  src: string;
  alt: string;
  description: string;
}

interface ChatProps {
  currentDoc: DocumentType;
  initialPythonMessages: ChatMessage[];
  initialAgenticMessages: ChatMessage[];
  userId: string;
  documentId: string;
}

interface ChatMessage {
  role: "human" | "ai";
  content: string;
  sentiment?: {
    polarity: number;
    subjectivity: number;
  };
}

export default function DocumentClient({
  currentDoc,
  initialPythonMessages,
  initialAgenticMessages,
  userId,
  documentId,
}: ChatProps) {
  const pdfUrl = currentDoc.file_url; // Ensure 'file_url' is the correct field for the PDF URL

  // Helper function to remove file extension
  const removeFileExtension = (filename: string): string => {
    return filename.substring(0, filename.lastIndexOf(".")) || filename;
  };

  // Extract patentId from file_name
  const patentId = removeFileExtension(currentDoc.file_name || "N/A");

  // State to toggle PDF display
  const [showPdf, setShowPdf] = useState(true);

  // State to toggle Image Gallery display
  const [showImages, setShowImages] = useState(true);

  // State to toggle Agentic Chatbot display
  const [showAgenticChat, setShowAgenticChat] = useState(false);

  // State for Image Gallery Modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState<number | null>(null);

  // State to store fetched images
  const [images, setImages] = useState<ImageData[]>([]);
  const [imagesLoading, setImagesLoading] = useState<boolean>(false);
  const [imagesError, setImagesError] = useState<string | null>(null);

  // Fetch images from the API route using patentId
  useEffect(() => {
    const fetchImages = async () => {
      setImagesLoading(true);
      setImagesError(null);

      try {
        const response = await fetch(
          `/api/pdf/patentImages?patentId=${encodeURIComponent(patentId)}`
        );
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
        setImagesError(
          error.message || "An error occurred while fetching patent images."
        );
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

  // Separate Messages States for Python and Agentic Chatbots
  const [pythonMessages, setPythonMessages] = useState<ChatMessage[]>(
    initialPythonMessages || []
  );
  const [agenticMessages, setAgenticMessages] = useState<ChatMessage[]>(
    initialAgenticMessages || []
  );
  const [isHistoryLoading, setIsHistoryLoading] = useState<boolean>(false);
  const [historyError, setHistoryError] = useState<string | null>(null);

  // State for Python Chat API
  const [pythonQuery, setPythonQuery] = useState<string>("");
  const [pythonIsLoading, setPythonIsLoading] = useState<boolean>(false);

  // State for Agentic Chat API
  const [agenticIsLoading, setAgenticIsLoading] = useState<boolean>(false); // Added state

  /**
   * Function to store a new message.
   *
   * **Functionality:**
   * - Sends a POST request to `/api/pdf/storeMessage` with the message details.
   * - Logs any errors encountered during the request.
   *
   * @param {ChatMessage} message - The chat message to store.
   */
  const storeMessage = async (message: ChatMessage) => {
    try {
      const response = await fetch("/api/pdf/storeMessage", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          documentId,
          role: message.role,
          content: message.content,
          sentiment: message.sentiment,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error("Error storing message:", errorData.error);
      }
    } catch (error) {
      console.error("Error storing message:", error);
    }
  };

  /**
   * Handler to send queries to the Python Chat API.
   *
   * **Functionality:**
   * - Validates the user query.
   * - Adds the user's message to `pythonMessages` and stores it.
   * - Sends the query to the Python Chat API.
   * - Processes the response and adds the AI's message to `pythonMessages` and stores it.
   */
  const handlePythonSend = async () => {
    if (!pythonQuery.trim()) {
      alert("Please enter a query for the Python Chat API.");
      return;
    }

    // Add the human message to pythonMessages and store it
    const newHumanMessage: ChatMessage = { role: "human", content: pythonQuery };
    setPythonMessages((prevMessages) => [...prevMessages, newHumanMessage]);
    await storeMessage(newHumanMessage);

    setPythonIsLoading(true);

    try {
      const response = await fetch("/api/pdf/pythonChat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          documentId: documentId,
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

      // Check if 'answer' and 'bias.sentiment' exist and are valid
      if (data.answer && typeof data.answer === "string" && data.bias?.sentiment) {
        const newAiMessage: ChatMessage = {
          role: "ai",
          content: data.answer,
          sentiment: {
            polarity: data.bias.sentiment.polarity,
            subjectivity: data.bias.sentiment.subjectivity,
          },
        };
        setPythonMessages((prevMessages) => [...prevMessages, newAiMessage]);
        await storeMessage(newAiMessage);
      } else {
        console.warn("Incomplete data received from Python Chat API:", data);
        alert("Received incomplete data from the Python Chat API.");
      }
    } catch (error) {
      console.error("Error communicating with Python Chat API:", error);
      alert("An error occurred while communicating with the Python Chat API.");
    } finally {
      setPythonIsLoading(false);
      setPythonQuery("");
    }
  };

  /**
   * Handler to send queries to the Agentic Chat API.
   *
   * **Functionality:**
   * - Validates the user query.
   * - Adds the user's message to `agenticMessages` and stores it.
   * - Sends the query to the Agentic Chat API.
   * - Processes the response and adds the AI's message to `agenticMessages` and stores it.
   * - Handles different response types (text, audio URL, image URL).
   *
   * @param {string} query - The user's query to send.
   */
  const handleAgenticSend = async (query: string) => {
    if (!query.trim()) {
      alert("Please enter a query for the Agentic Chatbot.");
      return;
    }

    // Add the human message to agenticMessages and store it
    const newHumanMessage: ChatMessage = { role: "human", content: query };
    setAgenticMessages((prevMessages) => [...prevMessages, newHumanMessage]);
    await storeMessage(newHumanMessage);

    setAgenticIsLoading(true); // Start loading

    try {
      // Construct the Agentic Chat API URL via the proxy
      const agenticApiUrl = `/api/pdf/agenticChat?userId=${encodeURIComponent(
        userId
      )}&patentId=${encodeURIComponent(patentId)}&query=${encodeURIComponent(query)}`;

      const response = await fetch(agenticApiUrl, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Agentic Chat API Error:", errorText);
        alert(`Failed to get response from Agentic Chat API: ${errorText}`);
        return;
      }

      const data = await response.json();

      // Assuming the API returns an object with an 'answer' field
      if (data.answer && typeof data.answer === "string") {
        const newAiMessage: ChatMessage = {
          role: "ai",
          content: data.answer,
          // If sentiment data is available, include it. Otherwise, omit.
          // sentiment: data.sentiment, // Uncomment if sentiment is provided
        };
        setAgenticMessages((prevMessages) => [...prevMessages, newAiMessage]);
        await storeMessage(newAiMessage);
      } else {
        console.warn("Incomplete data received from Agentic Chat API:", data);
        alert("Received incomplete data from the Agentic Chat API.");
      }
    } catch (error) {
      console.error("Error communicating with Agentic Chat API:", error);
      alert("An error occurred while communicating with the Agentic Chat API.");
    } finally {
      setAgenticIsLoading(false); // End loading
    }
  };

  return (
    <div className="bg-white min-h-screen">
      {/* Toggle Switches for PDF, Image Gallery, and Agentic Chatbot */}
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

        {/* Toggle for Agentic Chatbot Display */}
        <div className="flex items-center space-x-2">
          <Switch
            id="show_agentic_chat"
            checked={showAgenticChat}
            onCheckedChange={(checked) => setShowAgenticChat(checked === true)}
          />
          <label
            htmlFor="show_agentic_chat"
            className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
          >
            Show Agentic Chatbot
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
                spaceBetween={30}
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
        {/* Python Chat API Section */}
        {!showAgenticChat && (
          <div className="h-[90vh] overflow-hidden rounded-lg shadow-md">
            <div className="flex flex-col h-full">
              {/* Chat Header */}
              <div className="p-4 bg-gray-100 border-b border-gray-300">
                <h2 className="text-xl font-semibold">Chat with Patent Document</h2>
              </div>

              {/* Chat Messages */}
              <div className="flex-1 p-4 overflow-y-auto bg-gray-50">
                {/* Display Chat History */}
                {isHistoryLoading && <p>Loading chat history...</p>}
                {historyError && <p className="text-red-500">Error: {historyError}</p>}
                {!isHistoryLoading && !historyError && pythonMessages.length > 0 && (
                  pythonMessages.map((msg, index) => (
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
                        
                        {/* Display sentiment data for AI messages */}
                        {msg.role === "ai" && msg.sentiment && (
                          <div className="mt-2 text-sm">
                            <span
                              className={`inline-block px-2 py-1 rounded mr-2 ${getPolarityLabel(msg.sentiment.polarity).color}`}
                            >
                              Polarity: {getPolarityLabel(msg.sentiment.polarity).label} ({msg.sentiment.polarity.toFixed(2)})
                            </span>
                            <span
                              className={`inline-block px-2 py-1 rounded ${getSubjectivityLabel(msg.sentiment.subjectivity).color}`}
                            >
                              Subjectivity: {getSubjectivityLabel(msg.sentiment.subjectivity).label} ({msg.sentiment.subjectivity.toFixed(2)})
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                )}

                {/* No Chat History */}
                {!isHistoryLoading && !historyError && pythonMessages.length === 0 && (
                  <p className="text-center text-gray-700">No chat history available.</p>
                )}
              </div>

              {/* Chat Input */}
              <div className="p-4 bg-white flex items-center space-x-2">
                <input
                  type="text"
                  value={pythonQuery}
                  onChange={(e) => setPythonQuery(e.target.value)}
                  placeholder="Start Q&A With this patent document..."
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
        )}

        {/* Agentic Chatbot Section */}
        {showAgenticChat && (
          <AgenticChatWindow
            patentId={patentId}
            userId={userId}
            handleAgenticSend={handleAgenticSend}
            messages={agenticMessages}
            isLoading={agenticIsLoading}
          />
        )}

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
            <p className="text-left text-gray-700 mt-4">
              {images[currentImageIndex].description}
            </p>

            {/* Close Button */}
            <Button
              onClick={closeModal}
              className="mt-4 bg-green-500 text-white hover:bg-green-600"
            >
              Close
            </Button>
          </div>
        )}
      </Modal>
    </div>
  );
}
