import gradio as gr
import numpy as np
import random
import time
import matplotlib.pyplot as plt
import io
import base64
import requests
from PIL import Image
import tempfile
import os

# Custom CSS for the Earth to Sky theme
custom_css = """
#component-0 {
background: linear-gradient(135deg, #0a192f 0%, #145959 100%);
border-radius: 10px;
padding: 20px;
}
.gradio-container {
background: linear-gradient(135deg, #0a192f 0%, #145959 100%);
color: white;
}
.tabs {
background: rgba(10, 25, 47, 0.5);
border-radius: 10px;
box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
backdrop-filter: blur(5px);
border: 1px solid rgba(10, 25, 47, 0.3);
}
.tab-button {
background: transparent;
color: white;
border: none;
padding: 10px 20px;
border-radius: 5px;
margin: 5px;
transition: all 0.3s ease;
}
.tab-button:hover, .tab-button.selected {
background: rgba(255, 255, 255, 0.1);
transform: translateY(-2px);
}
.eco-card {
background: rgba(255, 255, 255, 0.05);
border-radius: 10px;
padding: 20px;
margin-bottom: 15px;
box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
backdrop-filter: blur(5px);
border: 1px solid rgba(255, 255, 255, 0.1);
}
.btn {
background: linear-gradient(90deg, #075a5a 0%, #0c8b8b 100%);
color: white;
border: none;
padding: 10px 20px;
border-radius: 5px;
cursor: pointer;
transition: all 0.3s ease;
}
.btn:hover {
transform: translateY(-2px);
box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}
.heading {
background: -webkit-linear-gradient(#ffffff, #7effe7);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
font-size: 2.5rem;
font-weight: bold;
text-align: center;
margin-bottom: 20px;
}
.subheading {
color: #9cffe0;
font-size: 1.2rem;
text-align: center;
margin-bottom: 30px;
}
/* Animations */
@keyframes float {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
    100% { transform: translateY(0px); }
}
.float-animation {
    animation: float 5s ease-in-out infinite;
}
/* Loader */
.loader {
    width: 60px;
    height: 60px;
    border: 5px solid rgba(67, 206, 162, 0.3);
    border-radius: 50%;
    border-top-color: #43cea2;
    display: inline-block;
    animation: spin 1s linear infinite;
}
@keyframes spin {
    to { transform: rotate(360deg); }
}
/* Badge styles */
.eco-badge {
    background: linear-gradient(135deg, rgba(67, 206, 162, 0.2) 0%, rgba(24, 90, 157, 0.2) 100%);
    border-radius: 20px;
    padding: 8px 15px;
    margin: 5px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(5px);
    border: 1px solid rgba(67, 206, 162, 0.2);
    transition: all 0.3s ease;
}
.eco-badge:hover {
    transform: scale(1.05);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}
/* Progress bar */
.progress-bar {
    height: 10px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 5px;
    overflow: hidden;
    margin: 10px 0;
}
.progress-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #43cea2 0%, #185a9d 100%);
    border-radius: 5px;
    transition: width 1s ease-in-out;
}
/* Card stats */
.stat-card {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 15px;
    text-align: center;
    transition: all 0.3s ease;
    backdrop-filter: blur(5px);
}
.stat-card:hover {
    transform: translateY(-5px);
    background: rgba(255, 255, 255, 0.15);
}
.stat-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: #e0fffa;
    margin: 5px 0;
}
.stat-label {
    color: rgba(255, 255, 255, 0.8);
    font-size: 0.9rem;
}
/* Impact visualization */
.impact-icon {
    font-size: 2.5rem;
    margin-bottom: 15px;
    display: inline-block;
}
/* Add to custom_css */
/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideIn {
    from { transform: translateX(-30px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

.fade-in {
    animation: fadeIn 0.5s ease-out forwards;
}

.slide-in {
    animation: slideIn 0.4s ease-out forwards;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .heading {
        font-size: 2.2rem;
    }
    .subheading {
        font-size: 1.1rem;
    }
    .stat-card {
        min-width: 100% !important;
        margin-bottom: 15px;
    }
    .tab-button {
        padding: 8px 15px;
        font-size: 0.9rem;
    }
}

/* Hover effects */
.hover-lift {
    transition: all 0.3s ease;
}
.hover-lift:hover {
    transform: translateY(-5px);
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #43cea2 0%, #185a9d 100%);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #43cea2 20%, #185a9d 80%);
}
"""

# Mock user data
user_data = {
    "scans_count": 45,
    "recycled_items": 32,
    "waste_types": {
        "Plastic": 18,
        "Paper": 12,
        "Glass": 7,
        "Metal": 5,
        "Organic": 3
    },
    "eco_score": 78,
    "co2_saved": 12.5,  # kg
    "badges": ["Eco Warrior", "Plastic Reducer", "Weekly Streaker"],
    "recent_activity": [
        {"date": "2025-04-12", "item": "Plastic bottle", "action": "Recycled"},
        {"date": "2025-04-10", "item": "Cardboard box", "action": "Recycled"},
        {"date": "2025-04-07", "item": "Glass jar", "action": "Upcycled"}
    ]
}

# Mock leaderboard data
leaderboard_data = [
    {"username": "EcoChampion", "score": 156},
    {"username": "GreenWarrior", "score": 142},
    {"username": "RecycleKing", "score": 137},
    {"username": "EarthProtector", "score": 129},
    {"username": "CurrentUser", "score": 78},
    {"username": "WasteReducer", "score": 65},
    {"username": "PlanetFriend", "score": 52},
]

# FAQ data
faq_content = [
    {
        "question": "How does EcoSnap identify waste items?",
        "answer": "EcoSnap uses advanced machine learning algorithms trained on thousands of waste images. Our AI model can identify various types of waste materials with high accuracy."
    },
    {
        "question": "Is my data private?",
        "answer": "Yes. We only use your images to provide classification results. We don't store your personal images unless you explicitly opt in to help improve our model."
    },
    {
        "question": "How accurate is the classification?",
        "answer": "Our model achieves over 90% accuracy for common waste items. However, unusual or mixed materials may sometimes be misclassified."
    },
    {
        "question": "Can I use EcoSnap offline?",
        "answer": "Currently, EcoSnap requires an internet connection to process images. We're working on a lite version that can work offline for basic classifications."
    },
    {
        "question": "How is my Eco Score calculated?",
        "answer": "Your Eco Score is based on the number of items you've scanned and properly recycled or composted, with bonus points for consistent usage and diversity of materials."
    }
]

# --- API Helper functions ---
def classify_image(image_path):
    """Call /classify/ endpoint with image file."""
    try:
        with open(image_path, "rb") as f:
            files = {"image": ("image.jpg", f, "image/jpeg")}
            resp = requests.post("http://localhost:8000/classify/", files=files)
        resp.raise_for_status()
        return resp.json().get("result", [])
    except requests.exceptions.ConnectionError:
        # Fallback to mock data if API is not available
        return ["plastic bottle"]
    except Exception as e:
        print(f"API Error: {e}")
        return ["unknown item"]

def generate_ideas(items):
    """Call /generate/ endpoint with recognized items."""
    try:
        payload = {"items": items}
        resp = requests.post("http://localhost:8000/generate/", json=payload)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        # Fallback to mock data if API is not available
        return {
            "recycling_tips": [
                "Remove caps and labels before recycling",
                "Rinse containers to remove food residue",
                "Check local recycling guidelines"
            ],
            "environmental_facts": [
                "Recycling one plastic bottle saves enough energy to power a light bulb for 3 hours",
                "It takes 450 years for plastic bottles to decompose naturally"
            ],
            "disposal_methods": [
                "Place in recycling bin after cleaning",
                "Take to local recycling center",
                "Participate in bottle return programs"
            ]
        }
    except Exception as e:
        print(f"API Error: {e}")
        return {"recycling_tips": [], "environmental_facts": [], "disposal_methods": []}

def get_diy(items, idea):
    """Call /diy/ endpoint with selected idea."""
    try:
        payload = {"items": items, "idea": idea}
        resp = requests.post("http://localhost:8000/diy/", json=payload)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        # Fallback to mock data if API is not available
        return {
            "title": "Plastic Bottle Planter",
            "materials": ["Plastic bottle", "Scissors", "Soil", "Seeds", "Paint (optional)"],
            "steps": [
                "Cut the bottle horizontally about 1/3 from the top",
                "Make drainage holes in the bottom part",
                "Decorate with paint if desired",
                "Fill with soil and plant seeds",
                "Water regularly and place in sunlight"
            ],
            "difficulty": "Easy",
            "safety_tip": "Be careful when cutting plastic - use proper scissors and cut away from your body"
        }
    except Exception as e:
        print(f"API Error: {e}")
        return {"title": "DIY Project", "materials": [], "steps": [], "difficulty": "Unknown", "safety_tip": ""}

# Helper functions for UI
def save_uploaded_image(image):
    """Save uploaded image to temporary file and return path"""
    if image is None:
        return None
    
    # Create temporary file
    temp_fd, temp_path = tempfile.mkstemp(suffix='.jpg')
    try:
        # If image is PIL Image, save it
        if hasattr(image, 'save'):
            image.save(temp_path)
        # If image is already a file path, copy it
        elif isinstance(image, str) and os.path.exists(image):
            import shutil
            shutil.copy2(image, temp_path)
        else:
            return None
        return temp_path
    except Exception as e:
        print(f"Error saving image: {e}")
        os.close(temp_fd)
        return None

def generate_impact_chart():
    """Generate a chart showing waste distribution"""
    labels = list(user_data["waste_types"].keys())
    sizes = list(user_data["waste_types"].values())
    
    # Create a figure with a modern, elegant background
    plt.figure(figsize=(10, 7), facecolor='#13293d')
    
    # Custom colors with better contrast
    colors = ['#43cea2', '#36b9cc', '#2a96da', '#185a9d', '#1a4971', '#13293d']
    
    # Create an exploded pie chart with modern styling
    explode = [0.05] * len(sizes)  # Slightly exploded segments
    wedges, texts, autotexts = plt.pie(
        sizes, 
        labels=None,  # We'll add custom legend instead
        autopct='%1.1f%%', 
        explode=explode,
        colors=colors,
        wedgeprops={'width': 0.6, 'edgecolor': '#13293d', 'linewidth': 2},  # Donut style with borders
        pctdistance=0.85,
        shadow=True,
        startangle=90
    )
    
    # Style percentage labels
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(11)
        autotext.set_fontweight('bold')
    
    # Add a circle at the center to make it a donut chart
    centre_circle = plt.Circle((0, 0), 0.4, fc='#13293d')
    plt.gca().add_artist(centre_circle)
    
    # Add a title in the center of the donut
    plt.text(0, 0, 'Waste\nDistribution', ha='center', va='center', fontsize=16, color='white', fontweight='bold')
    
    # Create custom legend with percentage and count
    total = sum(sizes)
    legend_labels = [f'{label}: {count} ({count/total*100:.1f}%)' for label, count in zip(labels, sizes)]
    plt.legend(wedges, legend_labels, title="Waste Types", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1),
              fontsize=10, title_fontsize=12, frameon=False, labelcolor='white')
    
    plt.title('Your Environmental Impact', color='white', fontsize=18, pad=20)
    plt.axis('equal')  # Equal aspect ratio ensures the pie chart is circular
    
    # Save the figure to a bytes buffer with higher DPI for better quality
    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor='#13293d', dpi=120, bbox_inches='tight')
    plt.close()
    
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    return f'<img src="data:image/png;base64,{img_str}" alt="Impact Chart" style="max-width:100%; border-radius:15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">'

def generate_progress_chart():
    """Generate a progress chart"""
    # Mock data for the last 6 weeks
    weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6']
    recycled = [5, 7, 6, 10, 8, 12]
    scanned = [8, 10, 7, 12, 10, 14]
    
    x = np.arange(len(weeks))
    width = 0.35
    
    plt.figure(figsize=(10, 5), facecolor='#0a192f')
    ax = plt.gca()
    ax.set_facecolor('#0a192f')
    
    rects1 = plt.bar(x - width/2, recycled, width, label='Recycled', color='#66c2a4')
    rects2 = plt.bar(x + width/2, scanned, width, label='Scanned', color='#41ae76')
    
    plt.ylabel('Count', color='white')
    plt.title('Your Recycling Progress', color='white', fontsize=14)
    plt.xticks(x, weeks, color='white')
    plt.yticks(color='white')
    plt.legend(facecolor='#0a192f', edgecolor='#0a192f', labelcolor='white')
    
    ax.spines['bottom'].set_color('white')
    ax.spines['top'].set_color('white')
    ax.spines['right'].set_color('white')
    ax.spines['left'].set_color('white')
    
    # Save the figure to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor='#0a192f')
    plt.close()
    
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    return f'<img src="data:image/png;base64,{img_str}" alt="Progress Chart">'

# Define the UI components for each page
def home_page():
    logo_html = """
    <div style="display: flex; justify-content: center; margin-bottom: 30px;" class="float-animation">
        <svg width="140" height="140" viewBox="0 0 140 140">
            <circle cx="70" cy="70" r="65" fill="url(#eco-grad)" />
            <path d="M40,40 L100,40 L100,100 L40,100 Z" fill="rgba(255,255,255,0.15)" />
            <path d="M50,50 L90,50 L90,90 L50,90 Z" fill="rgba(255,255,255,0.3)" />
            <path d="M55,70 L85,70 M70,55 L70,85" stroke="#ffffff" stroke-width="5" stroke-linecap="round" />
            <defs>
                <linearGradient id="eco-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#43cea2;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#185a9d;stop-opacity:1" />
                </linearGradient>
            </defs>
        </svg>
    </div>
    """
    
    welcome_html = """
    <div class="eco-card">
        <h1 class="heading">Welcome to EcoSnap</h1>
        <p class="subheading">Your AI-Powered Waste Classification Assistant</p>
        
        <div style="text-align: center; margin-bottom: 40px;">
            <p style="font-size: 1.1rem; line-height: 1.6; max-width: 800px; margin: 0 auto;">
                EcoSnap helps you properly recycle and dispose of waste by identifying materials with just a photo.
                Our advanced AI technology instantly recognizes different waste types and provides custom recycling instructions.
            </p>
        </div>
        
        <div style="display: flex; justify-content: space-around; margin: 40px 0; flex-wrap: wrap; gap: 15px;">
            <div class="stat-card" style="flex: 1; min-width: 200px;">
                <div class="impact-icon">📷</div>
                <h3 style="margin: 10px 0;">Snap a Photo</h3>
                <p>Capture any waste item with your camera</p>
            </div>
            <div class="stat-card" style="flex: 1; min-width: 200px;">
                <div class="impact-icon">🔍</div>
                <h3 style="margin: 10px 0;">AI Classification</h3>
                <p>Our AI instantly identifies the material</p>
            </div>
            <div class="stat-card" style="flex: 1; min-width: 200px;">
                <div class="impact-icon">♻️</div>
                <h3 style="margin: 10px 0;">Get Instructions</h3>
                <p>Learn how to properly dispose or recycle</p>
            </div>
            <div class="stat-card" style="flex: 1; min-width: 200px;">
                <div class="impact-icon">🌱</div>
                <h3 style="margin: 10px 0;">Track Impact</h3>
                <p>See your environmental contribution grow</p>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 20px;">
            <div class="progress-bar" style="max-width: 400px; margin: 30px auto 20px;">
                <div class="progress-bar-fill" style="width: 75%;"></div>
            </div>
            <p style="margin-bottom: 30px; color: rgba(255, 255, 255, 0.8);">
                Join 5,240+ users helping our planet. <strong>75%</strong> to our goal of 7,000!
            </p>
        </div>
    </div>
    """
    
    return [
        gr.HTML(logo_html),
        gr.HTML(welcome_html),
        gr.Button("Get Started", elem_classes=["btn"]),
    ]

def scan_page():
    return [
        gr.HTML("<h1 class='heading'>Scan Waste Item</h1>"),
        gr.HTML("<p class='subheading'>Upload an image or take a photo of the waste item you want to classify</p>"),
        gr.Image(type="pil", label="Upload or Capture Image", elem_classes=["eco-card"]),
        gr.Button("Scan Item", elem_classes=["btn"]),
        gr.HTML("<div id='loading-indicator' style='text-align: center; display: none;'><p>Analyzing image... Please wait</p><div class='loader'></div></div>"),
    ]

def results_page():
    return [
        gr.HTML("<h1 class='heading'>Classification Results</h1>"),
        gr.HTML("<div class='eco-card' id='result-container' style='display: none;'></div>"),
        gr.Radio(choices=[], label="Select a DIY Upcycling Idea", visible=False, elem_classes=["eco-card"]),
        gr.Button("Get DIY Tutorial", elem_classes=["btn"], visible=False),
        gr.HTML("<div class='eco-card' id='diy-container' style='display: none;'></div>"),
        gr.Button("Scan Another Item", elem_classes=["btn"]),
        gr.Button("View My Impact Dashboard", elem_classes=["btn"]),
    ]

def dashboard_page():
    stats_html = f"""
    <div class="eco-card">
        <h2 style="color: #5b9e69;">Your Sustainability Stats</h2>
        <div style="display: flex; justify-content: space-around; flex-wrap: wrap; margin: 20px 0;">
            <div style="text-align: center; margin: 10px; width: 150px;">
                <div style="font-size: 40px; color: #7be495; margin-bottom: 5px;">{user_data['scans_count']}</div>
                <p>Items Scanned</p>
            </div>
            <div style="text-align: center; margin: 10px; width: 150px;">
                <div style="font-size: 40px; color: #7be495; margin-bottom: 5px;">{user_data['recycled_items']}</div>
                <p>Items Recycled</p>
            </div>
            <div style="text-align: center; margin: 10px; width: 150px;">
                <div style="font-size: 40px; color: #7be495; margin-bottom: 5px;">{user_data['eco_score']}</div>
                <p>Eco Score</p>
            </div>
            <div style="text-align: center; margin: 10px; width: 150px;">
                <div style="font-size: 40px; color: #7be495; margin-bottom: 5px;">{user_data['co2_saved']}kg</div>
                <p>CO₂ Saved</p>
            </div>
        </div>
        
        <div style="margin: 20px 0;">
            <h3 style="color: #5b9e69;">Your Badges</h3>
            <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; margin: 15px 0;">
                {''.join(f'<div style="background: rgba(161, 255, 206, 0.3); padding: 10px; border-radius: 20px; backdrop-filter: blur(5px);">{badge}</div>' for badge in user_data["badges"])}
            </div>
        </div>
    </div>
    """
    
    leaderboard_html = """
    <div class="eco-card">
        <h2 style="color: #9cffe0;">Community Leaderboard</h2>
        <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.2);">
                <th style="padding: 10px; text-align: left;">Rank</th>
                <th style="padding: 10px; text-align: left;">User</th>
                <th style="padding: 10px; text-align: right;">Eco Score</th>
            </tr>
    """
    
    for i, user in enumerate(leaderboard_data):
        highlight = "background: rgba(102, 194, 164, 0.2); font-weight: bold;" if user["username"] == "CurrentUser" else ""
        leaderboard_html += f"""
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1); {highlight}">
                <td style="padding: 10px;">{i+1}</td>
                <td style="padding: 10px;">{user["username"]}</td>
                <td style="padding: 10px; text-align: right;">{user["score"]}</td>
            </tr>
        """
    
    leaderboard_html += """
        </table>
    </div>
    """
    
    # Recent activity
    activity_html = """
    <div class="eco-card">
        <h2 style="color: #9cffe0;">Recent Activity</h2>
        <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.2);">
                <th style="padding: 10px; text-align: left;">Date</th>
                <th style="padding: 10px; text-align: left;">Item</th>
                <th style="padding: 10px; text-align: right;">Action</th>
            </tr>
    """
    
    for activity in user_data["recent_activity"]:
        activity_html += f"""
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                <td style="padding: 10px;">{activity["date"]}</td>
                <td style="padding: 10px;">{activity["item"]}</td>
                <td style="padding: 10px; text-align: right;">{activity["action"]}</td>
            </tr>
        """
    
    activity_html += """
        </table>
    </div>
    """
    
    return [
        gr.HTML("<h1 class='heading'>Your Eco Impact Dashboard</h1>"),
        gr.HTML(stats_html),
        gr.HTML(f"<div class='eco-card'><div id='impact-chart'>{generate_impact_chart()}</div></div>"),
        gr.HTML(f"<div class='eco-card'><div id='progress-chart'>{generate_progress_chart()}</div></div>"),
        gr.HTML(leaderboard_html),
        gr.HTML(activity_html),
        gr.Button("Scan New Item", elem_classes=["btn"])
    ]

def diy_page():
    # Mock DIY project ideas
    diy_ideas = [
        {
            "title": "Plastic Bottle Planters",
            "materials": "Plastic bottles, scissors, soil, seeds",
            "difficulty": "Easy",
            "description": "Cut plastic bottles in half and use as small planters for herbs or flowers."
        },
        {
            "title": "Glass Jar Lanterns",
            "materials": "Glass jars, wire, tea lights, paint (optional)",
            "difficulty": "Medium",
            "description": "Transform glass jars into beautiful lanterns using wire handles and decorative paint."
        },
        {
            "title": "Cardboard Box Organizer",
            "materials": "Cardboard boxes, scissors, paint",
            "difficulty": "Easy",
            "description": "Use old cardboard boxes to create stylish organizers for your desk or shelves."
        },
        {
            "title": "Tin Can Herb Garden",
            "materials": "Empty tin cans, soil, herbs, paint (optional)",
            "difficulty": "Medium",
            "description": "Repurpose tin cans as small herb pots. Decorate them with paint for a personal touch."
        },
        {
            "title": "Old T-Shirt Tote Bag",
            "materials": "Old t-shirts, scissors",
            "difficulty": "Easy",
            "description": "Turn an old t-shirt into a reusable tote bag with just a few cuts and knots."
        }
    ]

# def diy_page():
#     diy_html = """
#     <h1 class='heading'>DIY Upcycling Ideas</h1>
#     <p class='subheading'>Give your waste items a second life with these creative projects</p>
#     <div style="display: flex; flex-wrap: wrap; justify-content: space-around; gap: 20px;">
#     """
    
#     for idea in diy_ideas:
#         difficulty_color = "#4CAF50" if idea["difficulty"] == "Easy" else "#FFC107" if idea["difficulty"] == "Medium" else "#F44336"
        
#         diy_html += f"""
#         <div class="eco-card" style="width: 300px;">
#             <h3 style="color: #9cffe0; margin-bottom: 10px;">{idea["title"]}</h3>
#             <p><strong>Materials:</strong> {idea["materials"]}</p>
#             <p><strong>Difficulty:</strong> <span style="color: {difficulty_color};">{idea["difficulty"]}</span></p>
#             <p>{idea["description"]}</p>
#         </div>
#         """
    
#     diy_html += """
#     </div>
#     """
    
#     return [
#         gr.HTML(diy_html),
#         gr.Button("Back to Dashboard", elem_classes=["btn"]),
#     ]

def faq_page():
    faq_html = """
    <h1 class='heading'>Frequently Asked Questions</h1>
    <div class="eco-card">
    """
    
    for item in faq_content:
        faq_html += f"""
        <details style="margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px;">
            <summary style="cursor: pointer; font-weight: bold; color: #9cffe0; padding: 10px 0;">{item["question"]}</summary>
            <p style="padding: 10px 20px;">{item["answer"]}</p>
        </details>
        """
    
    faq_html += """
    </div>
    
    <div class="eco-card" style="margin-top: 30px;">
        <h2 style="color: #9cffe0;">About EcoSnap</h2>
        <p>EcoSnap is an AI-powered waste classification assistant designed to help users properly recycle and dispose of waste items.</p>
        <p>Our mission is to reduce environmental impact by increasing recycling rates and reducing contamination in recycling streams.</p>
        <p>The application uses advanced machine learning algorithms trained on thousands of waste images to provide accurate classification and personalized recycling instructions.</p>
        <p>Join our community of eco-conscious users and start making a positive impact on the environment today!</p>
    </div>
    """
    
    return [
        gr.HTML(faq_html),
        gr.Button("Back to Home", elem_classes=["btn"]),
    ]
# Define the functions for handling page navigation and actions
def scan_item(image):
    """Process uploaded image and return classification results"""
    if image is None:
        return f"<p style='color: #f44336;'>Please upload an image first</p>"
    
    try:
        # Save uploaded image to temporary file
        temp_path = save_uploaded_image(image)
        if temp_path is None:
            return f"<p style='color: #f44336;'>Error processing image</p>"
        
        # Call API to classify image
        classified_items = classify_image(temp_path)
        
        # Clean up temporary file
        try:
            os.unlink(temp_path)
        except:
            pass
        
        if not classified_items:
            return f"<p style='color: #f44336;'>Could not classify the image</p>"
        
        # Get the primary classification
        primary_item = classified_items[0] if isinstance(classified_items, list) else classified_items
        
        # Generate recycling ideas and tips
        ideas_data = generate_ideas([primary_item])
        
        # Create result HTML
        result_html = create_results_html(primary_item, ideas_data, classified_items)
        
        # Update user stats (mock update)
        user_data["scans_count"] += 1
        if "recycled" in primary_item.lower() or "recyclable" in primary_item.lower():
            user_data["recycled_items"] += 1
        
        return result_html
        
    except Exception as e:
        print(f"Error in scan_item: {e}")
        return f"<p style='color: #f44336;'>Error processing image: {str(e)}</p>"

def create_results_html(primary_item, ideas_data, all_items):
    """Create HTML for displaying classification results"""
    
    # Mock confidence (in real app, this would come from your AI model)
    confidence = random.uniform(0.75, 0.95)
    conf_color = "#4CAF50" if confidence > 0.85 else "#FFC107" if confidence > 0.7 else "#F44336"
    
    # Get recycling tips
    recycling_tips = ideas_data.get("recycling_tips", ["Clean the item before recycling", "Check local recycling guidelines"])
    environmental_facts = ideas_data.get("environmental_facts", ["Recycling helps reduce waste in landfills"])
    disposal_methods = ideas_data.get("disposal_methods", ["Place in appropriate recycling bin"])
    
    # Format the tips for display
    tips_html = ""
    for i, tip in enumerate(recycling_tips[:3], 1):  # Show max 3 tips
        tips_html += f"""
        <div style="display: flex; align-items: start; margin-bottom: 15px;">
            <span style="background: rgba(67, 206, 162, 0.2); width: 30px; height: 30px; border-radius: 50%; display: inline-flex; justify-content: center; align-items: center; margin-right: 15px; flex-shrink: 0; font-weight: bold;">{i}</span>
            <p style="margin: 0; line-height: 1.5;">{tip}</p>
        </div>
        """
    
    # Environmental facts
    facts_html = ""
    for fact in environmental_facts[:2]:  # Show max 2 facts
        facts_html += f"<li style='margin-bottom: 10px; line-height: 1.5;'>{fact}</li>"
    
    # Disposal methods
    disposal_html = ""
    for method in disposal_methods[:3]:  # Show max 3 methods
        disposal_html += f"<li style='margin-bottom: 8px; line-height: 1.4;'>{method}</li>"
    
    # Create main result HTML
    result_html = f"""
    <div class="eco-card" style="animation: fadeIn 0.5s ease-out;">
        <div style="display: flex; flex-wrap: wrap; align-items: start; gap: 25px;">
            <div style="flex: 1; min-width: 300px;">
                <div style="display: flex; align-items: center; margin-bottom: 20px; flex-wrap: wrap;">
                    <h2 style="color: #e0fffa; margin: 0 15px 0 0; font-size: 1.8rem;">Item: {primary_item.title()}</h2>
                    <div style="background: rgba(67, 206, 162, 0.2); display: inline-flex; padding: 8px 15px; border-radius: 20px; align-items: center;">
                        <div class="progress-bar" style="width: 100px; height: 8px; margin: 0 10px 0 0;">
                            <div class="progress-bar-fill" style="width: {confidence*100}%; background: {conf_color};"></div>
                        </div>
                        <span style="color: {conf_color}; font-weight: bold;">{confidence:.1%}</span>
                    </div>
                </div>
                
                <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 20px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #43cea2; margin-bottom: 20px;">♻️ How to Recycle</h3>
                    {tips_html}
                    
                    <h3 style="color: #43cea2; margin: 25px 0 15px 0;">🌍 Environmental Impact</h3>
                    <ul style="padding-left: 0; list-style: none;">
                        {facts_html}
                    </ul>
                    
                    <h3 style="color: #43cea2; margin: 25px 0 15px 0;">🗂️ Disposal Methods</h3>
                    <ul style="padding-left: 20px;">
                        {disposal_html}
                    </ul>
                    
                    <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 25px;">
                        <div class="eco-badge">✅ Identified</div>
                        <div class="eco-badge">♻️ Recyclable</div>
                        <div class="eco-badge">🌱 Eco-friendly</div>
                    </div>
                </div>
                
                <div style="display: flex; flex-wrap: wrap; gap: 15px; margin-top: 20px;">
                    <button onclick="alert('Feature coming soon!')" class="btn" style="display: flex; align-items: center;">
                        <span style="margin-right: 8px;">🔄</span> Get DIY Ideas
                    </button>
                    
                    <button onclick="alert('Added to your tracker! Your eco-score has increased.')" class="btn" style="background: linear-gradient(90deg, #1a4971 0%, #36b9cc 100%);">
                        <span style="margin-right: 8px;">➕</span> Add to Tracker
                    </button>
                </div>
                
                <div style="background: rgba(24, 90, 157, 0.2); border-radius: 12px; padding: 15px; margin-top: 20px;">
                    <div style="display: flex; align-items: center;">
                        <div style="width: 50px; height: 50px; border-radius: 50%; background: rgba(67, 206, 162, 0.2); display: flex; justify-content: center; align-items: center; margin-right: 15px; font-size: 1.5rem;">
                            🌍
                        </div>
                        <div>
                            <h4 style="margin: 0 0 5px 0; color: #e0fffa;">Environmental Impact</h4>
                            <p style="margin: 0; font-size: 0.9rem;">Recycling this item saves approximately {round(random.uniform(0.1, 2.0), 2)} kg CO₂ equivalent</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div style="flex: 1; min-width: 280px;">
                <div style="background: rgba(67, 206, 162, 0.1); border-radius: 12px; padding: 20px; text-align: center;">
                    <div style="font-size: 4rem; margin-bottom: 15px;">
                        {"🍶" if "bottle" in primary_item.lower() else "📦" if "box" in primary_item.lower() or "cardboard" in primary_item.lower() else "🥫" if "can" in primary_item.lower() or "metal" in primary_item.lower() else "♻️"}
                    </div>
                    <h3 style="color: #e0fffa; margin-bottom: 10px;">Classification Result</h3>
                    <p style="font-size: 1.2rem; color: #9cffe0;">{primary_item.title()}</p>
                </div>
                
                <div style="background: rgba(67, 206, 162, 0.05); border-radius: 12px; padding: 15px; margin-top: 20px;">
                    <h4 style="margin: 0 0 15px 0; color: #e0fffa;">All Detected Items:</h4>
                    <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                        {' '.join([f'<div class="eco-badge" style="cursor: pointer; font-size: 0.9rem;">{item}</div>' for item in (all_items if isinstance(all_items, list) else [all_items])])}
                    </div>
                </div>
                
                <div style="background: rgba(24, 90, 157, 0.1); border-radius: 12px; padding: 15px; margin-top: 20px;">
                    <h4 style="margin: 0 0 10px 0; color: #e0fffa;">Quick Stats</h4>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span>Accuracy:</span>
                        <span style="color: {conf_color}; font-weight: bold;">{confidence:.1%}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span>Category:</span>
                        <span style="color: #43cea2;">Recyclable</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>CO₂ Impact:</span>
                        <span style="color: #4CAF50;">-{round(random.uniform(0.1, 2.0), 1)}kg</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <style>
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    </style>
    """
    
    return result_html

def process_diy_selection(items, selected_idea):
    """Process DIY idea selection and return tutorial"""
    if not selected_idea or not items:
        return f"<p>Please select a DIY idea first</p>"
    
    try:
        # Call API to get DIY tutorial
        diy_data = get_diy(items, selected_idea)
        
        # Create DIY tutorial HTML
        diy_html = create_diy_html(diy_data)
        
        return diy_html
        
    except Exception as e:
        print(f"Error in process_diy_selection: {e}")
        return f"<p style='color: #f44336;'>Error getting DIY tutorial: {str(e)}</p>"

def create_diy_html(diy_data):
    """Create HTML for DIY tutorial display"""
    
    title = diy_data.get("title", "DIY Project")
    materials = diy_data.get("materials", [])
    steps = diy_data.get("steps", [])
    difficulty = diy_data.get("difficulty", "Unknown")
    safety_tip = diy_data.get("safety_tip", "")
    
    # Difficulty color
    difficulty_colors = {
        "Easy": "#4CAF50",
        "Medium": "#FFC107", 
        "Hard": "#F44336"
    }
    difficulty_color = difficulty_colors.get(difficulty, "#9E9E9E")
    
    # Materials HTML
    materials_html = ""
    for material in materials:
        materials_html += f"<li style='margin-bottom: 8px; padding: 5px 0;'>{material}</li>"
    
    # Steps HTML
    steps_html = ""
    for i, step in enumerate(steps, 1):
        steps_html += f"""
        <div style="display: flex; align-items: start; margin-bottom: 20px; padding: 15px; background: rgba(255, 255, 255, 0.03); border-radius: 8px;">
            <div style="background: #43cea2; color: white; width: 30px; height: 30px; border-radius: 50%; display: flex; justify-content: center; align-items: center; margin-right: 15px; flex-shrink: 0; font-weight: bold;">
                {i}
            </div>
            <p style="margin: 0; line-height: 1.5;">{step}</p>
        </div>
        """
    
    diy_html = f"""
    <div class="eco-card" style="animation: slideIn 0.4s ease-out;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="color: #e0fffa; margin-bottom: 10px; font-size: 2rem;">{title}</h2>
            <div style="display: inline-flex; align-items: center; background: rgba(67, 206, 162, 0.1); padding: 8px 15px; border-radius: 20px;">
                <span style="margin-right: 8px;">⭐</span>
                <span style="color: {difficulty_color}; font-weight: bold;">{difficulty}</span>
            </div>
        </div>
        
        <div style="display: flex; flex-wrap: wrap; gap: 30px;">
            <div style="flex: 1; min-width: 300px;">
                <h3 style="color: #43cea2; margin-bottom: 15px; display: flex; align-items: center;">
                    <span style="margin-right: 10px;">🛠️</span> Materials Needed
                </h3>
                <ul style="padding-left: 20px; background: rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 15px 15px 15px 35px;">
                    {materials_html}
                </ul>
                
                {f'''
                <div style="background: rgba(244, 67, 54, 0.1); border-left: 4px solid #f44336; padding: 15px; margin-top: 25px; border-radius: 4px;">
                    <h4 style="color: #f44336; margin: 0 0 8px 0; display: flex; align-items: center;">
                        <span style="margin-right: 8px;">⚠️</span> Safety Tip
                    </h4>
                    <p style="margin: 0; line-height: 1.4;">{safety_tip}</p>
                </div>
                ''' if safety_tip else ''}
            </div>
            
            <div style="flex: 2; min-width: 400px;">
                <h3 style="color: #43cea2; margin-bottom: 20px; display: flex; align-items: center;">
                    <span style="margin-right: 10px;">📋</span> Step-by-Step Instructions
                </h3>
                <div>
                    {steps_html}
                </div>
                
                <div style="background: rgba(67, 206, 162, 0.1); border-radius: 12px; padding: 20px; margin-top: 30px; text-align: center;">
                    <h4 style="color: #e0fffa; margin: 0 0 10px 0;">🎉 Great Job!</h4>
                    <p style="margin: 0; color: rgba(255, 255, 255, 0.8);">
                        You've successfully upcycled waste into something useful! 
                        Share your creation with the EcoSnap community.
                    </p>
                    <div style="margin-top: 15px;">
                        <button onclick="alert('Photo sharing feature coming soon!')" class="btn" style="margin-right: 10px;">
                            📸 Share Photo
                        </button>
                        <button onclick="alert('Added 10 points to your eco-score!')" class="btn">
                            ⭐ Mark Complete
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <style>
    @keyframes slideIn {{
        from {{ transform: translateX(-30px); opacity: 0; }}
        to {{ transform: translateX(0); opacity: 1; }}
    }}
    </style>
    """
    
    return diy_html

# Updated diy_page function with proper integration
def diy_page():
    # Mock DIY project ideas
    diy_ideas = [
        {
            "title": "Plastic Bottle Planters",
            "materials": "Plastic bottles, scissors, soil, seeds",
            "difficulty": "Easy",
            "description": "Cut plastic bottles in half and use as small planters for herbs or flowers.",
            "time": "15 mins"
        },
        {
            "title": "Glass Jar Lanterns", 
            "materials": "Glass jars, wire, tea lights, paint (optional)",
            "difficulty": "Medium",
            "description": "Transform glass jars into beautiful lanterns using wire handles and decorative paint.",
            "time": "30 mins"
        },
        {
            "title": "Cardboard Box Organizer",
            "materials": "Cardboard boxes, scissors, paint",
            "difficulty": "Easy", 
            "description": "Use old cardboard boxes to create stylish organizers for your desk or shelves.",
            "time": "20 mins"
        },
        {
            "title": "Tin Can Herb Garden",
            "materials": "Empty tin cans, soil, herbs, paint (optional)",
            "difficulty": "Medium",
            "description": "Repurpose tin cans as small herb pots. Decorate them with paint for a personal touch.",
            "time": "25 mins"
        },
        {
            "title": "Old T-Shirt Tote Bag",
            "materials": "Old t-shirts, scissors",
            "difficulty": "Easy",
            "description": "Turn an old t-shirt into a reusable tote bag with just a few cuts and knots.",
            "time": "10 mins"
        }
    ]

    diy_html = """
    <h1 class='heading'>DIY Upcycling Ideas</h1>
    <p class='subheading'>Give your waste items a second life with these creative projects</p>
    
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px; margin-top: 30px;">
    """
    
    for idea in diy_ideas:
        difficulty_colors = {
            "Easy": "#4CAF50",
            "Medium": "#FFC107", 
            "Hard": "#F44336"
        }
        difficulty_color = difficulty_colors.get(idea["difficulty"], "#9E9E9E")
        
        # Icon based on project type
        icon = "🌱" if "plant" in idea["title"].lower() else "💡" if "lantern" in idea["title"].lower() else "📦" if "box" in idea["title"].lower() else "🥫" if "can" in idea["title"].lower() else "👕"
        
        diy_html += f"""
        <div class="eco-card hover-lift" style="height: 100%; display: flex; flex-direction: column;">
            <div style="text-align: center; margin-bottom: 15px;">
                <div style="font-size: 3rem; margin-bottom: 10px;">{icon}</div>
                <h3 style="color: #9cffe0; margin-bottom: 10px;">{idea["title"]}</h3>
            </div>
            
            <div style="flex-grow: 1;">
                <p style="line-height: 1.5; margin-bottom: 15px;">{idea["description"]}</p>
                
                <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 15px;">
                    <div class="eco-badge">
                        <span style="color: {difficulty_color};">⭐ {idea["difficulty"]}</span>
                    </div>
                    <div class="eco-badge">
                        ⏱️ {idea["time"]}
                    </div>
                </div>
                
                <div style="background: rgba(255, 255, 255, 0.05); padding: 10px; border-radius: 8px; margin-bottom: 15px;">
                    <p style="margin: 0; font-size: 0.9rem;"><strong>Materials:</strong> {idea["materials"]}</p>
                </div>
            </div>
            
            <div style="margin-top: auto; text-align: center;">
                <button onclick="alert('Tutorial feature coming soon for {idea["title"]}!')" class="btn" style="width: 100%;">
                    📋 View Tutorial
                </button>
            </div>
        </div>
        """
    
    diy_html += """
    </div>
    
    <div class="eco-card" style="margin-top: 40px; text-align: center;">
        <h3 style="color: #9cffe0; margin-bottom: 15px;">💡 Have Your Own Idea?</h3>
        <p style="margin-bottom: 20px;">Share your creative upcycling projects with the EcoSnap community!</p>
        <button onclick="alert('Community sharing feature coming soon!')" class="btn">
            📤 Submit Your Project
        </button>
    </div>
    """
    
    return [
        gr.HTML(diy_html),
        gr.Button("Back to Dashboard", elem_classes=["btn"]),
    ]

# Main Application
with gr.Blocks(css=custom_css) as app:
    # Current state
    current_page = gr.State("home")
    uploaded_image = gr.State(None)
    classified_items = gr.State([])
    
    # Container for all pages
    with gr.Group():
        # Home Page
        with gr.Group(visible=True) as home_container:
            home_components = home_page()
            home_get_started_btn = home_components[2]
        
        # Scan Page
        with gr.Group(visible=False) as scan_container:
            scan_components = scan_page()
            scan_image_input = scan_components[2]
            scan_btn = scan_components[3]
            scan_loading = scan_components[4]
        
        # Results Page
        with gr.Group(visible=False) as results_container:
            results_components = results_page()
            results_display = results_components[1]
            diy_ideas_radio = results_components[2]
            get_diy_btn = results_components[3]
            diy_display = results_components[4]
            scan_another_btn = results_components[5]
            view_dashboard_btn = results_components[6]
        
        # Dashboard Page
        with gr.Group(visible=False) as dashboard_container:
            dashboard_components = dashboard_page()
            dashboard_scan_btn = dashboard_components[-1]
        
        # DIY Page
        with gr.Group(visible=False) as diy_container:
            diy_components = diy_page()
            diy_back_btn = diy_components[-1]
        
        # FAQ Page
        with gr.Group(visible=False) as faq_container:
            faq_components = faq_page()
            faq_back_btn = faq_components[-1]
    
    # Navigation tabs
    with gr.Row(elem_classes=["tabs"]):
        home_tab = gr.Button("Home", elem_classes=["tab-button"], visible=True)
        scan_tab = gr.Button("Scan", elem_classes=["tab-button"], visible=True)
        dashboard_tab = gr.Button("Dashboard", elem_classes=["tab-button"], visible=True)
        diy_tab = gr.Button("DIY Upcycling", elem_classes=["tab-button"], visible=True, elem_id="diy-tab-button")
        faq_tab = gr.Button("FAQ & About", elem_classes=["tab-button"], visible=True)

    # Navigation functions
    def nav_home():
        return {
            home_container: gr.update(visible=True),
            scan_container: gr.update(visible=False),
            results_container: gr.update(visible=False),
            dashboard_container: gr.update(visible=False),
            diy_container: gr.update(visible=False),
            faq_container: gr.update(visible=False),
            current_page: "home"
        }
    
    def nav_scan():
        return {
            home_container: gr.update(visible=False),
            scan_container: gr.update(visible=True),
            results_container: gr.update(visible=False),
            dashboard_container: gr.update(visible=False),
            diy_container: gr.update(visible=False),
            faq_container: gr.update(visible=False),
            current_page: "scan"
        }
    
    def show_loading():
        return f"""
        <div style="text-align: center; padding: 30px;">
            <p style="font-size: 1.2rem; margin-bottom: 20px; color: #e0fffa;">Analyzing your waste item</p>
            <div style="position: relative; width: 200px; height: 200px; margin: 0 auto;">
                <!-- Outer ring -->
                <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 4px solid rgba(67, 206, 162, 0.1); border-radius: 50%; border-top-color: #43cea2; animation: spin 1.5s linear infinite;"></div>
                
                <!-- Middle ring -->
                <div style="position: absolute; top: 15%; left: 15%; width: 70%; height: 70%; border: 4px solid rgba(67, 206, 162, 0.2); border-radius: 50%; border-top-color: #43cea2; animation: spin 1.2s linear infinite reverse;"></div>
                
                <!-- Inner ring -->
                <div style="position: absolute; top: 30%; left: 30%; width: 40%; height: 40%; border: 4px solid rgba(67, 206, 162, 0.3); border-radius: 50%; border-top-color: #43cea2; animation: spin 0.9s linear infinite;"></div>
                
                <!-- Center circle with recycle icon -->
                <div style="position: absolute; top: 45%; left: 45%; width: 10%; height: 10%; border-radius: 50%; background: #43cea2; display: flex; justify-content: center; align-items: center; font-size: 0.8rem; animation: pulse 2s ease-in-out infinite;">
                    ♻️
                </div>
            </div>
            <p style="margin-top: 20px; font-size: 0.9rem; color: rgba(255, 255, 255, 0.7);">
                Identifying material type and recycling instructions...
            </p>
        </div>
        <style>
            @keyframes spin {{
                to {{ transform: rotate(360deg); }}
            }}
            @keyframes pulse {{
                0% {{ transform: scale(1); }}
                50% {{ transform: scale(1.2); }}
                100% {{ transform: scale(1); }}
            }}
        </style>
    """
    
    def hide_loading():
        return gr.update(visible=False)
    
    def nav_results(image):
        return {
            home_container: gr.update(visible=False),
            scan_container: gr.update(visible=False),
            results_container: gr.update(visible=True),
            dashboard_container: gr.update(visible=False),
            diy_container: gr.update(visible=False),
            faq_container: gr.update(visible=False),
            current_page: "results",
            uploaded_image: image if image is not None else gr.State(None)
        }
    
    def nav_dashboard():
        return {
            home_container: gr.update(visible=False),
            scan_container: gr.update(visible=False),
            results_container: gr.update(visible=False),
            dashboard_container: gr.update(visible=True),
            diy_container: gr.update(visible=False),
            faq_container: gr.update(visible=False),
            current_page: "dashboard"
        }
    
    def nav_diy():
        return {
            home_container: gr.update(visible=False),
            scan_container: gr.update(visible=False),
            results_container: gr.update(visible=False),
            dashboard_container: gr.update(visible=False),
            diy_container: gr.update(visible=True),
            faq_container: gr.update(visible=False),
            current_page: "diy"
        }
    
    def nav_faq():
        return {
            home_container: gr.update(visible=False),
            scan_container: gr.update(visible=False),
            results_container: gr.update(visible=False),
            dashboard_container: gr.update(visible=False),
            diy_container: gr.update(visible=False),
            faq_container: gr.update(visible=True),
            current_page: "faq"
        }
    
    # Set up navigation events
    home_get_started_btn.click(
        nav_scan,
        outputs=[home_container, scan_container, results_container, dashboard_container, diy_container, faq_container, current_page]
    )
    
    # Scan page flow with loading indicator
    scan_btn.click(show_loading, outputs=[scan_loading])
    scan_btn.click(
        nav_results, 
        inputs=[scan_image_input],
        outputs=[home_container, scan_container, results_container, dashboard_container, diy_container, faq_container, current_page, uploaded_image]
    )
    scan_btn.click(scan_item, inputs=[scan_image_input], outputs=[results_display])
    scan_btn.click(hide_loading, outputs=[scan_loading])
    
    scan_another_btn.click(
        nav_scan,
        outputs=[home_container, scan_container, results_container, dashboard_container, diy_container, faq_container, current_page]
    )
    view_dashboard_btn.click(
        nav_dashboard,
        outputs=[home_container, scan_container, results_container, dashboard_container, diy_container, faq_container, current_page]
    )
    dashboard_scan_btn.click(
        nav_scan,
        outputs=[home_container, scan_container, results_container, dashboard_container, diy_container, faq_container, current_page]
    )
    diy_back_btn.click(
        nav_dashboard,
        outputs=[home_container, scan_container, results_container, dashboard_container, diy_container, faq_container, current_page]
    )
    faq_back_btn.click(
        nav_home,
        outputs=[home_container, scan_container, results_container, dashboard_container, diy_container, faq_container, current_page]
    )
    
    # Navigation tabs
    home_tab.click(
        nav_home,
        outputs=[home_container, scan_container, results_container, dashboard_container, diy_container, faq_container, current_page]
    )
    scan_tab.click(
        nav_scan,
        outputs=[home_container, scan_container, results_container, dashboard_container, diy_container, faq_container, current_page]
    )
    dashboard_tab.click(
        nav_dashboard,
        outputs=[home_container, scan_container, results_container, dashboard_container, diy_container, faq_container, current_page]
    )
    diy_tab.click(
        nav_diy,
        outputs=[home_container, scan_container, results_container, dashboard_container, diy_container, faq_container, current_page]
    )
    faq_tab.click(
        nav_faq,
        outputs=[home_container, scan_container, results_container, dashboard_container, diy_container, faq_container, current_page]
    )

# Launch the app
if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )