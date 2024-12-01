create table
  patentdocuments (
    id text primary key,
    content text, -- corresponds to Document.pageContent
    metadata jsonb, -- corresponds to Document.metadata
    embedding vector (1536) -- 1536 works for OpenAI embeddings, change if needed
  );

  create table
  patentdocumentdetail (
    id text primary key,
    patentId text,
    content text, -- corresponds to Document.pageContent
    metadata jsonb, -- corresponds to Document.metadata
    embedding vector (1536) -- 1536 works for OpenAI embeddings, change if needed
  );

CREATE TABLE conversation_history (
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL, -- 'user' or 'assistant'
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IDX_SESSION_ID ON conversation_history(session_id);


--   create or replace function match_documents (
--   query_embedding vector(384),
--   match_threshold float,
--   match_count int
-- )
-- returns table (
--   id bigint,
--   title text,
--   body text,
--   similarity float
-- )
-- language sql stable
-- as $$
--   select
--     documents.id,
--     documents.title,
--     documents.body,
--     1 - (documents.embedding <=> query_embedding) as similarity
--   from documents
--   where 1 - (documents.embedding <=> query_embedding) > match_threshold
--   order by (documents.embedding <=> query_embedding) asc
--   limit match_count;
-- $$;

create function match_documents (
  query_embedding vector (1536),
  filter jsonb default '{}'
) 
returns table (
  id text,
  content text,
  metadata jsonb,
  similarity float
) language sql stable 
as $$
  select
    patentdocuments.id,
    patentdocuments.content,
    patentdocuments.metadata,
    1 - (patentdocuments.embedding <=> query_embedding) as similarity
  from patentdocuments
  where metadata @> filter
  order by patentdocuments.embedding <=> query_embedding asc
$$;


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
  documentID text
)
returns table (
  id text,
  page_content text,
  metadata text,
  similarity float
)
language sql stable
as $$
  select
    patentdocumentdetail.id,
    patentdocumentdetail.content,
    patentdocumentdetail.metadata,
    1 - (patentdocumentdetail.embedding <=> query_embedding) as similarity
  from patentdocumentdetail
  where 1 - (patentdocumentdetail.embedding <=> query_embedding) > match_threshold
  AND 
  patentdocumentdetail.id like documentID
  order by (patentdocumentdetail.embedding <=> query_embedding) asc
  limit match_count;
$$;