create table
  patentdocuments (
    id text primary key,
    content text, -- corresponds to Document.pageContent
    metadata jsonb, -- corresponds to Document.metadata
    embedding vector (3072) -- 1536 works for OpenAI embeddings, change if needed
  );

  create table
  patentdocumentdetail (
    id text primary key,
    content text, -- corresponds to Document.pageContent
    metadata jsonb, -- corresponds to Document.metadata
    embedding vector (3072) -- 1536 works for OpenAI embeddings, change if needed
  );