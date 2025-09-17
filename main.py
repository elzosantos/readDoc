from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader 
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from filter_retriever import RedundantFilterRetriever

import argparse  
import langchain

langchain.debug = True



load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument("--load", default="query")
parser.add_argument("--file", default="historia.txt")
parser.add_argument("--task", default="Quem foi Pedro Alvares Cabral?")
args = parser.parse_args()


embedding_function = OpenAIEmbeddings(model="text-embedding-3-large")
chat = ChatOpenAI(model="gpt-4o-mini")
match args.load:
    case "load":
        print("Carregando arquivo...")
        # Criar o splitter
        splitter = CharacterTextSplitter(
            chunk_size=600, 
            chunk_overlap=200, 
            separator="\n"
        )
        # Carregar o arquivo PDF
        loader = TextLoader(args.file, encoding="utf-8")
        docs = loader.load_and_split(splitter)
        db = Chroma.from_documents(
            documents = docs,  
            embedding = embedding_function, 
            persist_directory="./chromadb"
        )
        print("Arquivo carregado com sucesso...")
    case "query":
        print("Executando query...")
        db = Chroma(
            persist_directory="./chromadb", 
            embedding_function=embedding_function
        )
        busca = args.task
        # retriever = db.as_retriever()
        
        retriever = RedundantFilterRetriever(
            embedding=embedding_function,
            chroma=db
        )
        
        chain = RetrievalQA.from_chain_type(
            llm=chat, 
            chain_type="stuff", 
            retriever=retriever
        )
        resultado = chain.invoke(busca)
        print(resultado)
  



 