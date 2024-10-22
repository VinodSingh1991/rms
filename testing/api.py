
from fastapi import FastAPI
from checktool import all_leads

app = FastAPI()

# # Allow requests from your React app (adjust this if your frontend runs elsewhere)
@app.get("/api/rm")
async def root():
    #print("Result from the crew", result)
    return all_leads
   
   
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
    