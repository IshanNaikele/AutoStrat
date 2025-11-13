# visualize_graph.py
from backend.agents import graph_app

def generate_graph_image():
    print("🎨 Generating Graph Visualization...")
    
    try:
        # 1. Get the graph object
        graph = graph_app.get_graph()
        
        # 2. Generate the PNG binary data (draw_mermaid_png)
        # Note: This connects to a mermaid API service to render the image
        image_data = graph.draw_mermaid_png()
        
        # 3. Save to a file
        output_file = "autostrat_workflow.png"
        with open(output_file, "wb") as f:
            f.write(image_data)
            
        print(f"✅ Success! Graph saved as '{output_file}'")
        print("👉 Go open that file to see your agent logic.")
        
    except Exception as e:
        print(f"❌ Error generating graph: {e}")
        print("Tip: You might need to install: pip install pygraphviz (optional but helps)")

if __name__ == "__main__":
    generate_graph_image()