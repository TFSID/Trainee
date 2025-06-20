"""
Gradio interface for CVE Analyst
"""
import gradio as gr
from config.settings import CVEConfig
from api.cve_analyst_api import CVEAnalystAPI

def create_gradio_interface(config: CVEConfig):
    """Create Gradio interface"""
    analyst = CVEAnalystAPI(config)
    
    def analyze_cve_gradio(cve_id: str, instruction: str):
        """Analyze CVE for Gradio interface"""
        if not cve_id.strip():
            return "Please enter a CVE ID"
        
        return analyst.analyze_cve(cve_id.strip(), instruction)
    
    def get_recent_cves_gradio():
        """Get recent CVEs for display"""
        recent_cves = analyst.get_recent_cves(limit=20)
        if not recent_cves:
            return "No recent CVEs found"
        
        result = "**Recent CVEs:**\n\n"
        for cve in recent_cves:
            result += f"- **{cve['cve_id']}** (Severity: {cve['severity']})\n"
            result += f"  {cve['description'][:100]}...\n\n"
        
        return result
    
    # Create interface
    with gr.Blocks(title="CVE Security Analyst") as interface:
        gr.Markdown("# CVE Security Analyst")
        gr.Markdown("AI-powered CVE analysis and security recommendations")
        
        with gr.Tab("CVE Analysis"):
            with gr.Row():
                with gr.Column():
                    cve_input = gr.Textbox(
                        label="CVE ID", 
                        placeholder="CVE-2024-XXXX",
                        value="CVE-2024-1234"
                    )
                    instruction_input = gr.Textbox(
                        label="Analysis Instruction", 
                        value="Analyze this CVE and provide security recommendations",
                        lines=3
                    )
                    analyze_btn = gr.Button("Analyze CVE", variant="primary")
                
                with gr.Column():
                    analysis_output = gr.Textbox(
                        label="Analysis Result", 
                        lines=20,
                        max_lines=30
                    )
            
            analyze_btn.click(
                fn=analyze_cve_gradio,
                inputs=[cve_input, instruction_input],
                outputs=analysis_output
            )
        
        with gr.Tab("Recent CVEs"):
            with gr.Row():
                refresh_btn = gr.Button("Refresh Recent CVEs")
                recent_output = gr.Markdown()
            
            refresh_btn.click(
                fn=get_recent_cves_gradio,
                outputs=recent_output
            )
        
        # Load recent CVEs on startup
        interface.load(
            fn=get_recent_cves_gradio,
            outputs=recent_output
        )
    
    return interface
