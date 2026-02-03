# Nepal Entity Service - Project Overview

## 🎯 What This Project Does

This is a **clean, optimized local web application** that displays Nepal's parliament members with their photos, party information, and biographical details. It's designed to be simple, fast, and easy to run.

## 🚀 How to Run (Super Simple)

1. **Double-click** `START_SERVER.bat` (Windows)
2. **Wait** for the server to start (about 5 seconds)
3. **Open browser** and go to: http://localhost:8197
4. **Enjoy** browsing Nepal's political representatives!

## 📱 What You'll See

### Landing Page (/)
- **Hero section** with search
- **Statistics** (264+ leaders, parties, provinces)
- **Featured leaders** in beautiful card layout
- **Real photos** from parliament.gov.np

### Leaders Page (/leaders.html)
- **Complete directory** of all parliament members
- **Advanced filtering** by party, province, education
- **Search functionality** with instant results
- **Sortable table** with photos and details

### Parties Page (/parties.html)
- **All political parties** with member counts
- **Party logos** and information
- **Click to filter** leaders by party

### Map Page (/map.html)
- **Interactive Nepal map** with province data
- **Leader distribution** by region
- **Clickable provinces** for detailed view

## 🔧 Technical Details

### Performance Features
- **5-minute caching** for fast data access
- **Thread-safe** concurrent request handling
- **Optimized images** with automatic fallbacks
- **Minimal dependencies** (just Python + browser)
- **Instant search** with debounced queries

### Data Source
- **Real parliament data** (264+ members)
- **Official photos** from parliament.gov.np
- **Complete metadata** (age, education, constituency)
- **Bilingual names** (English + Nepali)
- **Party affiliations** with color coding

### Browser Compatibility
- ✅ Chrome, Firefox, Safari, Edge
- ✅ Mobile responsive design
- ✅ Works offline (after initial load)
- ✅ Fast loading (< 2 seconds)

## 📁 Key Files

- `run_local_simple.py` - The optimized server (main file)
- `frontend/index.html` - Landing page with featured leaders
- `frontend/leaders.html` - Complete leaders directory
- `frontend/parties.html` - Political parties overview
- `parliament_data_enhanced.json` - All parliament member data
- `START_SERVER.bat` - Easy startup script

## 🎨 Customization

### Change Colors
Edit `frontend/styles/main.css` - look for CSS variables at the top

### Add New Pages
Create new HTML files in `frontend/` directory

### Modify Data
Update `parliament_data_enhanced.json` and restart server

### Change Port
Edit `PORT = 8197` in `run_local_simple.py`

## 🚨 If Something Goes Wrong

### Server Won't Start
- Make sure Python is installed
- Check if port 8197 is free
- Try running: `python run_local_simple.py`

### Images Not Loading
- Check internet connection
- Images load from parliament.gov.np
- Placeholder images will show if originals fail

### Page Looks Broken
- Clear browser cache (Ctrl+F5)
- Check browser console for errors
- Try a different browser

## 💡 Why This Approach?

Instead of complex frameworks, this project uses:
- **Pure HTML/CSS/JavaScript** for maximum compatibility
- **Single Python file** server for simplicity
- **No databases** - data loads from JSON file
- **No build process** - just run and go
- **Minimal dependencies** - works anywhere Python runs

This makes it **perfect for**:
- Quick demos and presentations
- Local development and testing
- Educational purposes
- Situations where you need something that "just works"

---

**🇳🇵 Enjoy exploring Nepal's political landscape!**