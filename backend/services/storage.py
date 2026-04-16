import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.getenv("SUPABASE_URL", "")
key: str = os.getenv("SUPABASE_ANON_KEY", "")

try:
    if url and key:
        supabase: Client = create_client(url, key)
    else:
        supabase = None
except Exception as e:
    print(f"Supabase init error: {e}")
    supabase = None

def upload_file_to_supabase(bucket: str, file_path: str, file_name: str) -> str:
    """Uploads file to Supabase Storage and returns public URL."""
    if not supabase:
        print("Warning: Supabase client not initialized. Using fallback URL.")
        return f"http://localhost:8000/static/{file_name}" # fallback structure
    
    try:
        with open(file_path, "rb") as f:
            res = supabase.storage.from_(bucket).upload(file_name, f)
            
        return f"{url}/storage/v1/object/public/{bucket}/{file_name}"
    except Exception as e:
        print(f"Upload error: {e}")
        return f"http://localhost:8000/static/{file_name}"
