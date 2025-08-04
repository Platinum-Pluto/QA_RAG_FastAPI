### Features
- RAG support for various file formats. [e.g doc, pdf, csv, xlsx, jpg, jpeg, png, sql, .db and etc]
- OCR-Tesseract support with pytesseract to extract texts from images for context.
- Upload route with multiple files and Query with image supported. [base64 image encoded]
- Multimodal model support which can describe images or analyze diagrams and such from an image.
- Streamlit app for an interactive user experience.
- Docker compose to build container from images support
- Utilizes Langchain graph setup.

# README.md
**Table of Contents**

- [Project Setup] (#project-setup)
- [Fastapi Manual] (#fastapi-manual)
- [Streamlit Manual] (#streamlit-manual)
- [Unit Tests] (#unit-tests)
- [Demonstration Images] (#demonstration-images)

# Project Setup
First clone this git repository using the git command or you can also download the project file.
To clone this repository use the following git command:

`git clone https://github.com/Platinum-Pluto/QA_RAG_FastAPI.git`

Since the images for this project exists in my dockerhub repository you can either pull both of the images required for this project or build the images and create their container in your own PC.
However you need docker desktop installed in your system.
Here is a link to the docker desktop page if you do not have docker installed:

`https://www.docker.com/products/docker-desktop/`

If you want to pull the already built images from my repository then use the following docker command in terminal:

` `
Or,

if you want to build it in your own PC then simply open a terminal in the project folder and run the following docker command:

`docker compose up --build `

This will take a while but it will build the images and start up your container will will start both the FASTapi server in port 8000 and the Streamlit app in port 8501 locally.

If you pull the images from my dockerhub repository then you can navigate to the project folder and open terminal and simple run the following command to start up FASTapi and Streamlit:

`docker compose up`

This is the link to open the FASTapi swagger UI for an interactive experience and tests with the FASTapi server:

`http://localhost:8000/docs#/`

And this is the link to open the Streamlit app:

`http://localhost:8501/`

Copy paste them in the browser search bar.

The Streamlit app communicates with the FASTapi server to send and retrieve data.


After setting up the docker images and container remember to put in the API key, model name and provider name in the .env file and then run `docker compose up` otherwise without these the LLM model will not work.

> ⚠️**Warning:** Currently this project only supports Gemini models for both multimodal support I used Gemini 2.5 flash model so use Gemini api.
> ⚠️**Warning:** If you want to change the model you want to use then open rag.py and change the 
` os.environ["GOOGLE_API_KEY"] = os.getenv("API_KEY") ` 
to the following Langchain supported LLM's then simply copy paste to replace the existing one with any one of the below of which you want to use: 
`os.environ["OPENAI_API_KEY"] = os.getenv("API_KEY")` [Provider in .env will be openai]
`os.environ["ANTHROPIC_API_KEY"] = os.getenv("API_KEY")` [Provider in .env will be anthropic]
`os.environ["GROQ_API_KEY"] = os.getenv("API_KEY")` [Provider in .env will be groq]
`os.environ["COHERE_API_KEY"] = os.getenv("API_KEY")` [Provider in .env will be cohere]
`os.environ["NVIDIA_API_KEY"] = os.getenv("API_KEY")` [Provider in .env will be nvidia]
`os.environ["FIREWORKS_API_KEY"] = os.getenv("API_KEY")` [Provider in .env will be fireworks]
`os.environ["MISTRAL_API_KEY"] = os.getenv("API_KEY")` [Provider in .env will be mistralai]
`os.environ["TOGETHER_API_KEY"] = os.getenv("API_KEY")` [Provider in .env will be together]
`os.environ["XAI_API_KEY"] = os.getenv("API_KEY")` [Provider in .env will be xai]
`os.environ["PPLX_API_KEY"] = os.getenv("API_KEY")` [Provider in .env will be perplexity]

And change the .env model name, api key and provider based on your needs. 

# Fastapi Manual




# Streamlit Manual




# Unit Tests




# Demonstration Images