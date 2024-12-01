create table
  patentdocuments (
    id text primary key,
    document_id uuid,
    content text, -- corresponds to Document.pageContent
    metadata jsonb, -- corresponds to Document.metadata
    embedding vector (1536) -- 1536 works for OpenAI embeddings, change if needed
  );

CREATE INDEX IDX_PATENT_DOC_ID ON patentdocuments(document_id);


ALTER TABLE patentdocuments
ADD CONSTRAINT fk_patent_document_id
FOREIGN KEY (document_id)
REFERENCES documents(id)
ON DELETE CASCADE;

  create table
  patentdocumentdetail (
    id text primary key,
    document_id uuid,
    patentId text,
    content text, -- corresponds to Document.pageContent
    metadata jsonb, -- corresponds to Document.metadata
    embedding vector (1536) -- 1536 works for OpenAI embeddings, change if needed
  );

CREATE INDEX IDX_PATENTDETAILS_DOC_ID ON patentdocumentdetail(document_id);

ALTER TABLE patentdocumentdetail
ADD CONSTRAINT fk_patent_document_id
FOREIGN KEY (document_id)
REFERENCES documents(id)
ON DELETE CASCADE;


CREATE TABLE conversation_history (
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    document_id UUID NOT NULL,
    role TEXT NOT NULL, -- 'user' or 'assistant'
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IDX_SESSION_ID ON conversation_history(session_id);


create or replace function match_documents_native (
  query_embedding vector(1536),
  match_threshold float,
  match_count int
)
returns table (
  id text,
  document_id text,
  page_content text,
  metadata text,
  similarity float
)
language sql stable
as $$
  select
    patentdocuments.id,
    patentdocuments.document_id,
    patentdocuments.content,
    patentdocuments.metadata,
    1 - (patentdocuments.embedding <=> query_embedding) as similarity
  from patentdocuments
  where 1 - (patentdocuments.embedding <=> query_embedding) > match_threshold
  order by (patentdocuments.embedding <=> query_embedding) asc
  limit match_count;
$$;

create or replace function match_documents_detail (
  query_embedding vector(1536),
  match_threshold float,
  match_count int, 
  documentID uuid
)
returns table (
  id text,
  page_content text,
  similarity float
)
language sql stable
as $$
  select
    patentdocumentdetail.id,
    patentdocumentdetail.content,
    1 - (patentdocumentdetail.embedding <=> query_embedding) as similarity
  from patentdocumentdetail
  where 1 - (patentdocumentdetail.embedding <=> query_embedding) > match_threshold
  AND 
  patentdocumentdetail.document_id = documentID
  order by (patentdocumentdetail.embedding <=> query_embedding) asc
  limit match_count;
$$;