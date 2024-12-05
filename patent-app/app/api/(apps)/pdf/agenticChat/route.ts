// app/api/pdf/agenticChat/route.ts

import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/lib/utils/supabase/server";

/**
 * API Route: Proxy for Agentic Chatbot.
 *
 * **Functionality:**
 * - Authenticates the user.
 * - Extracts user ID, patent ID, and query from query parameters.
 * - Validates the input.
 * - Forwards the request to the Agentic Chatbot API.
 * - Returns the response back to the frontend.
 *
 * @param {NextRequest} req - Incoming request object.
 * @returns {Promise<NextResponse>} - JSON response with Agentic Chatbot data or error messages.
 */
export async function GET(req: NextRequest) {
  const supabase = createClient();

  // Authenticate user
  const {
    data: { user },
    error: authError,
  } = await supabase.auth.getUser();

  const userId = user?.id;

  if (authError || !userId) {
    console.error("Authentication Error:", authError);
    return NextResponse.json(
      { error: "You must be logged in to use the Agentic Chatbot." },
      { status: 401 }
    );
  }

  try {
    // Extract query parameters
    const { searchParams } = new URL(req.url);
    const query = searchParams.get("query");
    const patentId = searchParams.get("patentId");

    if (!query || !patentId) {
      return NextResponse.json(
        { error: "Missing required query parameters: 'query' and 'patentId'." },
        { status: 400 }
      );
    }

    // Construct the Agentic Chatbot API URL
    const agenticApiUrl = `http://127.0.0.1:5001/patent/query/${encodeURIComponent(
      userId
    )}/${encodeURIComponent(patentId)}?query=${encodeURIComponent(query)}`;

    // Forward the request to the Agentic Chatbot API
    const agenticResponse = await fetch(agenticApiUrl, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!agenticResponse.ok) {
      const errorText = await agenticResponse.text();
      console.error("Agentic Chatbot API Error:", errorText);
      return NextResponse.json(
        { error: `Agentic Chatbot API Error: ${errorText}` },
        { status: agenticResponse.status }
      );
    }

    const data = await agenticResponse.json();

    return NextResponse.json(data, { status: 200 });
  } catch (error: any) {
    console.error("Agentic Chatbot Proxy Route Error:", error);
    return NextResponse.json(
      {
        error:
          error.message ||
          "An error occurred while processing your request to the Agentic Chatbot.",
      },
      { status: 500 }
    );
  }
}
