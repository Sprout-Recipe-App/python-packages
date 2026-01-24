from pydantic import BaseModel, Field


class ProgrammingFileResponse(BaseModel):
    file_content: str = Field(..., description="The entire file content without surrounding quotes!")


class LLMCodeResponse(BaseModel):
    code: str = Field(..., description="The code with it's comments and docstrings in single quotes!")
