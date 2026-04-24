
from fastapi import FastAPI, HTTPException, requests
from pydantic import BaseModel
from typing import List

app = FastAPI()

# ---------------------------
# Pydantic model for a Note
# ---------------------------
class Note(BaseModel):
    title: str
    content: str

notes_db: List[Note] = []

@app.get("/")
def root():
    return {"message":"FastAPI is great!"}

@app.get("/notes", response_model=List[Note])
def getNotes():
    return notes_db


@app.post("/add", response_model=Note)
def add_note(note: Note):
    """
    Adds a new note to memory
    Raises 400 if title already exists
    """
    for n in notes_db:
        if n.title == note.title:
            raise HTTPException(status_code=400, detail="Note with this title already exists")

    notes_db.append(note)
    return note

@app.put("/update/{title}", response_model=Note)
def update_note(title: str, updated_note: Note):
    """
    Updates content of a note by its title
    """
    for idx, n in enumerate(notes_db):
        if n.title == title:
            notes_db[idx] = updated_note
            return updated_note
    raise HTTPException(status_code=404, detail="Note not found")

@app.delete("/delete/{title}")
def delete_note(title: str):
    """
    Deletes a note by its title
    """
    for idx, n in enumerate(notes_db):
        if n.title == title:
            notes_db.pop(idx)
            return {"detail": f"Note '{title}' deleted"}
    raise HTTPException(status_code=404, detail="Note not found")

@app.get("/agent")
def agent(query: str):
    return {"response": notes_agent(query, notes_db)}

# OLLAMA CALL
# ---------------------------
def ask_ollama(prompt: str):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "deepseek-r1:7b",   # or "llama3"
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"]


# ---------------------------
# AGENT LOGIC
# ---------------------------
def notes_agent(query: str, notes_db):
    if not notes_db:
        return "No notes available."

    # Build context from notes
    context = "\n".join([f"{n.title}: {n.content}" for n in notes_db])

    # Prompt
    prompt = f"""
    You are an intelligent productivity agent. You have to execute all of the instructions provided to you.

    User notes:
    {context}

    Task:
    - Understand the notes
    - Answer the query
    - Suggest clear actionable steps

    Query:
    {query}
    """

    # Call model
    return ask_ollama(prompt)