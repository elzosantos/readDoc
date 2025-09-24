# Sistema de Busca de Documentos com IA

Este projeto implementa um sistema de busca de documentos usando LangChain, ChromaDB e modelos de IA da OpenAI. O sistema permite carregar documentos e fazer consultas inteligentes sobre seu conteúdo.

## Funcionalidades

- **Carregamento de documentos**: Suporte para arquivos de texto (.txt)
- **Busca inteligente**: Utiliza embeddings e Max Marginal Relevance Search para reduzir redundância
- **Interface de linha de comando**: Fácil de usar via terminal
- **Configuração centralizada**: Parâmetros organizados em arquivo de configuração

## Estrutura do Projeto

```
readDoc/
├── main.py                 # Arquivo principal do sistema
├── filter_retriever.py     # Retriever personalizado com filtro de redundância
├── config.py              # Configurações do sistema
├── convert.py             # Utilitário de conversão (legado)
├── main2.py               # Script alternativo (legado)
├── chromadb/              # Banco de dados ChromaDB
├── historia.txt           # Arquivo de exemplo
├── História_do_Brasil.pdf # PDF de exemplo
└── README.md              # Este arquivo
```

## Instalação

1. Clone o repositório ou baixe os arquivos
2. Instale as dependências:
   ```bash
   pip install langchain langchain-openai langchain-community langchain-chroma chromadb python-dotenv
   ```

3. Configure suas chaves da OpenAI no arquivo `.env`:
   ```
   OPENAI_API_KEY=sua_chave_aqui
   ```

## Uso

### Carregar Documentos

Para carregar um arquivo de texto no banco de dados:

```bash
python main.py --load load --file historia.txt
```

### Fazer Consultas

Para fazer uma consulta sobre os documentos carregados:

```bash
python main.py --load query --task "Sua pergunta aqui"
```

### Exemplo Completo

```bash
# 1. Carregar documento
python main.py --load load --file historia.txt

# 2. Fazer consulta
python main.py --load query --task "Quem foi Pedro Alvares Cabral?"
```

## Configuração

As configurações do sistema podem ser ajustadas no arquivo `config.py`:

- **EMBEDDING_MODEL**: Modelo de embedding da OpenAI
- **CHAT_MODEL**: Modelo de chat da OpenAI
- **CHUNK_SIZE**: Tamanho dos chunks de texto
- **CHUNK_OVERLAP**: Sobreposição entre chunks
- **LAMBDA_MULT**: Parâmetro para Max Marginal Relevance Search
- **K_DOCUMENTS**: Número de documentos a retornar

## Arquitetura

### DocumentSearchSystem

Classe principal que gerencia:
- Carregamento de documentos
- Criação do banco de dados ChromaDB
- Execução de consultas

### RedundantFilterRetriever

Retriever personalizado que:
- Utiliza Max Marginal Relevance Search
- Reduz redundância nos resultados
- Melhora a qualidade das respostas

## Dependências

- `langchain`: Framework principal para aplicações de IA
- `langchain-openai`: Integração com modelos da OpenAI
- `langchain-community`: Componentes da comunidade
- `langchain-chroma`: Integração com ChromaDB
- `chromadb`: Banco de dados vetorial
- `python-dotenv`: Gerenciamento de variáveis de ambiente

## Exemplos de Uso

### Perguntas sobre História do Brasil

```bash
python main.py --load query --task "Quando foi descoberto o Brasil?"
python main.py --load query --task "Quais foram as principais capitanias hereditárias?"
python main.py --load query --task "Explique o período colonial brasileiro"
```

### Perguntas sobre Documentos Técnicos

```bash
python main.py --load query --task "Resuma os principais pontos do documento"
python main.py --load query --task "Quais são as conclusões apresentadas?"
```

## Troubleshooting

### Erro de API Key
Certifique-se de que a variável `OPENAI_API_KEY` está configurada no arquivo `.env`.

### Erro de Banco de Dados
Se o banco de dados não existir, execute primeiro o modo `load` para carregar documentos.

### Erro de Memória
Para documentos muito grandes, ajuste `CHUNK_SIZE` e `CHUNK_OVERLAP` no arquivo `config.py`.

## Contribuição

Para contribuir com o projeto:
1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Faça commit das mudanças
4. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
