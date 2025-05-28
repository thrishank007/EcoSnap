# EcoSnap

EcoSnap is a Python-based web application for waste classification and sustainability recommendations. It provides both a user-friendly Gradio interface and a FastAPI backend. Users can upload waste images or enter textual queries to classify waste types and receive eco-friendly tips.

## Features

- 🖼️ Image Upload & Waste Classification  
- 📊 Interactive Gradio UI with Earth-to-Sky theme  
- 🌍 Sustainability recommendations via RAG (Retrieval-Augmented Generation)  
- 🔌 FastAPI backend for programmatic access  
- 🔧 Local FAISS-based vector store with HuggingFace embeddings  

## Tech Stack

- Python 3.x  
- Gradio  
- FastAPI  
- LangChain & HuggingFace Embeddings  
- FAISS vector store  
- Pandas, NumPy, Matplotlib  
- PIL (Pillow)  

## Repository Structure

```
├── app.py            # Gradio UI and front-end logic  
├── model.py          # FastAPI app, RAG setup, and classification API  
├── sustainability_data/
│   └── plastic_general_info.txt  # Sample sustainability docs  
├── faiss_index/      # Saved FAISS index (created at runtime)  
└── requirements.txt  # Python dependencies  
```

## Installation

1. Clone the repository  
   ```bash
   git clone https://github.com/thrishank007/EcoSnap.git
   cd EcoSnap
   ```

2. Create and activate a virtual environment  
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies  
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 1. Run the Gradio UI

```bash
python app.py
```

Open the displayed local URL (e.g., http://localhost:7860) in your browser to interact with the EcoSnap UI.

### 2. Start the FastAPI Backend

```bash
uvicorn model:app --reload
```

By default, the API will run at http://127.0.0.1:8000. Endpoints:

- `POST /classify-image/` – Upload an image to classify waste.  
- `POST /recommend/` – Send a text prompt to get sustainability tips via RAG.

API docs: http://127.0.0.1:8000/docs

## Sustainability Data

On first run, the app generates mock sustainability data under `./sustainability_data/`. You can replace these with your own `.txt` documents:

- Create `.txt` files in `sustainability_data/`
- RAG will ingest them and build/update `faiss_index/`

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Contact

Created by [@thrishank007](https://github.com/thrishank007).  
Feel free to reach out with feedback or questions.
