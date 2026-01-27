# AI-Powered Interactive Website Builder

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/your-repo/streamlit_demo.py) <!-- Update with actual URL if deployed -->

An AI-powered interactive website builder that guides users through a conversational interface to create custom websites. Built with Streamlit and powered by Google's Gemini AI (via OpenAI-compatible API), this tool generates complete, responsive HTML/CSS websites based on user requirements.

## Features

- **Conversational Setup**: Interactive chat interface that asks targeted questions to gather website requirements
- **AI-Powered Generation**: Uses advanced AI to create professional website specifications and code
- **Live Preview**: Real-time HTML preview of generated websites
- **Iterative Updates**: Chat-based interface to modify and update websites after generation
- **Responsive Design**: Generated websites are mobile-friendly and fully responsive
- **Export Functionality**: Download generated HTML files for deployment
- **Modern UI Components**: Includes headers, navigation, hero sections, about pages, services, contact forms, and footers

## Prerequisites

- Python 3.8 or higher
- Google Gemini API key (for AI generation)
- Internet connection for API calls

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/AI-Powered-Interactive-Website-Builder.git
   cd AI-Powered-Interactive-Website-Builder
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. **Set up environment variables:**
   
   Create a `.env` file in the root directory with your API credentials:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-pro  # or your preferred model
   GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/  # Gemini API endpoint
   ```

   > **Note:** The app uses the OpenAI Python client configured to work with Google's Gemini API. Make sure your API key has access to the Gemini API.

2. **Verify configuration:**
   
   The settings are loaded from `config/settings.py` which reads the `.env` file.

## Usage

1. **Run the Streamlit app:**
   ```bash
   streamlit run streamlit_demo.py
   ```

2. **Open your browser:**
   
   Navigate to the URL shown in the terminal (usually `http://localhost:8501`).

3. **Build your website:**
   - Answer the guided questions in the chat interface
   - The AI will generate a website summary and HTML code
   - Preview your website in the app
   - Make updates using the chat interface
   - Download the final HTML file

## Project Structure

```
AI-Powered Interactive Website Builder/
├── README.md
├── requirements.txt
├── streamlit_demo.py          # Main Streamlit application
├── config/
│   └── settings.py           # Configuration and API settings
├── prompt/
│   └── website_builder_prompt.txt  # AI system prompt for website generation
└── summary/                  # Generated during runtime
    ├── formatted_prompt.txt
    └── generated_summary.txt
```

## Key Components

- **`streamlit_demo.py`**: Main application with chat interface, AI integration, and website preview
- **`config/settings.py`**: Environment variable management and configuration
- **`prompt/website_builder_prompt.txt`**: Detailed prompt engineering for consistent AI-generated websites
- **`requirements.txt`**: Python dependencies (OpenAI, Streamlit)

## How It Works

1. **Question Gathering**: The app presents a series of questions to understand the user's website needs
2. **AI Processing**: User answers are formatted into a prompt and sent to Gemini AI
3. **Website Generation**: AI generates JSON specifications and complete HTML/CSS code
4. **Preview & Updates**: Users can preview the site and request modifications via chat
5. **Export**: Final website can be downloaded as HTML file

## Customization

- **Prompt Engineering**: Modify `prompt/website_builder_prompt.txt` to change AI behavior
- **UI Styling**: Update the Streamlit interface in `streamlit_demo.py`
- **API Configuration**: Change models or endpoints in `config/settings.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Google Gemini AI](https://ai.google.dev/)
- Uses [OpenAI Python Client](https://github.com/openai/openai-python) for API integration

## Support

If you encounter issues:
1. Check your API key and configuration
2. Ensure all dependencies are installed
3. Verify your Python version (3.8+)
4. Check the console for error messages

For questions or feature requests, please open an issue on GitHub.