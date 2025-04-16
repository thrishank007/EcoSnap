import gradio as gr
import numpy as np
import pandas as pd
import random
import time
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64
from PIL import Image

# Custom CSS for the Earth to Sky theme
custom_css = """
#component-0 {
background: linear-gradient(135deg, #0a192f 0%, #145959 100%);
border-radius: 10px;
padding: 20px;
}
.gradio-container {
background: linear-gradient(135deg, #0a192f 0%, #145959 100%);
color: white;3;
}
.tabs {
background: rgba(10, 25, 47, 0.5);3);
border-radius: 10px;
box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
backdrop-filter: blur(5px);
border: 1px solid rgba(10, 25, 47, 0.3);5);
}
.tab-button {
background: transparent;
color: white;3;
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
color: white;3;
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

# Mock data for demonstration
waste_types = ["Plastic", "Paper", "Glass", "Metal", "Organic", "E-waste", "Hazardous"]
recycling_instructions = {
    "Plastic": {
        "title": "Recyclable Plastic",
        "instructions": "Rinse the container. Remove caps and labels if possible. Place in recycling bin designated for plastics.",
        "tips": "Avoid single-use plastics. Consider reusable alternatives.",
        "image": "https://images.unsplash.com/photo-1605600659873-d808a13e4d23?q=80&w=500"
    },
    "Paper": {
        "title": "Paper Waste",
        "instructions": "Remove any non-paper attachments. Flatten cardboard boxes. Place in paper recycling bin.",
        "tips": "Use digital alternatives when possible. Print on both sides of paper.",
        "image": "https://images.unsplash.com/photo-1589634749362-a6e6577856df?q=80&w=500"
    },
    "Glass": {
        "title": "Glass",
        "instructions": "Rinse thoroughly. Remove caps and lids. Sort by color if required in your area.",
        "tips": "Glass can be recycled infinitely without quality loss. Choose glass over plastic when possible.",
        "image": "https://images.unsplash.com/photo-1605001015592-99a2210e279c?q=80&w=500"
    },
    "Metal": {
        "title": "Metal",
        "instructions": "Rinse to remove food residue. Crush if possible to save space.",
        "tips": "Metals are highly recyclable. Separate different metal types if possible.",
        "image": "https://images.unsplash.com/photo-1533521718263-371de3e46c30?q=80&w=500"
    },
    "Organic": {
        "title": "Organic Waste",
        "instructions": "Compost if possible. Otherwise place in designated organic waste bin.",
        "tips": "Consider home composting. Avoid mixing with non-organic waste.",
        "image": "https://images.unsplash.com/photo-1593369196682-6d8ec9ff2124?q=80&w=500"
    },
    "E-waste": {
        "title": "Electronic Waste",
        "instructions": "Do not place in regular trash. Find a designated e-waste collection point.",
        "tips": "E-waste contains valuable materials that can be recovered. Consider donating working electronics.",
        "image": "https://images.unsplash.com/photo-1602086252751-8c27254e7477?q=80&w=500"
    },
    "Hazardous": {
        "title": "Hazardous Waste",
        "instructions": "Never mix with regular trash. Take to special collection facilities.",
        "tips": "Store safely away from children and pets. Look for eco-friendly alternatives.",
        "image": "https://images.unsplash.com/photo-1612965607446-25e1332775ae?q=80&w=500"
    }
}

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
        "title": "Cardboard Organizers",
        "materials": "Cardboard boxes, scissors, glue, decorative paper",
        "difficulty": "Medium",
        "description": "Create desk organizers from cardboard boxes, customized with decorative paper."
    },
    {
        "title": "Tin Can Luminaries",
        "materials": "Tin cans, hammer, nails, tea lights",
        "difficulty": "Medium",
        "description": "Make beautiful luminaries by creating patterns of holes in tin cans."
    }
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

# Helper functions
def classify_waste(image):
    """Mock function to classify waste from an image"""
    # In a real app, this would call a trained model
    time.sleep(2)  # Simulate processing time
    waste_type = random.choice(waste_types)
    confidence = random.uniform(0.7, 0.98)
    return waste_type, confidence

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
    diy_html = """
    <h1 class='heading'>DIY Upcycling Ideas</h1>
    <p class='subheading'>Give your waste items a second life with these creative projects</p>
    <div style="display: flex; flex-wrap: wrap; justify-content: space-around; gap: 20px;">
    """
    
    for idea in diy_ideas:
        difficulty_color = "#4CAF50" if idea["difficulty"] == "Easy" else "#FFC107" if idea["difficulty"] == "Medium" else "#F44336"
        
        diy_html += f"""
        <div class="eco-card" style="width: 300px;">
            <h3 style="color: #9cffe0; margin-bottom: 10px;">{idea["title"]}</h3>
            <p><strong>Materials:</strong> {idea["materials"]}</p>
            <p><strong>Difficulty:</strong> <span style="color: {difficulty_color};">{idea["difficulty"]}</span></p>
            <p>{idea["description"]}</p>
        </div>
        """
    
    diy_html += """
    </div>
    """
    
    return [
        gr.HTML(diy_html),
        gr.Button("Back to Dashboard", elem_classes=["btn"]),
    ]

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
    # This function would typically call a machine learning model
    if image is None:
        return gr.HTML.update(value="<p>Please upload an image first</p>", visible=True)
    
    waste_type, confidence = classify_waste(image)
    info = recycling_instructions[waste_type]
    
    # Calculate confidence color: green for high, yellow for medium, red for low
    conf_color = "#4CAF50" if confidence > 0.85 else "#FFC107" if confidence > 0.7 else "#F44336"
    
    result_html = f"""
    <div class="eco-card" style="animation: fadeIn 0.5s ease-out;">
        <div style="display: flex; flex-wrap: wrap; align-items: start; gap: 25px;">
            <div style="flex: 1; min-width: 280px;">
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                    <h2 style="color: #e0fffa; margin: 0; font-size: 1.8rem;">{info['title']}</h2>
                    <div style="margin-left: 15px; background: rgba(67, 206, 162, 0.2); display: inline-flex; padding: 8px 15px; border-radius: 20px; align-items: center;">
                        <div class="progress-bar" style="width: 100px; height: 8px; margin: 0 10px 0 0;">
                            <div class="progress-bar-fill" style="width: {confidence*100}%; background: {conf_color};"></div>
                        </div>
                        <span style="color: {conf_color}; font-weight: bold;">{confidence:.1%}</span>
                    </div>
                </div>
                
                <div style="background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 20px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #43cea2; display: flex; align-items: center;">
                        <span style="background: rgba(67, 206, 162, 0.2); width: 30px; height: 30px; border-radius: 50%; display: inline-flex; justify-content: center; align-items: center; margin-right: 10px;">1</span>
                        How to Recycle
                    </h3>
                    <p style="line-height: 1.6;">{info['instructions']}</p>
                    
                    <h3 style="color: #43cea2; display: flex; align-items: center;">
                        <span style="background: rgba(67, 206, 162, 0.2); width: 30px; height: 30px; border-radius: 50%; display: inline-flex; justify-content: center; align-items: center; margin-right: 10px;">2</span>
                        Eco-Friendly Tips
                    </h3>
                    <p style="line-height: 1.6;">{info['tips']}</p>
                    
                    <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 25px;">
                        <div class="eco-badge">✅ Recyclable</div>
                        <div class="eco-badge">♻️ {waste_type}</div>
                        <div class="eco-badge">🌱 Eco-friendly</div>
                    </div>
                </div>
                
                <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 20px;">
                    <button onclick="document.getElementById('diy-tab-button').click()" class="btn" style="display: flex; align-items: center;">
                        <span style="margin-right: 8px;">🔄</span> Upcycle Ideas
                    </button>
                    
                    <button onclick="alert('Added to your tracker!')" class="btn" style="background: linear-gradient(90deg, #1a4971 0%, #36b9cc 100%);">
                        <span style="margin-right: 8px;">➕</span> Add to Tracker
                    </button>
                </div>
                
                <div style="background: rgba(24, 90, 157, 0.2); border-radius: 12px; padding: 15px; margin-top: 20px;">
                    <div style="display: flex; align-items: center;">
                        <div style="width: 40px; height: 40px; border-radius: 50%; background: rgba(67, 206, 162, 0.2); display: flex; justify-content: center; align-items: center; margin-right: 10px;">
                            🌍
                        </div>
                        <div>
                            <h4 style="margin: 0 0 5px 0; color: #e0fffa;">Environmental Impact</h4>
                            <p style="margin: 0; font-size: 0.9rem;">Recycling this item saves ~{round(random.uniform(0.1, 2.0), 2)} kg CO₂</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div style="flex: 1; min-width: 280px;">
                <img src="{info['image']}" style="width: 100%; border-radius: 12px; box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3); transition: all 0.3s ease;" 
                    onmouseover="this.style.transform='scale(1.02)'" 
                    onmouseout="this.style.transform='scale(1)'" 
                    alt="{waste_type} recycling">
                
                <div style="background: rgba(67, 206, 162, 0.15); border-radius: 12px; padding: 15px; margin-top: 20px;">
                    <h4 style="margin: 0 0 10px 0; color: #e0fffa;">Similar Items</h4>
                    <div style="display: flex; gap: 10px; overflow-x: auto; padding-bottom: 10px;">
                        <div class="eco-badge" style="cursor: pointer;">Plastic Bottles</div>
                        <div class="eco-badge" style="cursor: pointer;">Food Containers</div>
                        <div class="eco-badge" style="cursor: pointer;">Packaging</div>
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
    
    # In a real application, you would update user stats here
    
    return gr.HTML.update(value=result_html, visible=True)

# Main Application
with gr.Blocks(css=custom_css) as app:
    # Current state
    current_page = gr.State("home")
    uploaded_image = gr.State(None)
    
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
            scan_another_btn = results_components[2]
            view_dashboard_btn = results_components[3]
        
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
        return gr.HTML.update(value="""
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
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.2); }
                100% { transform: scale(1); }
            }
        </style>
    """, visible=True)
    
    def hide_loading():
        return gr.HTML.update(visible=False)
    
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
    app.launch()