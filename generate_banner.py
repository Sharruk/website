from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np

def create_college_banner():
    # Create figure and axis
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Create gradient background
    gradient = np.linspace(0, 1, 256).reshape(256, -1)
    gradient = np.vstack((gradient, gradient))
    
    # Background with tech-themed gradient
    ax.imshow(gradient, extent=[0, 16, 0, 10], aspect='auto', 
              cmap='Blues', alpha=0.3)
    
    # Add geometric background elements
    circle1 = plt.Circle((2, 8), 1.5, color='lightblue', alpha=0.2)
    circle2 = plt.Circle((14, 2), 1.2, color='lightcyan', alpha=0.2)
    circle3 = plt.Circle((13, 8), 0.8, color='lightsteelblue', alpha=0.2)
    ax.add_patch(circle1)
    ax.add_patch(circle2)
    ax.add_patch(circle3)
    
    # Add header
    ax.text(8, 9, 'COLLEGE DEGREE PROGRAMS', 
            fontsize=28, fontweight='bold', ha='center', va='center',
            color='#1e3a8a', family='serif')
    
    ax.text(8, 8.3, 'Excellence in Education & Technology', 
            fontsize=16, ha='center', va='center',
            color='#374151', style='italic')
    
    # Define degree programs
    programs = [
        {'name': 'B.E CSE', 'full': 'Computer Science & Engineering', 'color': '#3b82f6', 'icon': '💻'},
        {'name': 'B.Tech IT', 'full': 'Information Technology', 'color': '#10b981', 'icon': '🌐'},
        {'name': 'B.E EEE', 'full': 'Electrical & Electronics Engineering', 'color': '#f59e0b', 'icon': '⚡'},
        {'name': 'B.E Mechanical', 'full': 'Mechanical Engineering', 'color': '#ef4444', 'icon': '⚙️'},
        {'name': 'B.Sc Computer Science', 'full': 'Computer Science', 'color': '#8b5cf6', 'icon': '🔬'},
        {'name': 'B.Com General', 'full': 'Commerce General', 'color': '#06b6d4', 'icon': '📊'}
    ]
    
    # Create program cards in a 2x3 grid
    positions = [
        (2.5, 6), (8, 6), (13.5, 6),  # Top row
        (2.5, 3), (8, 3), (13.5, 3)   # Bottom row
    ]
    
    for i, (program, pos) in enumerate(zip(programs, positions)):
        x, y = pos
        
        # Create fancy box for each program
        box = FancyBboxPatch((x-2, y-1.2), 4, 2.4,
                            boxstyle="round,pad=0.1",
                            facecolor='white',
                            edgecolor=program['color'],
                            linewidth=2,
                            alpha=0.9)
        ax.add_patch(box)
        
        # Add program icon (using text representation)
        ax.text(x-1.3, y+0.5, program['icon'], fontsize=24, ha='center', va='center')
        
        # Add program name
        ax.text(x, y+0.5, program['name'], 
                fontsize=16, fontweight='bold', ha='center', va='center',
                color=program['color'])
        
        # Add full program name
        ax.text(x, y-0.2, program['full'], 
                fontsize=10, ha='center', va='center',
                color='#374151', wrap=True)
        
        # Add decorative elements
        ax.plot([x-1.8, x+1.8], [y-0.7, y-0.7], 
                color=program['color'], linewidth=2, alpha=0.5)
    
    # Add footer elements
    ax.text(8, 0.8, '🎓 Shape Your Future with Quality Education 🎓', 
            fontsize=14, ha='center', va='center',
            color='#374151', weight='bold')
    
    # Add decorative border
    border = plt.Rectangle((0.2, 0.2), 15.6, 9.6, 
                          fill=False, edgecolor='#1e3a8a', linewidth=3)
    ax.add_patch(border)
    
    # Save the image
    plt.tight_layout()
    plt.savefig('college_programs_banner.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    print("College degree programs banner created successfully!")
    print("Saved as: college_programs_banner.png")

if __name__ == "__main__":
    create_college_banner()