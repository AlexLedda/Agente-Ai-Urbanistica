"""
Generatore report di conformità urbanistica.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from loguru import logger

from backend.models.llm_router import LLMRouter, TaskType
from backend.models.prompt_templates import PromptTemplates


class ReportGenerator:
    """Generatore report professionali di conformità."""
    
    def __init__(self, router: LLMRouter):
        """
        Inizializza il generatore.
        
        Args:
            router: Router LLM
        """
        self.router = router
        logger.info("Report Generator inizializzato")
    
    def generate_report(
        self,
        compliance_result: Dict[str, Any],
        document_analysis: Dict[str, Any],
        normative_context: str,
        municipality: str,
        region: str,
        output_format: str = "markdown"
    ) -> Dict[str, Any]:
        """
        Genera report completo di conformità.
        
        Args:
            compliance_result: Risultati verifica conformità
            document_analysis: Analisi documenti
            normative_context: Contesto normativo
            municipality: Comune
            region: Regione
            output_format: Formato output (markdown, html, pdf)
            
        Returns:
            Report generato
        """
        logger.info(f"Generazione report per {municipality}")
        
        # Prepara dati per il report
        analysis_data = {
            "municipality": municipality,
            "region": region,
            "compliance_analysis": compliance_result.get("analysis", ""),
            "difformita": compliance_result.get("difformita", []),
            "document_analysis": document_analysis,
            "normative_context": normative_context,
            "date": datetime.now().strftime("%d/%m/%Y")
        }
        
        # Usa prompt template per generazione
        prompt = PromptTemplates.format_prompt(
            PromptTemplates.REPORT_GENERATION,
            analysis_data=str(analysis_data),
            date=analysis_data["date"]
        )
        
        # Genera report con LLM
        report_content = self.router.analyze_with_best_model(
            prompt,
            TaskType.REPORT_GENERATION,
            system_message=PromptTemplates.get_system_message("report_writer")
        )
        
        # Formatta secondo il formato richiesto
        if output_format == "markdown":
            formatted_report = self._format_markdown(report_content)
        elif output_format == "html":
            formatted_report = self._format_html(report_content)
        else:
            formatted_report = report_content
        
        report = {
            "content": formatted_report,
            "format": output_format,
            "metadata": {
                "municipality": municipality,
                "region": region,
                "generation_date": datetime.now().isoformat(),
                "difformita_count": len(compliance_result.get("difformita", []))
            }
        }
        
        logger.success("Report generato")
        return report
    
    def _format_markdown(self, content: str) -> str:
        """Formatta report in Markdown."""
        # Il contenuto è già in markdown dal LLM
        return content
    
    def _format_html(self, content: str) -> str:
        """Converte report Markdown in HTML."""
        try:
            import markdown
            html = markdown.markdown(content, extensions=['tables', 'fenced_code'])
            
            # Aggiungi CSS
            styled_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Report Conformità Urbanistica</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        h3 {{ color: #7f8c8d; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #3498db; color: white; }}
        .warning {{ background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; }}
        .info {{ background-color: #d1ecf1; padding: 15px; border-left: 4px solid #17a2b8; }}
    </style>
</head>
<body>
{html}
</body>
</html>
"""
            return styled_html
        except ImportError:
            logger.warning("Modulo markdown non disponibile, ritorno testo plain")
            return content
    
    def save_report(
        self,
        report: Dict[str, Any],
        output_path: Path
    ) -> Path:
        """
        Salva report su file.
        
        Args:
            report: Report da salvare
            output_path: Path output
            
        Returns:
            Path al file salvato
        """
        logger.info(f"Salvataggio report: {output_path}")
        
        # Determina estensione
        if report["format"] == "html":
            output_path = output_path.with_suffix(".html")
        else:
            output_path = output_path.with_suffix(".md")
        
        # Salva
        output_path.write_text(report["content"], encoding="utf-8")
        
        # Salva anche metadati
        import json
        metadata_path = output_path.with_suffix(".meta.json")
        metadata_path.write_text(
            json.dumps(report["metadata"], indent=2),
            encoding="utf-8"
        )
        
        logger.success(f"Report salvato: {output_path}")
        return output_path
