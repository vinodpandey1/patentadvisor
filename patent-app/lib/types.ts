// lib/types.ts

export interface DocumentType {
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
    file_url:string;
  }
  