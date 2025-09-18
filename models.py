#!/usr/bin/env python3

from pydantic import BaseModel
from typing import List
from textwrap import dedent

# --------------------------------------------------------------------------------
# Pydantic Models
# --------------------------------------------------------------------------------

class FileToCreate(BaseModel):
    path: str
    content: str

class FileToEdit(BaseModel):
    path: str
    original_snippet: str
    new_snippet: str

