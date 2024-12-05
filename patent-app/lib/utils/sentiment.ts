// lib/utils/sentiment.ts

export const getPolarityLabel = (polarity: number): { label: string; color: string } => {
    if (polarity > 0.1) return { label: "Positive", color: "bg-green-200 text-green-800" };
    if (polarity < -0.1) return { label: "Negative", color: "bg-red-200 text-red-800" };
    return { label: "Neutral", color: "bg-gray-200 text-gray-800" };
  };
  
  export const getSubjectivityLabel = (subjectivity: number): { label: string; color: string } => {
    if (subjectivity > 0.5) return { label: "Subjective", color: "bg-yellow-200 text-yellow-800" };
    return { label: "Objective", color: "bg-blue-200 text-blue-800" };
  };
  