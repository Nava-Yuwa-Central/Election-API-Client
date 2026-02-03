# Nepal Entity Service - Optimized Local Server

🇳🇵 **Who's My Neta Nepal** - A clean, optimized local server for exploring Nepal's political representatives with real parliament data.

## ✨ Features

- **264+ Parliament Members** with official photos and complete data
- **Optimized Performance** with in-memory caching and efficient data handling
- **Beautiful Frontend** with responsive design and smooth animations
- **Real-time Search** with instant results and photo synchronization
- **Party Information** with color-coded badges and member counts
- **Clean Architecture** with minimal dependencies and fast loading

## 🚀 Quick Start

### Prerequisites
- **Python 3.7+** (no additional dependencies required)
- **Web Browser** (Chrome, Firefox, Safari, Edge)

### Running the Application

1. **Clone or download** this repository
2. **Navigate** to the project directory
3. **Run the server:**

```bash
# Windows
python run_local_simple.py

# Or use the batch file
run_local.bat
```

4. **Open your browser** and visit:
   - **Main App**: http://localhost:8197
   - **Leaders**: http://localhost:8197/leaders.html
   - **Parties**: http://localhost:8197/parties.html
   - **Map**: http://localhost:8197/map.html

## 📁 Project Structure

```
nepal-entity-service/
├── frontend/                    # Frontend application
│   ├── assets/                 # Images and static assets
│   ├── data/                   # Nepal map data (GeoJSON)
│   ├── js/                     # JavaScript modules
│   │   ├── api.js             # Optimized API client
│   │   ├── config.js          # Configuration
│   │   ├── main.js            # Main application logic
│   │   ├── translations.js    # Language support
│   │   └── utils.js           # Utility functions
│   ├── styles/                # CSS stylesheets
│   │   ├── main.css          # Main styles and variables
│   │   ├── components.css    # Component styles
│   │   └── animations.css    # Animation definitions
│   ├── index.html            # Landing page with featured leaders
│   ├── leaders.html          # Complete leaders directory
│   ├── parties.html          # Political parties overview
│   ├── map.html              # Interactive Nepal map
│   └── leader-detail.html    # Individual leader profiles
├── data/                       # Raw data files
├── database/                   # Data import scripts
├── scripts/                    # Utility scripts
├── run_local_simple.py        # Optimized local server
├── run_local.bat             # Windows batch file
├── run_local.ps1             # PowerShell script
├── parliament_data_enhanced.json  # Parliament member data
└── README.md                 # This file
```

## 🎯 Key Features

### Performance Optimizations
- **In-memory caching** with 5-minute TTL
- **Thread-safe data access** for concurrent requests
- **HTTP caching headers** for browser optimization
- **Request deduplication** to prevent duplicate API calls
- **Image preloading** for smooth user experience
- **Lazy loading** for better page performance

### Data Features
- **Complete parliament data** with 264+ members
- **Official photos** from parliament.gov.np
- **Bilingual support** (English and Nepali names)
- **Party affiliations** with color-coded badges
- **District and province** mapping
- **Age, education, and constituency** information

### User Interface
- **Responsive design** that works on all devices
- **Smooth animations** and transitions
- **Real-time search** with instant results
- **Card-based layout** for easy browsing
- **Interactive map** with province data
- **Clean, modern design** with Nepal-inspired colors

## 🔧 Configuration

The server runs on **port 8197** by default. You can modify this in `run_local_simple.py`:

```python
PORT = 8197  # Change this to your preferred port
```

## 📊 API Endpoints

- `GET /health` - Server health check
- `GET /api/v1/entities/` - List all entities (leaders/parties)
- `GET /api/v1/entities/{id}` - Get specific entity details
- `GET /api/v1/entities/?entity_type=person` - Get all leaders
- `GET /api/v1/entities/?entity_type=political_party` - Get all parties
- `GET /api/v1/entities/?search=query` - Search entities

## 🎨 Customization

### Adding New Leaders
1. Update `parliament_data_enhanced.json` with new member data
2. Restart the server to reload the cache
3. New members will appear automatically

### Styling
- **Main colors**: Edit CSS variables in `frontend/styles/main.css`
- **Components**: Modify `frontend/styles/components.css`
- **Animations**: Update `frontend/styles/animations.css`

### Adding Features
- **New pages**: Create HTML files in `frontend/`
- **API endpoints**: Add handlers in `run_local_simple.py`
- **JavaScript**: Add modules in `frontend/js/`

## 🚨 Troubleshooting

### Server Won't Start
- Check if port 8197 is available
- Ensure Python 3.7+ is installed
- Verify `parliament_data_enhanced.json` exists

### Images Not Loading
- Check internet connection (images load from parliament.gov.np)
- Verify image URLs in the data file
- Fallback placeholder images are provided

### Performance Issues
- Clear browser cache
- Restart the server to refresh data cache
- Check console for JavaScript errors

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Made with ❤️ for transparency in Nepali politics**

*Empowering citizens with accessible, transparent data about their political representatives.*