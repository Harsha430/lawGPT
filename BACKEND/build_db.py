import os
import time
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

load_dotenv()


PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "lawgpt")
EMBEDDING_DIMENSION = 384  


pc = Pinecone(api_key=PINECONE_API_KEY)


existing_indexes = pc.list_indexes().names()
if INDEX_NAME in existing_indexes:
    
    index_info = pc.describe_index(INDEX_NAME)
    if index_info.dimension != EMBEDDING_DIMENSION:
        print(f"Deleting existing index with dimension {index_info.dimension}...")
        pc.delete_index(INDEX_NAME)
        print("Index deleted. Creating new index with correct dimension...")
        time.sleep(5)  
        existing_indexes = []

if INDEX_NAME not in existing_indexes:
    print(f"Creating new Pinecone index with dimension {EMBEDDING_DIMENSION}...")
    pc.create_index(
        name=INDEX_NAME,
        dimension=EMBEDDING_DIMENSION,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )
    print("Index created successfully!")

index = pc.Index(INDEX_NAME)


DATA_DIR = "books"


BOOK_MAPPING = {
    "250882_english_01042024_0.pdf": "BSA",   
    "250883_english_01042024.pdf": "BNS",     
    "250884_2_english_01042024.pdf": "BNSS"   
}

books_with_metadata = []

for file in os.listdir(DATA_DIR):
    file_path = os.path.join(DATA_DIR, file)
    book_source = BOOK_MAPPING.get(file, "UNKNOWN")

    if file.endswith(".txt") or file.endswith(".md"):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
            books_with_metadata.append({"text": text, "source": book_source})

    elif file.endswith(".pdf"):
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            books_with_metadata.append({"text": text, "source": book_source})


splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,  
    chunk_overlap=300  
)


all_chunks = []
for book_data in books_with_metadata:
    book_chunks = splitter.split_text(book_data["text"])
    for chunk in book_chunks:
        all_chunks.append({
            "text": chunk,
            "source": book_data["source"]
        })

print(f"Total Chunks: {len(all_chunks)}")
print(f"BNS Chunks: {sum(1 for c in all_chunks if c['source'] == 'BNS')}")
print(f"BNSS Chunks: {sum(1 for c in all_chunks if c['source'] == 'BNSS')}")
print(f"BSA Chunks: {sum(1 for c in all_chunks if c['source'] == 'BSA')}")



print("Loading embedding model...")
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
embedding_model = SentenceTransformer(MODEL_NAME)
print(f"Model loaded. Embedding dimension: {embedding_model.get_sentence_embedding_dimension()}")

def embed_text(text: str):
    """
    Get embedding using local sentence-transformers model
    Returns 1D Python float list for Pinecone
    """
    embedding = embedding_model.encode(text, convert_to_numpy=True)
    return embedding.tolist()



vectors = []

for i, chunk_data in enumerate(all_chunks):
    if i % 100 == 0:
        print(f"Processing chunk {i}/{len(all_chunks)}...")
    vec = embed_text(chunk_data["text"])  
    vectors.append({
        "id": f"chunk-{i}",
        "values": vec,
        "metadata": {
            "text": chunk_data["text"],
            "source": chunk_data["source"]
        }
    })

BATCH_SIZE = 100
total_batches = (len(vectors) + BATCH_SIZE - 1) // BATCH_SIZE

for batch_idx in range(0, len(vectors), BATCH_SIZE):
    batch = vectors[batch_idx:batch_idx + BATCH_SIZE]
    index.upsert(batch)
    print(f"Upserted batch {batch_idx // BATCH_SIZE + 1}/{total_batches} ({len(batch)} vectors)")

print("Pinecone DB build completed successfully!")