
from fastapi import FastAPI
from main import start_app
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5003",
    "http://127.0.0.1:5173"
]

# Define the request body
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

class Imessage(BaseModel):
      message: str
      
# # Allow requests from your React app (adjust this if your frontend runs elsewhere)
@app.post("/api/rm")
async def root(message: Imessage):
    return start_app(message)
   
   
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
    