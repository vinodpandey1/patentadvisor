// lib/hooks/useUploadToUploadDirectory.ts

import { PutObjectCommand } from "@aws-sdk/client-s3";
import s3 from "@/lib/cloudflare";
import { v4 as uuidv4 } from "uuid";

interface UploadOptions {
  file: File;
  contentType: string;
  fileName?: string;
}

/**
 * Uploads a file to the 'upload' directory in Cloudflare R2.
 *
 * @param {UploadOptions} options - The options for uploading.
 * @returns {Promise<{ url: string; path: string }>} The public URL and file path of the uploaded file.
 */
export async function uploadFileToUploadDirectory({
  file,
  fileName,
  contentType,
}: UploadOptions): Promise<{ url: string; path: string }> {
  const uploadPath = "upload"; // Fixed upload path for this function
  const uniqueFileName = fileName || `file-${uuidv4()}`; // Generate unique filename if not provided
  const key = `${uploadPath}/${uniqueFileName}.pdf`; // Assuming PDF files

  try {
    // Convert File to Buffer
    const buffer = Buffer.from(await file.arrayBuffer());

    // Upload the file to Cloudflare R2
    const uploadParams = {
      Bucket: process.env.STORAGE_BUCKET_PIPELINE!, // Ensure this is set in your .env
      Key: key,
      Body: buffer,
      ContentType: contentType,
    };

    console.log(`Uploading to Bucket: ${uploadParams.Bucket}`);
    console.log(`S3 Key: ${uploadParams.Key}`);

    const command = new PutObjectCommand(uploadParams);
    await s3.send(command);

    // Construct the public URL
    const publicUrl = `${process.env.STORAGE_PUBLIC_URL}/${key}`; // e.g., "https://<bucket_name>.r2.dev/upload/<fileName>.pdf"
    const filePath = key;

    console.log(`publicUrl-${publicUrl}`)

    return { url: publicUrl, path: filePath };
  } catch (error) {
    console.error("Error uploading file:", error);
    throw new Error("Failed to upload file to Cloudflare.");
  }
}
