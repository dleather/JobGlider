import os
from dotenv import load_dotenv
import logging
import sys

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console handler
        logging.FileHandler(os.path.join('logs', 'app.log'))  # File handler
    ]
)
logger = logging.getLogger(__name__)

# Path configurations
BASE_DOCKER_PATH = os.getenv("BASE_DOCKER_PATH", "/app")
BASE_LOCAL_PATH = os.getenv("BASE_LOCAL_PATH", "C:/Users/davle/Dropbox (Personal)")
ROOT_DIR = os.path.abspath(r"C:/Users/davle/Dropbox (Personal)/Jobs 2024")
COVER_LETTERS_DIR = os.path.join(ROOT_DIR, "cover_letters")

# Ensure directories exist
os.makedirs(COVER_LETTERS_DIR, exist_ok=True)
os.makedirs('logs', exist_ok=True)  # Create logs directory if it doesn't exist

# Predefine dependency variables so they can always be imported.
# In a test environment these will remain None, but in production they will be populated.
openai_client = None
notion_client = None
tokenizer = None
model = None

# Only initialize clients and models if not in test environment
if not os.getenv('PYTEST') and not os.getenv('PYTEST_CURRENT_TEST'):
    from openai import OpenAI
    from notion_client import Client
    from transformers import AutoModelForCausalLM, AutoTokenizer
    
    # Initialize OpenAI client
    openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Initialize Notion client
    notion_client = Client(auth=os.getenv('NOTION_API_KEY'))
    
    # Initialize Mistral model and tokenizer
    MODEL_ID = "mistralai/Mistral-7B-v0.1"
    
    try:
        logger.info(f"Loading Mistral model and tokenizer from {MODEL_ID}")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            torch_dtype="auto",
            device_map="auto",
            load_in_8bit=True  # Enable 8-bit quantization to reduce memory usage
        )
        logger.info("Successfully loaded Mistral model and tokenizer")
    except Exception as e:
        logger.error(f"Error loading Mistral model: {str(e)}", exc_info=True)
        raise
