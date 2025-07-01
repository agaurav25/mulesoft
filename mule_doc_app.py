import streamlit as st
import os
import tempfile
import zipfile
from typing import List, Dict, Any, Tuple
from utils.xml_parser import MuleSoftXMLParser
from utils.dwl_parser import DataWeaveParser
from utils.vector_store import VectorStore
from utils.simple_enhanced_vector_store import SimpleEnhancedVectorStore
from utils.ai_agents import DocumentationAgents
from utils.documentation_generator import DocumentationGenerator
from utils.document_formatter import DocumentFormatter
from utils.document_reader import DocumentReader
from datetime import datetime

# Configure Streamlit page
st.set_page_config(
    page_title="MuleSoft Documentation Generator | Professional AI-Powered Analysis",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://docs.mulesoft.com/',
        'Report a bug': None,
        'About': "# MuleSoft Documentation Generator\n\nProfessional AI-powered documentation generation for MuleSoft integration projects. Built with advanced multi-agent AI systems and semantic search capabilities."
    }
)

# Custom CSS for professional styling with animations and modern design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Main container styling */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1400px;
        font-family: 'Inter', sans-serif;
    }

    /* Global animations */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(30px); }
        to { opacity: 1; transform: translateX(0); }
    }

    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }

    /* Professional Header styling */
    .main-header {
        background: linear-gradient(135deg, #0066cc 0%, #003d7a 50%, #001a33 100%);
        padding: 3rem 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 102, 204, 0.3);
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.8s ease-out;
    }

    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="2" fill="rgba(255,255,255,0.1)"/></svg>') repeat;
        opacity: 0.3;
    }

    .main-header h1 {
        color: white !important;
        margin-bottom: 0.5rem;
        font-size: 3rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        position: relative;
        z-index: 1;
    }

    .main-header .subtitle {
        color: #b3d9ff;
        font-size: 1.3rem;
        margin: 0;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }

    .main-header .badge {
        background: rgba(255, 255, 255, 0.2);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin-top: 1rem;
        display: inline-block;
        font-size: 0.9rem;
        font-weight: 500;
        position: relative;
        z-index: 1;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background-color: #ffffff;
        border-radius: 8px;
        padding: 0.25rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 6px;
        color: #495057;
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        margin: 0;
    }

    .stTabs [aria-selected="true"] {
        background-color: #1f4e79 !important;
        color: white !important;
    }

    /* Professional Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #0066cc 0%, #004499 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 1rem 2rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(0, 102, 204, 0.3);
        position: relative;
        overflow: hidden;
    }

    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }

    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 102, 204, 0.4);
        background: linear-gradient(135deg, #0052a3 0%, #003366 100%);
    }

    .stButton > button:hover::before {
        left: 100%;
    }

    .stButton > button:active {
        transform: translateY(-1px);
        transition: transform 0.1s;
    }

    /* Secondary button styling */
    .stButton > button[kind="secondary"] {
        background: #6c757d;
    }

    /* Enhanced Card styling */
    .info-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8fbff 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0, 102, 204, 0.1);
        border-left: 5px solid #0066cc;
        margin: 1.5rem 0;
        transition: all 0.3s ease;
        animation: slideInRight 0.6s ease-out;
    }

    .info-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 102, 204, 0.15);
    }

    .metric-card {
        background: linear-gradient(145deg, #ffffff 0%, #f0f8ff 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        text-align: center;
        border: 1px solid #e6f3ff;
        transition: all 0.3s ease;
        animation: fadeInUp 0.6s ease-out;
    }

    .metric-card:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 15px 35px rgba(0, 102, 204, 0.12);
    }

    .feature-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8fbff 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        border: 1px solid #e6f3ff;
        margin: 1rem 0;
        transition: all 0.3s ease;
        animation: fadeInUp 0.6s ease-out;
    }

    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 102, 204, 0.15);
        border-color: #0066cc;
    }

    .professional-badge {
        background: linear-gradient(135deg, #0066cc 0%, #004499 100%);
        color: white;
        padding: 0.5rem 1.2rem;
        border-radius: 25px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        display: inline-block;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0, 102, 204, 0.3);
    }

    /* File uploader styling */
    .stFileUploader {
        background: #f8f9fa;
        border: 2px dashed #1f4e79;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
    }

    /* Success/Error message styling */
    .stSuccess {
        background-color: #d1f2eb;
        border: 1px solid #7dcea0;
        border-radius: 8px;
        padding: 1rem;
    }

    .stError {
        background-color: #fadbd8;
        border: 1px solid #e74c3c;
        border-radius: 8px;
        padding: 1rem;
    }

    .stWarning {
        background-color: #fcf3cf;
        border: 1px solid #f39c12;
        border-radius: 8px;
        padding: 1rem;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border-radius: 8px;
        font-weight: 500;
    }

    /* Progress bar styling */
    .stProgress > div > div {
        background: linear-gradient(90deg, #1f4e79 0%, #2c5f8a 100%);
    }

    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e9ecef;
        padding: 0.75rem;
    }

    .stTextInput > div > div > input:focus {
        border-color: #1f4e79;
        box-shadow: 0 0 0 0.2rem rgba(31, 78, 121, 0.25);
    }

    /* Code block styling */
    .stCode {
        border-radius: 8px;
        border: 1px solid #e9ecef;
    }

    /* Enhanced Status indicators */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
        position: relative;
        animation: pulse 2s infinite;
    }

    .status-success {
        background: radial-gradient(circle, #28a745 0%, #20c997 100%);
        box-shadow: 0 0 10px rgba(40, 167, 69, 0.3);
    }

    .status-error {
        background: radial-gradient(circle, #dc3545 0%, #e74c3c 100%);
        box-shadow: 0 0 10px rgba(220, 53, 69, 0.3);
    }

    .status-warning {
        background: radial-gradient(circle, #ffc107 0%, #ffad0e 100%);
        box-shadow: 0 0 10px rgba(255, 193, 7, 0.3);
    }

    /* Loading animations */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 2px solid #f3f3f3;
        border-top: 2px solid #0066cc;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-right: 10px;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Professional toast notifications */
    .toast-success {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(21, 87, 36, 0.1);
        animation: slideInRight 0.5s ease-out;
    }

    .toast-error {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(114, 28, 36, 0.1);
        animation: slideInRight 0.5s ease-out;
    }

    /* Professional charts and metrics */
    .metric-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #0066cc;
        line-height: 1;
        margin-bottom: 0.5rem;
    }

    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

def test_groq_api_key(api_key: str, model: str) -> dict:
    """Test if the Groq API key is valid and working with enhanced error handling"""
    try:
        from groq import Groq

        # Initialize client with timeout
        client = Groq(api_key=api_key)

        # Test with a simple request
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a professional MuleSoft documentation assistant."},
                {"role": "user", "content": "Respond with 'Enterprise API connection established successfully' to confirm connectivity."}
            ],
            max_tokens=20,
            temperature=0.1
        )

        # Check if response is valid
        if response.choices and response.choices[0].message.content:
            return {
                'success': True,
                'model': model,
                'response': response.choices[0].message.content.strip(),
                'usage': {
                    'prompt_tokens': getattr(response.usage, 'prompt_tokens', 0),
                    'completion_tokens': getattr(response.usage, 'completion_tokens', 0),
                    'total_tokens': getattr(response.usage, 'total_tokens', 0)
                }
            }
        else:
            return {
                'success': False,
                'error': 'Invalid response received from API endpoint',
                'suggestion': 'Please check your network connection and try again'
            }

    except Exception as e:
        error_msg = str(e).lower()
        if "401" in error_msg or "unauthorized" in error_msg:
            return {
                'success': False,
                'error': 'Authentication failed - Invalid API key',
                'suggestion': 'Please verify your Groq API key in the Configuration panel'
            }
        elif "rate" in error_msg or "limit" in error_msg:
            return {
                'success': False,
                'error': 'Rate limit exceeded',
                'suggestion': 'Please wait a moment before retrying or upgrade your Groq plan'
            }
        elif "model" in error_msg and "not" in error_msg:
            return {
                'success': False,
                'error': f'Model {model} is not available',
                'suggestion': 'Please select a different model from the dropdown'
            }
        elif "timeout" in error_msg or "connection" in error_msg:
            return {
                'success': False,
                'error': 'Network connection timeout',
                'suggestion': 'Please check your internet connection and try again'
            }
        else:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)[:100]}',
                'suggestion': 'Please contact support if this issue persists'
            }

def initialize_session_state():
    """Initialize session state variables"""
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = None
    if 'vector_store' not in st.session_state:
        st.session_state.vector_store = None
    if 'documentation' not in st.session_state:
        st.session_state.documentation = ""
    if 'agents_initialized' not in st.session_state:
        st.session_state.agents_initialized = False
    if 'agents' not in st.session_state:
        st.session_state.agents = None
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False

def validate_groq_api_key():
    """Validate Groq API key - now handled in sidebar"""
    return True  # Always return True since validation is handled in sidebar

def extract_files_from_zip(zip_file) -> List[Tuple[str, str]]:
    """Extract XML and DWL files from ZIP archive"""
    extracted_files = []

    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            for file_info in zip_ref.filelist:
                if file_info.filename.endswith(('.xml', '.dwl')) and not file_info.is_dir():
                    content = zip_ref.read(file_info.filename).decode('utf-8', errors='ignore')
                    extracted_files.append((file_info.filename, content))
    except Exception as e:
        st.error(f"Error extracting ZIP file: {str(e)}")

    return extracted_files

def process_uploaded_files(uploaded_files: List[Any]) -> Dict[str, List[Dict]]:
    """Process uploaded XML, DWL files, and ZIP archives"""
    results = {
        'flows': [],
        'dwl_scripts': [],
        'errors': []
    }

    xml_parser = MuleSoftXMLParser()
    dwl_parser = DataWeaveParser()

    # Collect all files to process (including from ZIP archives)
    files_to_process = []

    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith('.zip'):
            # Extract files from ZIP
            zip_files = extract_files_from_zip(uploaded_file)
            for filename, content in zip_files:
                files_to_process.append((filename, content))
        else:
            # Regular file
            try:
                content = uploaded_file.read()
                if isinstance(content, bytes):
                    content = content.decode('utf-8', errors='ignore')
                files_to_process.append((uploaded_file.name, content))
            except Exception as e:
                results['errors'].append(f"Error reading {uploaded_file.name}: {str(e)}")

    if not files_to_process:
        return results

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, (filename, content) in enumerate(files_to_process):
        try:
            # Update progress
            progress = (i + 1) / len(files_to_process)
            progress_bar.progress(progress)
            status_text.text(f"Processing {filename}...")

            # Process based on file extension
            if filename.endswith('.xml'):
                flows = xml_parser.parse_xml_content(content, filename)
                results['flows'].extend(flows)
            elif filename.endswith('.dwl'):
                dwl_info = dwl_parser.parse_dwl_content(content, filename)
                results['dwl_scripts'].append(dwl_info)
            else:
                results['errors'].append(f"Unsupported file type: {filename}")

        except Exception as e:
            results['errors'].append(f"Error processing {filename}: {str(e)}")

    progress_bar.progress(1.0)
    status_text.text(f"Processing complete! Processed {len(files_to_process)} files.")

    return results

def display_processing_results(results: Dict[str, List[Dict]]):
    """Display processing results in the UI"""
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #1f4e79; margin: 0;">📊 {len(results['flows'])}</h3>
            <p style="margin: 0; color: #6c757d;">Flows Extracted</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #1f4e79; margin: 0;">🔄 {len(results['dwl_scripts'])}</h3>
            <p style="margin: 0; color: #6c757d;">DWL Scripts</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        error_color = "#dc3545" if len(results['errors']) > 0 else "#28a745"
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: {error_color}; margin: 0;">⚠️ {len(results['errors'])}</h3>
            <p style="margin: 0; color: #6c757d;">Errors</p>
        </div>
        """, unsafe_allow_html=True)

    # Show errors if any
    if results['errors']:
        st.error("Errors encountered:")
        for error in results['errors']:
            st.write(f"• {error}")

    # Show extracted flows
    if results['flows']:
        with st.expander(f"📋 Extracted Flows ({len(results['flows'])})"):
            for flow in results['flows']:
                st.write(f"**{flow['name']}** ({flow['type']}) - {flow['file_name']} - {len(flow.get('components', []))} components")

    # Show DataWeave scripts
    if results['dwl_scripts']:
        with st.expander(f"🔄 DataWeave Scripts ({len(results['dwl_scripts'])})"):
            for script in results['dwl_scripts']:
                st.write(f"**{script['file_name']}** - {script.get('line_count', 0)} lines - Input: {bool(script.get('input_vars'))} - Output: {bool(script.get('output_structure'))}")

def main():
    """Main application function"""
    initialize_session_state()

    # Professional header with enhanced branding
    st.markdown("""
    <div class="main-header">
        <h1>🚀 MuleSoft Documentation Generator</h1>
        <p class="subtitle">Enterprise-Grade AI-Powered Documentation Platform</p>
        <div class="badge">Multi-Agent AI System | Semantic Search | Professional Output</div>
    </div>
    """, unsafe_allow_html=True)

    # Feature highlights bar
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="feature-card" style="text-align: center;">
            <h4 style="color: #0066cc; margin: 0;">🤖 AI-Powered</h4>
            <p style="margin: 0.5rem 0 0 0; color: #6c757d; font-size: 0.9rem;">Multi-agent system for intelligent analysis</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card" style="text-align: center;">
            <h4 style="color: #0066cc; margin: 0;">📊 Semantic Search</h4>
            <p style="margin: 0.5rem 0 0 0; color: #6c757d; font-size: 0.9rem;">Advanced vector-based code exploration</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card" style="text-align: center;">
            <h4 style="color: #0066cc; margin: 0;">📄 Multi-Format</h4>
            <p style="margin: 0.5rem 0 0 0; color: #6c757d; font-size: 0.9rem;">Export to PDF, Word, and Markdown</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="feature-card" style="text-align: center;">
            <h4 style="color: #0066cc; margin: 0;">🏢 Enterprise</h4>
            <p style="margin: 0.5rem 0 0 0; color: #6c757d; font-size: 0.9rem;">Production-ready documentation</p>
        </div>
        """, unsafe_allow_html=True)

    # Validate API key (now handled in sidebar)
    validate_groq_api_key()

    # Enhanced sidebar for configuration
    with st.sidebar:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #0066cc 0%, #004499 100%); 
                    padding: 1.5rem; border-radius: 15px; margin-bottom: 1.5rem; text-align: center;
                    box-shadow: 0 8px 25px rgba(0, 102, 204, 0.3);">
            <h2 style="color: white; margin: 0; font-weight: 700;">⚙️ Configuration Panel</h2>
            <p style="color: #b3d9ff; margin: 0.5rem 0 0 0; font-size: 0.9rem;">Enterprise AI Settings</p>
        </div>
        """, unsafe_allow_html=True)

        # Get API key first
        current_key = os.getenv("GROQ_API_KEY", "")
        api_key_placeholder = "sk-..." if current_key else "Enter your Groq API key"

        groq_api_key = st.text_input(
            "Groq API Key",
            value=current_key,
            type="password",
            placeholder=api_key_placeholder,
            help="Enter your Groq API key. Get one from https://console.groq.com/keys"
        )

        # Configuration status overview
        st.markdown("### 📊 System Status")

        # Create status indicators
        api_configured = bool(groq_api_key)
        files_processed = bool(st.session_state.processed_files)
        agents_ready = bool(st.session_state.agents_initialized)

        status_html = f"""
        <div class="info-card" style="padding: 1rem;">
            <div style="margin-bottom: 0.5rem;">
                <span class="status-indicator {'status-success' if api_configured else 'status-error'}"></span>
                <strong>API Connection</strong>
            </div>
            <div style="margin-bottom: 0.5rem;">
                <span class="status-indicator {'status-success' if files_processed else 'status-warning'}"></span>
                <strong>Files Processed</strong>
            </div>
            <div>
                <span class="status-indicator {'status-success' if agents_ready else 'status-warning'}"></span>
                <strong>AI Agents Ready</strong>
            </div>
        </div>
        """
        st.markdown(status_html, unsafe_allow_html=True)



        # Model selection (moved before API key test)
        st.markdown("### 🤖 Model Settings")
        model_options = [
            "llama3-8b-8192",
            "llama3-70b-8192",
            "mixtral-8x7b-32768",
            "gemma-7b-it"
        ]
        selected_model = st.selectbox(
            "Select Groq Model",
            model_options,
            index=0,
            help="Choose the language model for documentation generation"
        )

        st.markdown("---")

        # Update API key in environment if changed
        if groq_api_key and groq_api_key != current_key:
            os.environ["GROQ_API_KEY"] = groq_api_key
            st.success("✅ API key updated!")

        # API key status and test functionality
        if groq_api_key:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown('<span class="status-indicator status-success"></span>**API key configured**', unsafe_allow_html=True)
            with col2:
                if st.button("🧪 Test", key="test_api_key", help="Test API key connection"):
                    with st.spinner("Testing API key..."):
                        test_result = test_groq_api_key(groq_api_key, selected_model)
                        if test_result['success']:
                            st.success(f"✅ API key works! Model: {test_result['model']}")
                        else:
                            st.error(f"❌ API key test failed: {test_result['error']}")
        else:
            st.markdown('<span class="status-indicator status-error"></span>**API key required**', unsafe_allow_html=True)

        st.markdown("---")

        # Temperature setting
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.1,
            help="Lower values for more focused output, higher for more creative"
        )

        # Max tokens
        max_tokens = st.number_input(
            "Max Tokens",
            min_value=100,
            max_value=4000,value=1000,
            help="Maximum tokens for AI responses"
        )

        st.markdown("---")

        # Vector Store Configuration
        st.markdown("### 🔍 Vector Store Settings")

        use_enhanced_vectorstore = st.checkbox(
            "Use Enhanced Vector Store",
            value=True,
            help="Enable TF-IDF embeddings and advanced chunking for large files"
        )

        if use_enhanced_vectorstore:
            use_flow_chunking = st.checkbox(
                "Use Flow-Level Chunking",
                value=True,
                help="Enable intelligent chunking based on MuleSoft flow structure and DataWeave sections"
            )

            chunk_size = st.slider(
                "Chunk Size",
                min_value=500,
                max_value=2000,
                value=1000,
                step=100,
                help="Size of text chunks for processing large files"
            )

            chunk_overlap = st.slider(
                "Chunk Overlap",
                min_value=50,
                max_value=500,
                value=200,
                step=50,
                help="Overlap between chunks to maintain context"
            )

            if use_flow_chunking:
                st.info("🔧 Flow-level chunking preserves logical structure of MuleSoft components and DataWeave sections")
        else:
            chunk_size = 1000
            chunk_overlap = 200
            use_flow_chunking = False

    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["📁 File Upload", "🔍 Semantic Search", "📄 Documentation", "🤖 Agent Management"])

    with tab1:
        st.markdown("## 📁 Project File Upload")

        # Professional upload section
        st.markdown("""
        <div class="info-card">
            <h4 style="color: #0066cc; margin-top: 0;">📋 Supported File Types</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                <div>
                    <div class="professional-badge">XML Files</div>
                    <p style="margin: 0.5rem 0; font-size: 0.9rem;">MuleSoft configuration files with flows and sub-flows</p>
                </div>
                <div>
                    <div class="professional-badge">DWL Scripts</div>
                    <p style="margin: 0.5rem 0; font-size: 0.9rem;">DataWeave transformation scripts</p>
                </div>
            </div>
            <div style="margin-top: 1rem;">
                <div class="professional-badge">ZIP Archives</div>
                <p style="margin: 0.5rem 0; font-size: 0.9rem;">Complete MuleSoft projects with multiple files</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Upload statistics if files are already processed
        if st.session_state.processed_files:
            flows_count = len(st.session_state.processed_files.get('flows', []))
            dwl_count = len(st.session_state.processed_files.get('dwl_scripts', []))
            errors_count = len(st.session_state.processed_files.get('errors', []))

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-number">{flows_count}</div>
                    <div class="metric-label">Flows Processed</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-number">{dwl_count}</div>
                    <div class="metric-label">DWL Scripts</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                error_color = "#dc3545" if errors_count > 0 else "#28a745"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-number" style="color: {error_color};">{errors_count}</div>
                    <div class="metric-label">Issues Found</div>
                </div>
                """, unsafe_allow_html=True)

        # File uploader with ZIP support
        uploaded_files = st.file_uploader(
            "Choose XML, DWL files, or ZIP archives",
            type=['xml', 'dwl', 'zip'],
            accept_multiple_files=True,
            help="Select MuleSoft XML files, DataWeave scripts, or ZIP archives containing your project files"
        )

        # Professional tips section
        st.markdown("""
        <div class="info-card">
            <h4 style="color: #0066cc; margin-top: 0;">💡 Professional Tips</h4>
            <ul style="margin: 0; padding-left: 1.2rem;">
                <li><strong>Bulk Processing:</strong> Upload ZIP archives to analyze complete MuleSoft projects efficiently</li>
                <li><strong>Large Files:</strong> Advanced chunking automatically handles complex configurations</li>
                <li><strong>File Organization:</strong> Group related files together for comprehensive analysis</li>
                <li><strong>Best Practice:</strong> Include both XML configs and DWL scripts for complete documentation</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        if uploaded_files:
            st.success(f"📁 {len(uploaded_files)} files uploaded")

            if st.button("🚀 Process Files", type="primary"):
                with st.spinner("Processing files and initializing AI agents..."):
                    # Process files
                    results = process_uploaded_files(uploaded_files)
                    st.session_state.processed_files = results

                    # Display results
                    display_processing_results(results)

                    # Initialize vector store and agents
                    if results['flows'] or results['dwl_scripts']:
                        try:
                            # Initialize vector store based on user preference
                            if use_enhanced_vectorstore:
                                vector_store = SimpleEnhancedVectorStore(
                                    chunk_size=chunk_size,
                                    chunk_overlap=chunk_overlap,
                                    use_flow_chunking=use_flow_chunking
                                )
                                chunking_type = "Flow-Level" if use_flow_chunking else "Text-Based"
                                st.info(f"📊 Using Enhanced Vector Store with {chunking_type} chunking ({chunk_size} char chunks, {chunk_overlap} char overlap)")
                            else:
                                vector_store = VectorStore()
                                st.info("📊 Using Basic Vector Store")

                            # Add flows to vector store
                            for flow in results['flows']:
                                vector_store.add_flow(flow)

                            # Add DWL scripts to vector store
                            for script in results['dwl_scripts']:
                                vector_store.add_dwl_script(script)

                            st.session_state.vector_store = vector_store

                            # Display vector store statistics
                            if use_enhanced_vectorstore:
                                stats = vector_store.get_statistics()
                                chunking_info = []
                                if stats.get('chunking_strategies'):
                                    strategies = stats['chunking_strategies']
                                    if strategies.get('flow_level', 0) > 0:
                                        chunking_info.append(f"{strategies['flow_level']} flow-level")
                                    if strategies.get('dwl_level', 0) > 0:
                                        chunking_info.append(f"{strategies['dwl_level']} DWL-level")
                                    if strategies.get('text_based', 0) > 0:
                                        chunking_info.append(f"{strategies['text_based']} text-based")

                                chunking_details = f" ({', '.join(chunking_info)} chunks)" if chunking_info else ""
                                st.success(f"✅ Enhanced Vector Store initialized: {stats['total_chunks']} chunks, {stats['unique_flows']} flows, {stats['unique_dwl_scripts']} DWL scripts{chunking_details}")

                                # Display chunk characteristics if available
                                if stats.get('chunk_characteristics'):
                                    characteristics = list(stats['chunk_characteristics'].keys())[:5]  # Show top 5
                                    if characteristics:
                                        st.info(f"🔍 Detected patterns: {', '.join(characteristics)}")

                            # Initialize AI agents
                            if groq_api_key:
                                try:
                                    agents = DocumentationAgents(
                                        groq_api_key=groq_api_key,
                                        model=selected_model,
                                        temperature=temperature,
                                        max_tokens=max_tokens
                                    )
                                    st.session_state.agents = agents
                                    st.session_state.agents_initialized = True
                                except Exception as e:
                                    st.error(f"Failed to initialize AI agents: {str(e)}")
                                    st.session_state.agents_initialized = False
                            else:
                                st.warning("Please configure your Groq API key in the sidebar first.")
                                st.session_state.agents_initialized = False

                            st.session_state.processing_complete = True
                            st.success("✅ Files processed and AI agents initialized successfully!")

                        except Exception as e:
                            st.error(f"Error initializing systems: {str(e)}")
                            st.session_state.processing_complete = False

    with tab2:
        st.markdown("## 💬 Chat with Your Codebase")

        st.markdown("""
        <div class="info-card">
            <p><strong>AI-Powered Conversations:</strong> Chat naturally with your MuleSoft project. Ask questions, explore patterns, and get intelligent insights about your flows and transformations.</p>
        </div>
        """, unsafe_allow_html=True)

        # Check if processing is complete
        if not st.session_state.processing_complete:
            st.warning("⚠️ Please upload and process files first in the File Upload tab.")
            # Debug information
            with st.expander("Debug Information", expanded=False):
                st.write("**Session State Debug:**")
                st.write(f"- Processing Complete: {st.session_state.processing_complete}")
                st.write(f"- Vector Store: {st.session_state.vector_store is not None}")
                st.write(f"- Processed Files: {st.session_state.processed_files is not None}")
                st.write(f"- AI Agents: {getattr(st.session_state, 'agents', None) is not None}")
                if st.session_state.processed_files:
                    st.write(f"- Flows: {len(st.session_state.processed_files.get('flows', []))}")
                    st.write(f"- DWL Scripts: {len(st.session_state.processed_files.get('dwl_scripts', []))}")
        else:
            # Initialize chat history with professional welcome
            if 'chat_history' not in st.session_state:
                st.session_state.chat_history = []
                # Add professional welcome message
                if st.session_state.processed_files:
                    flows_count = len(st.session_state.processed_files.get('flows', []))
                    dwl_count = len(st.session_state.processed_files.get('dwl_scripts', []))
                    welcome_msg = f"""🚀 **Welcome to your MuleSoft AI Assistant!**

I've successfully analyzed your integration project and I'm ready to help you explore it:

📊 **Project Overview:**
• **{flows_count}** flows and sub-flows processed
• **{dwl_count}** DataWeave transformation scripts analyzed
• Advanced semantic search enabled
• Multi-agent AI system active

🎯 **What I can help you with:**
• Architectural analysis and best practices
• Integration patterns and data flows
• Error handling strategies
• Performance optimization suggestions
• Code quality assessments

Feel free to ask me anything about your MuleSoft project!"""
                    st.session_state.chat_history.append({"role": "assistant", "content": welcome_msg})

            # Chat interface container
            chat_container = st.container()

            with chat_container:
                # Display chat history with proper styling
                for i, message in enumerate(st.session_state.chat_history):
                    if message["role"] == "user":
                        st.markdown(f"""
                        <div style="display: flex; justify-content: flex-end; margin: 1rem 0;">
                            <div style="background: linear-gradient(90deg, #1f4e79 0%, #2c5f8a 100%); 
                                        color: white; padding: 1rem; border-radius: 18px 18px 4px 18px; 
                                        max-width: 70%; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                                <strong>You:</strong><br>{message["content"]}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="display: flex; justify-content: flex-start; margin: 1rem 0;">
                            <div style="background: #f8f9fa; border: 1px solid #e9ecef; 
                                        padding: 1rem; border-radius: 18px 18px 18px 4px; 
                                        max-width: 70%; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                                <strong>🤖 Assistant:</strong><br>{message["content"]}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

            # Input area at the bottom
            st.markdown("---")

            # Two-column layout for input and suggestions
            col1, col2 = st.columns([3, 1])

            with col1:
                # Chat input
                user_input = st.text_input(
                    "Type your message...",
                    placeholder="Ask me anything about your MuleSoft project...",
                    key="chat_input",
                    label_visibility="collapsed"
                )

                # Send button and clear chat
                input_col1, input_col2, input_col3 = st.columns([2, 1, 1])
                with input_col1:
                    send_clicked = st.button("💬 Send", type="primary", use_container_width=True)
                with input_col2:
                    if st.button("🔄 Clear Chat", use_container_width=True):
                        st.session_state.chat_history = []
                        flows_count = len(st.session_state.processed_files.get('flows', []))
                        dwl_count = len(st.session_state.processed_files.get('dwl_scripts', []))
                        welcome_msg = f"👋 Hello! I'm your MuleSoft codebase assistant. I've analyzed your project with {flows_count} flows and {dwl_count} DataWeave scripts. What would you like to know?"
                        st.session_state.chat_history.append({"role": "assistant", "content": welcome_msg})
                        st.rerun()
                with input_col3:
                    if st.button("📊 Stats", use_container_width=True):
                        if st.session_state.vector_store:
                            stats = st.session_state.vector_store.get_statistics()
                            stats_msg = f"📈 **Codebase Statistics:**\n\n"
                            stats_msg += f"• **Total Documents:** {stats.get('total_documents', 0)}\n"
                            stats_msg += f"• **Flows:** {stats.get('unique_flows', stats.get('total_flows', 0))}\n"
                            stats_msg += f"• **DataWeave Scripts:** {stats.get('unique_dwl_scripts', stats.get('total_dwl_scripts', 0))}\n"
                            if stats.get('total_chunks'):
                                stats_msg += f"• **Chunks:** {stats['total_chunks']}\n"
                            if stats.get('vocabulary_size'):
                                stats_msg += f"• **Vocabulary Size:** {stats['vocabulary_size']}\n"
                            st.session_state.chat_history.append({"role": "assistant", "content": stats_msg})
                            st.rerun()

            with col2:
                # Quick action buttons
                st.markdown("**💡 Quick Actions:**")

                quick_actions = [
                    ("🏗️ Overview", "Give me an overview of this MuleSoft project"),
                    ("🔗 APIs", "What APIs and endpoints are exposed?"),
                    ("⚠️ Errors", "How is error handling implemented?"),
                    ("🔄 Transforms", "What data transformations are performed?"),
                    ("🗄️ Database", "How does this connect to databases?"),
                    ("🔒 Security", "What security measures are in place?")
                ]

                for label, query in quick_actions:
                    if st.button(label, key=f"quick_{hash(query)}", use_container_width=True, type="secondary"):
                        st.session_state.chat_history.append({"role": "user", "content": query})
                        # Process the query
                        with st.spinner("🤔 Thinking..."):
                            try:
                                if st.session_state.vector_store and st.session_state.vector_store.documents:
                                    search_results = st.session_state.vector_store.semantic_search(query, k=5)

                                    if st.session_state.agents_initialized and st.session_state.agents and search_results:
                                        answer = st.session_state.agents.answer_question(query, search_results)
                                        st.session_state.chat_history.append({"role": "assistant", "content": answer})
                                    elif search_results:
                                        # Fallback response with search results
                                        response = f"I found {len(search_results)} relevant components:\n\n"
                                        for i, result in enumerate(search_results[:3], 1):
                                            metadata = result['metadata']
                                            response += f"**{i}. {metadata.get('name', 'Unknown')}** ({metadata.get('type', 'unknown')})\n"
                                            response += f"File: {metadata.get('file_name', 'Unknown')}\n"
                                            response += f"Preview: {result['content'][:150]}...\n\n"
                                        st.session_state.chat_history.append({"role": "assistant", "content": response})
                                    else:
                                        st.session_state.chat_history.append({"role": "assistant", "content": "I couldn't find specific information about that topic in your codebase. Try rephrasing your question or asking about something more specific."})
                                else:
                                    st.session_state.chat_history.append({"role": "assistant", "content": "Please process your files first to enable search capabilities."})
                            except Exception as e:
                                st.session_state.chat_history.append({"role": "assistant", "content": f"I encountered an error while searching: {str(e)}"})
                        st.rerun()

            # Handle user input
            if send_clicked and user_input.strip():
                # Add user message to chat
                st.session_state.chat_history.append({"role": "user", "content": user_input})

                # Process the query
                with st.spinner("🤔 Thinking..."):
                    try:
                        if st.session_state.vector_store and st.session_state.vector_store.documents:
                            search_results = st.session_state.vector_store.semantic_search(user_input, k=5)

                            if st.session_state.agents_initialized and st.session_state.agents and search_results:
                                try:
                                    answer = st.session_state.agents.answer_question(user_input, search_results)
                                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                                except Exception as ai_error:
                                    # Fallback to search results if AI fails
                                    response = f"I found {len(search_results)} relevant components, but couldn't generate a detailed analysis:\n\n"
                                    for i, result in enumerate(search_results[:3], 1):
                                        metadata = result['metadata']
                                        response += f"**{i}. {metadata.get('name', 'Unknown')}** ({metadata.get('type', 'unknown')})\n"
                                        response += f"File: {metadata.get('file_name', 'Unknown')}\n"
                                        response += f"Relevance Score: {result['score']:.3f}\n\n"
                                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                            elif search_results:
                                # Fallback response with search results
                                response = f"I found {len(search_results)} relevant components:\n\n"
                                for i, result in enumerate(search_results[:3], 1):
                                    metadata = result['metadata']
                                    response += f"**{i}. {metadata.get('name', 'Unknown')}** ({metadata.get('type', 'unknown')})\n"
                                    response += f"File: {metadata.get('file_name', 'Unknown')}\n"
                                    response += f"Preview: {result['content'][:150]}...\n\n"
                                response += "\n💡 *Tip: For detailed AI analysis, ensure your API key is configured in the sidebar.*"
                                st.session_state.chat_history.append({"role": "assistant", "content": response})
                            else:
                                st.session_state.chat_history.append({"role": "assistant", "content": "I couldn't find specific information about that in your codebase. Could you try asking in a different way or be more specific about what you're looking for?"})
                        else:
                            st.session_state.chat_history.append({"role": "assistant", "content": "Please upload and process your MuleSoft files first in the File Upload tab."})
                    except Exception as e:
                        st.session_state.chat_history.append({"role": "assistant", "content": f"I encountered an error while processing your request: {str(e)}"})

                # Clear input and refresh
                st.session_state.chat_input = ""
                st.rerun()

    with tab3:
        st.markdown("## 📄 Generate Documentation")

        st.markdown("""
        <div class="info-card">
            <p><strong>AI-Powered Documentation:</strong> Create comprehensive technical documentation for your MuleSoft project with automated analysis and structured output.</p>
        </div>
        """, unsafe_allow_html=True)

        # Check if processing is complete
        if not st.session_state.processing_complete:
            st.warning("⚠️ Please upload and process files first in the File Upload tab.")
            # Debug information
            with st.expander("Debug Information", expanded=False):
                st.write("**Session State Debug:**")
                st.write(f"- Processing Complete: {st.session_state.processing_complete}")
                st.write(f"- Vector Store: {st.session_state.vector_store is not None}")
                st.write(f"- Processed Files: {st.session_state.processed_files is not None}")
                st.write(f"- AI Agents: {getattr(st.session_state, 'agents', None) is not None}")
                if st.session_state.processed_files:
                    st.write(f"- Flows: {len(st.session_state.processed_files.get('flows', []))}")
                    st.write(f"- DWL Scripts: {len(st.session_state.processed_files.get('dwl_scripts', []))}")
        else:
            col1, col2 = st.columns([2, 1])

            with col1:
                # Add documentation type selection
                doc_type = st.selectbox(
                    "Select Documentation Type:",
                    ["Standard AI Documentation", "Custom Prompt-Based Documentation"],
                    help="Choose between standard AI-generated documentation or custom prompt-based analysis"
                )

                if doc_type == "Custom Prompt-Based Documentation":
                    st.info("📝 Upload your custom Word document prompts for specialized documentation generation")

                    # File uploader for prompt documents
                    prompt_files = st.file_uploader(
                        "Upload Prompt Documents (.docx or .txt)",
                        type=['docx', 'txt'],
                        accept_multiple_files=True,
                        help="Upload Word documents or text files containing your custom prompts"
                    )

                    if prompt_files and st.button("🚀 Generate Custom Documentation", type="primary"):
                        if not st.session_state.processed_files:
                            st.error("❌ Please process project files first!")
                        else:
                            with st.spinner("Generating custom prompt-based documentation..."):
                                try:
                                    # Save uploaded files temporarily and read them
                                    doc_reader = DocumentReader()
                                    prompts = []

                                    for uploaded_file in prompt_files:
                                        # Save file temporarily
                                        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                                            tmp_file.write(uploaded_file.getvalue())
                                            tmp_file_path = tmp_file.name

                                        try:
                                            if uploaded_file.name.endswith('.docx'):
                                                content = doc_reader.read_docx_file(tmp_file_path)
                                                if content:
                                                    prompts.append(content)
                                            elif uploaded_file.name.endswith('.txt'):
                                                with open(tmp_file_path, 'r', encoding='utf-8') as f:
                                                    prompts.append(f.read())
                                        finally:
                                            os.unlink(tmp_file_path)

                                    if prompts:
                                        # Generate prompt-based documentation
                                        from utils.document_reader import PromptBasedDocumentationGenerator
                                        prompt_generator = PromptBasedDocumentationGenerator(prompts)

                                        dwl_scripts = st.session_state.processed_files.get('dwl_scripts', [])
                                        if dwl_scripts:
                                            documentation = prompt_generator.generate_documentation_with_prompts(dwl_scripts)

                                            st.success("✅ Custom documentation generated successfully!")

                                            # Display documentation
                                            st.markdown("### 📄 Custom Generated Documentation")
                                            st.markdown(documentation)

                                            # Download button
                                            st.download_button(
                                                label="💾 Download Custom Documentation (Markdown)",
                                                data=documentation,
                                                file_name=f"custom_dwl_documentation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                                                mime="text/markdown",
                                                use_container_width=True
                                            )
                                        else:
                                            st.warning("⚠️ No DataWeave scripts found in the analysis results!")
                                    else:
                                        st.error("❌ Could not read prompt files. For .docx files, make sure python-docx is installed.")

                                except Exception as e:
                                    st.error(f"❌ Custom documentation generation failed: {str(e)}")
                                    st.exception(e)

                else:
                    # Standard documentation generation
                    if st.button("📝 Generate Documentation", type="primary"):
                        with st.spinner("Generating comprehensive documentation..."):
                            try:
                                # Generate documentation
                                doc_generator = DocumentationGenerator(st.session_state.agents)
                                documentation = doc_generator.generate_full_documentation(
                                    st.session_state.processed_files
                                )

                                st.session_state.documentation = documentation
                                st.success("✅ Documentation generated successfully!")

                            except Exception as e:
                                st.error(f"Documentation generation error: {str(e)}")

            with col2:
                if st.session_state.documentation:
                    st.markdown("**📥 Download Options:**")

                    # Initialize document formatter
                    formatter = DocumentFormatter()

                    # Enhanced markdown content
                    formatted_content = formatter.create_formatted_markdown(st.session_state.documentation)

                    # Markdown download
                    st.download_button(
                        label="📄 Markdown (.md)",
                        data=formatted_content,
                        file_name="mulesoft_documentation.md",
                        mime="text/markdown",
                        use_container_width=True
                    )

                    # PDF download
                    try:
                        pdf_data = formatter.export_to_pdf(formatted_content)
                        st.download_button(
                            label="📕 PDF Document",
                            data=pdf_data,
                            file_name="mulesoft_documentation.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"PDF generation error: {str(e)}")

                    # Word download
                    try:
                        word_data = formatter.export_to_word(formatted_content)
                        st.download_button(
                            label="📘 Word Document",
                            data=word_data,
                            file_name="mulesoft_documentation.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Word generation error: {str(e)}")

                    # Format preview options
                    st.markdown("---")
                    st.markdown("**🎨 Format Preview:**")

                    preview_col1, preview_col2 = st.columns(2)
                    with preview_col1:
                        if st.button("👀 PDF Preview", use_container_width=True, type="secondary"):
                            try:
                                pdf_data = formatter.export_to_pdf(formatted_content)
                                st.info(f"📄 PDF generated successfully! Size: {len(pdf_data):,} bytes")
                                st.success("✅ PDF is ready for download above")
                            except Exception as e:
                                st.error(f"PDF preview error: {str(e)}")

                    with preview_col2:
                        if st.button("👀 Word Preview", use_container_width=True, type="secondary"):
                            try:
                                word_data = formatter.export_to_word(formatted_content)
                                st.info(f"📝 Word document generated successfully! Size: {len(word_data):,} bytes")
                                st.success("✅ Word document is ready for download above")
                            except Exception as e:
                                st.error(f"Word preview error: {str(e)}")

            # Professional export format information
            st.markdown("---")
            st.markdown("### 📋 Professional Export Formats")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("""
                <div class="feature-card">
                    <h4 style="color: #0066cc;">📄 Markdown</h4>
                    <div class="professional-badge">Developer Friendly</div>
                    <ul style="margin: 1rem 0 0 0; padding-left: 1.2rem; font-size: 0.9rem;">
                        <li>GitHub/GitLab compatible</li>
                        <li>Version control optimized</li>
                        <li>Raw syntax access</li>
                        <li>Wiki integration ready</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown("""
                <div class="feature-card">
                    <h4 style="color: #0066cc;">📕 PDF</h4>
                    <div class="professional-badge">Executive Ready</div>
                    <ul style="margin: 1rem 0 0 0; padding-left: 1.2rem; font-size: 0.9rem;">
                        <li>Enterprise branding</li>
                        <li>Professional layouts</li>
                        <li>Print-optimized design</li>
                        <li>Stakeholder presentations</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown("""
                <div class="feature-card">
                    <h4 style="color: #0066cc;">📘 Word</h4>
                    <div class="professional-badge">Collaboration Ready</div>
                    <ul style="margin: 1rem 0 0 0; padding-left: 1.2rem; font-size: 0.9rem;">
                        <li>Fully editable content</li>
                        <li>Corporate templates</li>
                        <li>Team collaboration</li>
                        <li>Review workflows</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

            # Display generated documentation
            if st.session_state.documentation:
                st.markdown("---")
                st.markdown("### 📖 Generated Documentation")

                # Add a preview toggle
                show_preview = st.checkbox("Show Full Documentation Preview", value=False)

                if show_preview:
                    st.markdown(st.session_state.documentation)
                else:
                    # Show first 2000 characters with expand option
                    preview_text = st.session_state.documentation[:2000]
                    if len(st.session_state.documentation) > 2000:
                        preview_text += "\n\n*... (content truncated for preview)*"

                    st.markdown(preview_text)

                    if len(st.session_state.documentation) > 2000:
                        st.info(f"📊 Full documentation: {len(st.session_state.documentation):,} characters, {len(st.session_state.documentation.split())} words")

    with tab4:
        st.markdown("## 🤖 Multi-Agent System Management")

        st.markdown("""
        <div class="info-card">
            <p><strong>AI Agent Orchestration:</strong> Manage and configure the multi-agent system that powers your documentation generation. Each agent has specialized roles and can be customized for your specific needs.</p>
        </div>
        """, unsafe_allow_html=True)

        # Check if agents are initialized
        if not st.session_state.agents_initialized or not st.session_state.agents:
            st.warning("⚠️ AI agents are not initialized. Please configure your API key and process files first.")

            # Show agent initialization status
            col1, col2 = st.columns(2)
            with col1:
                api_key_status = "✅ Configured" if groq_api_key else "❌ Missing"
                st.markdown(f"**API Key Status:** {api_key_status}")
            with col2:
                files_status = "✅ Processed" if st.session_state.processed_files else "❌ No files"
                st.markdown(f"**Files Status:** {files_status}")

            if st.button("🔄 Initialize Agents", type="primary"):
                if groq_api_key and st.session_state.processed_files:
                    try:
                        with st.spinner("Initializing AI agents..."):
                            agents = DocumentationAgents(
                                groq_api_key=groq_api_key,
                                model=selected_model,
                                temperature=temperature,
                                max_tokens=max_tokens
                            )
                            st.session_state.agents = agents
                            st.session_state.agents_initialized = True
                            st.success("✅ AI agents initialized successfully!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Failed to initialize agents: {str(e)}")
                else:
                    st.error("Please configure API key and process files first.")
        else:
            # Agent status and configuration
            st.markdown("### 🎯 Agent Status")

            # Display agent status cards
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("""
                <div class="metric-card">
                    <h4 style="color: #1f4e79; margin: 0;">📝 Summarizer</h4>
                    <p style="margin: 0; color: #28a745;">Active</p>
                    <small style="color: #6c757d;">Creates technical summaries</small>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown("""
                <div class="metric-card">
                    <h4 style="color: #1f4e79; margin: 0;">🔍 Analyzer</h4>
                    <p style="margin: 0; color: #28a745;">Active</p>
                    <small style="color: #6c757d;">Analyzes architecture patterns</small>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown("""
                <div class="metric-card">
                    <h4 style="color: #1f4e79; margin: 0;">🎭 Coordinator</h4>
                    <p style="margin: 0; color: #28a745;">Active</p>
                    <small style="color: #6c757d;">Orchestrates documentation</small>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")

            # Agent Configuration
            st.markdown("### ⚙️ Agent Configuration")

            config_tab1, config_tab2, config_tab3 = st.tabs(["📝 Summarizer Agent", "🔍 Analyzer Agent", "🎭 Coordinator Agent"])

            with config_tab1:
                st.markdown("#### 📝 Summarizer Agent Configuration")
                st.markdown("**Role:** Creates clear, comprehensive summaries of MuleSoft flows and DataWeave transformations")

                # Current prompt display
                current_summarizer_prompt = st.session_state.agents.summarizer.system_message

                with st.expander("View Current System Prompt", expanded=False):
                    st.code(current_summarizer_prompt, language="text")

                # Editable prompt
                st.markdown("**Custom System Prompt:**")
                new_summarizer_prompt = st.text_area(
                    "Edit Summarizer System Prompt",
                    value=current_summarizer_prompt,
                    height=200,
                    key="summarizer_prompt",
                    help="Define how the Summarizer agent should behave and what it should focus on"
                )

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Update Summarizer Prompt", type="primary"):
                        try:
                            st.session_state.agents.summarizer.system_message = new_summarizer_prompt
                            st.success("✅ Summarizer prompt updated successfully!")
                        except Exception as e:
                            st.error(f"Error updating prompt: {str(e)}")

                with col2:
                    if st.button("🔄 Reset to Default"):
                        # Reset to default prompt
                        default_prompt = """You are a technical documentation expert specializing in MuleSoft integration platforms. 
Your role is to create clear, comprehensive summaries of MuleSoft flows and DataWeave transformations.

When summarizing MuleSoft flows:
- Identify the business purpose and trigger mechanism
- Describe the main data flow and transformations
- Highlight error handling and validation logic
- Note external system integrations
- Explain any complex routing or conditional logic

When summarizing DataWeave scripts:
- Describe the input and output data structures
- Explain the transformation logic in business terms
- Identify key mappings and calculations
- Note any complex functions or custom logic

Always provide summaries that are:
- Technical but accessible to both developers and business analysts
- Structured with clear sections
- Focused on business value and technical implementation
- Include relevant technical details without overwhelming non-technical readers"""
                        st.session_state.agents.summarizer.system_message = default_prompt
                        st.success("✅ Reset to default prompt!")
                        st.rerun()

                # Test the agent
                st.markdown("**Test Summarizer Agent:**")
                if st.session_state.processed_files and st.session_state.processed_files['flows']:
                    test_flow = st.selectbox(
                        "Select a flow to test summarization:",
                        options=range(len(st.session_state.processed_files['flows'])),
                        format_func=lambda x: f"{st.session_state.processed_files['flows'][x]['name']} ({st.session_state.processed_files['flows'][x]['type']})"
                    )

                    if st.button("🧪 Test Summarizer"):
                        with st.spinner("Testing summarizer agent..."):
                            try:
                                flow_data = st.session_state.processed_files['flows'][test_flow]
                                summary = st.session_state.agents.summarize_flow(flow_data)
                                st.markdown("**Generated Summary:**")
                                st.markdown(summary)
                            except Exception as e:
                                st.error(f"Error testing summarizer: {str(e)}")

            with config_tab2:
                st.markdown("#### 🔍 Analyzer Agent Configuration")
                st.markdown("**Role:** Analyzes MuleSoft projects for architecture patterns, best practices, and technical insights")

                # Current prompt display
                current_analyzer_prompt = st.session_state.agents.analyzer.system_message

                with st.expander("View Current System Prompt", expanded=False):
                    st.code(current_analyzer_prompt, language="text")

                # Editable prompt
                st.markdown("**Custom System Prompt:**")
                new_analyzer_prompt = st.text_area(
                    "Edit Analyzer System Prompt",
                    value=current_analyzer_prompt,
                    height=200,
                    key="analyzer_prompt",
                    help="Define how the Analyzer agent should analyze code and what patterns to look for"
                )

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Update Analyzer Prompt", type="primary"):
                        try:
                            st.session_state.agents.analyzer.system_message = new_analyzer_prompt
                            st.success("✅ Analyzer prompt updated successfully!")
                        except Exception as e:
                            st.error(f"Error updating prompt: {str(e)}")

                with col2:
                    if st.button("🔄 Reset to Default", key="reset_analyzer"):
                        # Reset to default prompt
                        default_prompt = """You are a MuleSoft architecture analyst with deep expertise in integration patterns and best practices.
Your role is to analyze MuleSoft projects for:

Technical Analysis:
- Integration patterns used (point-to-point, publish-subscribe, message routing, etc.)
- Error handling strategies and fault tolerance
- Performance considerations and bottlenecks
- Security implementations and data protection
- Compliance with MuleSoft best practices

Architectural Insights:
- System dependencies and coupling
- Data flow complexity and optimization opportunities  
- Reusability of components and sub-flows
- Scalability and maintainability concerns

Code Quality Assessment:
- Configuration consistency
- Naming conventions and documentation
- Test coverage implications
- Deployment and environment considerations

Provide analysis that helps stakeholders understand the technical implications and architectural decisions."""
                        st.session_state.agents.analyzer.system_message = default_prompt
                        st.success("✅ Reset to default prompt!")
                        st.rerun()

                # Test the agent
                st.markdown("**Test Analyzer Agent:**")
                if st.button("🧪 Test Project Analysis"):
                    with st.spinner("Testing analyzer agent..."):
                        try:
                            flows = st.session_state.processed_files.get('flows', [])
                            dwl_scripts = st.session_state.processed_files.get('dwl_scripts', [])
                            analysis = st.session_state.agents.analyze_project_architecture(flows, dwl_scripts)
                            st.markdown("**Generated Analysis:**")
                            st.markdown(analysis)
                        except Exception as e:
                            st.error(f"Error testing analyzer: {str(e)}")

            with config_tab3:
                st.markdown("#### 🎭 Coordinator Agent Configuration")
                st.markdown("**Role:** Orchestrates the documentation process and manages agent interactions")

                # Display coordinator properties
                # Safely get coordinator configuration
                human_input_mode = getattr(st.session_state.agents.coordinator, 'human_input_mode', 'NEVER')
                max_auto_reply = getattr(st.session_state.agents.coordinator, 'max_consecutive_auto_reply', 3)
                if not isinstance(max_auto_reply, int):
                    max_auto_reply = 3

                coordinator_config = {
                    "Human Input Mode": human_input_mode,
                    "Max Consecutive Auto Reply": max_auto_reply,
                    "Code Execution": getattr(st.session_state.agents.coordinator, 'code_execution_config', False)
                }

                st.markdown("**Current Configuration:**")
                for key, value in coordinator_config.items():
                    st.write(f"• **{key}:** {value}")

                # Coordinator settings
                st.markdown("**Adjust Coordinator Settings:**")

                # Get current value safely, defaulting to 3 if not accessible
                current_max_replies = getattr(st.session_state.agents.coordinator, 'max_consecutive_auto_reply', 3)
                if not isinstance(current_max_replies, int):
                    current_max_replies = 3

                new_max_replies = st.number_input(
                    "Max Consecutive Auto Replies",
                    min_value=1,
                    max_value=10,
                    value=current_max_replies,
                    help="Maximum number of automatic replies before requiring intervention"
                )

                if st.button("💾 Update Coordinator Settings", type="primary"):
                    try:
                        # Update the coordinator settings if the attribute exists
                        if hasattr(st.session_state.agents.coordinator, 'max_consecutive_auto_reply'):
                            st.session_state.agents.coordinator.max_consecutive_auto_reply = new_max_replies
                        st.success("✅ Coordinator settings updated successfully!")
                    except Exception as e:
                        st.error(f"Error updating settings: {str(e)}")

            st.markdown("---")

            # Agent Interaction Visualization
            st.markdown("### 🔄 Agent Workflow Visualization")

            st.markdown("""
            <div class="info-card">
                <h4>🎯 Multi-Agent Workflow</h4>
                <p><strong>1. Summarizer Agent</strong> → Analyzes individual flows and DWL scripts</p>
                <p><strong>2. Analyzer Agent</strong> → Evaluates overall architecture and patterns</p>
                <p><strong>3. Coordinator Agent</strong> → Orchestrates the documentation generation process</p>
                <p><strong>4. Question Answering</strong> → All agents collaborate to answer specific queries</p>
            </div>
            """, unsafe_allow_html=True)

            # Real-time agent communication test
            st.markdown("### 🧪 Test Agent Collaboration")

            if st.button("🎭 Demonstrate Agent Workflow", type="primary"):
                if st.session_state.processed_files:
                    with st.spinner("Demonstrating multi-agent collaboration..."):
                        try:
                            # Show step-by-step agent workflow
                            st.markdown("#### 🔄 Agent Workflow in Action")

                            # Step 1: Summarizer
                            with st.expander("Step 1: Summarizer Agent Analysis", expanded=True):
                                if st.session_state.processed_files['flows']:
                                    flow_data = st.session_state.processed_files['flows'][0]
                                    st.write(f"**Analyzing Flow:** {flow_data['name']}")
                                    summary = st.session_state.agents.summarize_flow(flow_data)
                                    st.markdown("**Summarizer Output:**")
                                    st.markdown(summary[:500] + "..." if len(summary) > 500 else summary)

                            # Step 2: Analyzer
                            with st.expander("Step 2: Analyzer Agent Assessment", expanded=True):
                                flows = st.session_state.processed_files.get('flows', [])
                                dwl_scripts = st.session_state.processed_files.get('dwl_scripts', [])
                                analysis = st.session_state.agents.analyze_project_architecture(flows, dwl_scripts)
                                st.markdown("**Analyzer Output:**")
                                st.markdown(analysis[:500] + "..." if len(analysis) > 500 else analysis)

                            # Step 3: Coordinator
                            with st.expander("Step 3: Coordinator Orchestration", expanded=True):
                                st.markdown("**Coordinator Role:**")
                                st.write("• Manages the documentation generation workflow")
                                st.write("• Coordinates between Summarizer and Analyzer agents")
                                st.write("• Ensures comprehensive coverage of all components")
                                st.write("• Handles error scenarios and fallback strategies")
                                max_replies = getattr(st.session_state.agents.coordinator, 'max_consecutive_auto_reply', 3)
                                if not isinstance(max_replies, int):
                                    max_replies = 3
                                st.write(f"• Current max auto-replies: {max_replies}")

                            st.success("✅ Multi-agent workflow demonstration complete!")

                        except Exception as e:
                            st.error(f"Error demonstrating workflow: {str(e)}")
                else:
                    st.warning("Please process files first to demonstrate the workflow.")

            # Model and API configuration
            st.markdown("---")
            st.markdown("### 🔧 Global Agent Configuration")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Current Model Settings:**")
                st.write(f"• **Model:** {selected_model}")
                st.write(f"• **Temperature:** {temperature}")
                st.write(f"• **Max Tokens:** {max_tokens}")

            with col2:
                st.markdown("**API Configuration:**")
                api_status = "✅ Connected" if groq_api_key else "❌ Not configured"
                st.write(f"• **API Status:** {api_status}")
                st.write(f"• **Base URL:** https://api.groq.com/openai/v1")

                # Comprehensive API test
                if groq_api_key:
                    if st.button("🔍 Test API & Model", key="comprehensive_test", help="Test API connection and model availability"):
                        with st.spinner("Running comprehensive API test..."):
                            test_result = test_groq_api_key(groq_api_key, selected_model)
                            if test_result['success']:
                                st.success(f"✅ API test successful!")
                                st.info(f"Model response: {test_result.get('response', 'N/A')}")
                            else:
                                st.error(f"❌ API test failed: {test_result['error']}")
                                if "Invalid API key" in test_result['error']:
                                    st.info("💡 Please check your API key in the Configuration section")
                                elif "Model" in test_result['error'] and "not available" in test_result['error']:
                                    st.info("💡 Try selecting a different model from the dropdown")
                else:
                    st.info("💡 Configure your API key to test the connection")

            # Reinitialize agents with new settings
            if st.button("🔄 Reinitialize All Agents", type="secondary"):
                if groq_api_key:
                    try:
                        with st.spinner("Reinitializing agents with current settings..."):
                            new_agents = DocumentationAgents(
                                groq_api_key=groq_api_key,
                                model=selected_model,
                                temperature=temperature,
                                max_tokens=max_tokens
                            )
                            st.session_state.agents = new_agents
                            st.session_state.agents_initialized = True
                            st.success("✅ All agents reinitialized with current settings!")
                    except Exception as e:
                        st.error(f"Error reinitializing agents: {str(e)}")
                else:
                    st.error("Please configure your API key first.")

    # Professional footer
    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8fbff 0%, #e6f3ff 100%); 
                padding: 2rem; border-radius: 15px; text-align: center; margin-top: 3rem;
                border: 1px solid #e6f3ff;">
        <h4 style="color: #0066cc; margin-top: 0;">🚀 MuleSoft Documentation Generator</h4>
        <p style="color: #6c757d; margin: 0.5rem 0;">
            Enterprise-grade AI-powered documentation platform for MuleSoft integration projects
        </p>
        <div style="margin-top: 1rem;">
            <span style="background: #0066cc; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; 
                         font-size: 0.8rem; margin: 0 0.3rem;">Multi-Agent AI</span>
            <span style="background: #0066cc; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; 
                         font-size: 0.8rem; margin: 0 0.3rem;">Semantic Search</span>
            <span style="background: #0066cc; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; 
                         font-size: 0.8rem; margin: 0 0.3rem;">Professional Output</span>
        </div>
        <p style="color: #999; margin: 1rem 0 0 0; font-size: 0.8rem;">
            Powered by Groq LLM • Built with Streamlit • Deployed on Replit
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()