# StudyForge Architecture

## Current System

StudyForge is built as an AI learning assistant.

The current flow:

Student
↓
StudyForge Interface
↓
Python Application Logic
↓
AI API
↓
Response
↓
Saved Conversation


## Components

## User Interface

Currently built using Streamlit.

Responsibilities:
- displaying chat interface
- collecting questions
- showing responses
- managing settings


## AI Layer

StudyForge uses an external LLM through an API.

The system creates structured prompts that include:
- subject
- learning depth
- teaching mode
- user question

The goal is not just generating text, but generating explanations suitable for learning.


## Database

SQLite is used to store:

- chats
- messages
- user information

The purpose is maintaining conversation history and building toward personalised learning.


## Future Architecture

The planned architecture:

Frontend:
React + Tailwind

Backend:
FastAPI

Database:
PostgreSQL

AI:
LLM + retrieval systems


The goal is moving from a prototype into a scalable learning platform.
