// app/api/pdf/uploadToUploadDirectory/route.ts

import { NextResponse } from "next/server";
import { createClient } from "@/lib/utils/supabase/server";
import { uploadFileToUploadDirectory } from "@/lib/hooks/useNewFileUpload";

/**
 * API Route: Handles PDF file uploads to the 'upload' directory in Cloudflare R2.
 *
 * **Process:**
 * 1. Authenticates the user.
 * 2. Extracts the PDF file from the request.
 * 3. Validates the file type and size.
 * 4. Generates a unique file name if necessary.
 * 5. Uploads the file to the 'upload' directory in Cloudflare.
 * 6. Returns the public URL, file path, and patentId (filename without extension).
 *
 * @param {Request} request - The incoming request object.
 * @returns {Promise<NextResponse>} JSON response containing the uploaded document details.
 */
export async function POST(request: Request) {
  const supabase = createClient();

  // Authenticate user
  const {
    data: { user },
    error: authError,
  } = await supabase.auth.getUser();

  const userId = user?.id;

  if (authError || !userId) {
    return NextResponse.json(
      { error: "You must be logged in to upload documents." },
      { status: 401 }
    );
  }

  try {
    const formData = await request.formData();
    const file = formData.get("file") as File | null;

    if (!file) {
      throw new Error("No document file uploaded.");
    }

    // Server-Side Validation: File Type
    if (file.type !== "application/pdf") {
      throw new Error("Only PDF files are allowed.");
    }

    // Server-Side Validation: File Size (Max 10MB)
    const maxSizeMB = 10;
    const fileSizeMB = file.size / (1024 * 1024);
    if (fileSizeMB > maxSizeMB) {
      throw new Error(`File size exceeds the maximum limit of ${maxSizeMB} MB.`);
    }

    // Extract patentId from the filename (without extension)
    const originalFileName = file.name;
    const fileName = originalFileName.replace(/\.[^/.]+$/, ""); // Removes extension
    const patentId = fileName;

    console.log(`Uploading document: ${originalFileName} as ${fileName}`);

    // Upload the file to the 'upload' directory
    const { url: publicUrl, path: filePath } = await uploadFileToUploadDirectory({
      file,
      fileName,
      contentType: file.type, // Use the original content type
    });

    return NextResponse.json(
      {
        url: publicUrl,
        path: filePath,
        patentId: patentId,
      },
      { status: 200 }
    );
  } catch (error: any) {
    console.error("Error in file upload:", error);
    return NextResponse.json(
      {
        error:
          error.message ||
          "An error occurred during the file upload process.",
      },
      { status: 500 }
    );
  }
}
