CREATE TABLE patentdocuments (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(1536), -- Adjust vector dimension based on your embeddings
    metadata JSONB
);