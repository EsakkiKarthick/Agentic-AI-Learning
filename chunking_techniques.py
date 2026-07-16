from langchain_text_splitters import RecursiveCharacterTextSplitter
import tiktoken
import numpy as np
from langchain_text_splitters import MarkdownHeaderTextSplitter

def fixed_size_chunking(input_data: str, chunk_size: int=100, chunk_overlap: int=20) -> list[str]:
    chunks=[]
    start=0
    while start<len(input_data):
        end=start+chunk_size
        chunks.append(input_data[start:end])
        start= (start + chunk_size) - chunk_overlap
    return chunks

def recurrsive_chunking(input_text: str, chunk_size: int=100, chunk_overlap: int=20) -> list[str]:
    chunks=[]
    splitter = RecursiveCharacterTextSplitter(
        chunk_size,
        chunk_overlap,
        seperators = ["\n\n", "\n", ".", " ", ""],
        length_function = len

    )
    chunks = splitter.split_text(input_text)
    return chunks

def token_chunk(input_text: str, chunk_size: int=100, chunk_overlap: int=20, model = "gpt-4o") -> list[str]:
    chunks=[]
    enc=tiktoken.encoding_for_model(model)
    tokens= enc.encode(input_text)
    start = 0
    while start < len(tokens):
        end= start + chunk_size
        chunk_tokens = tokens[start:end]
        chunks.append(enc.decode(chunk_tokens))
        start += chunk_size - chunk_overlap
    return chunks

def semanctic_chunk(sentences: list[str], embeddings_client, threshold_percentile: int = 90):
    embeds = embeddings_client.embed_documents(sentences)
    embeds = np.array(embeds)

def structure_aware_chunk(input_text: str, headers_to_split: list[str]):
    headers_to_split =[]




