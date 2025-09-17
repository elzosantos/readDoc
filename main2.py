from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader    
from langchain_text_splitters import CharacterTextSplitter


load_dotenv()

# Criar o splitter
splitter = CharacterTextSplitter(
    chunk_size=200, chunk_overlap=0, separator="\n")

# Carregar o arquivo PDF
loader = PyPDFLoader("História_do_Brasil.pdf")
docs = loader.load_and_split(splitter)

for doc in docs:
    print(doc) 
    print("\n")

