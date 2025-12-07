"""
CLI interattiva per l'agente urbanistico.
"""
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from pathlib import Path
from typing import Optional, List
import sys

# Aggiungi backend al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.agents.urban_compliance_agent import UrbanComplianceAgent
from backend.rag.vector_store import MultiLevelVectorStore
from backend.rag.document_processor import NormativeDocumentProcessor
from backend.scrapers.testo_unico_scraper import TestoUnicoScraper
from backend.scrapers.regione_lazio_scraper import RegioneLazioScraper
from backend.scrapers.comune_scraper import create_tarquinia_scraper, create_montalto_scraper

app = typer.Typer(help="🏛️ Urbanistica AI Agent - CLI")
console = Console()

# Istanze globali
agent = None
vector_store = None


def get_agent() -> UrbanComplianceAgent:
    """Ottiene istanza agente (lazy loading)."""
    global agent
    if agent is None:
        with console.status("[bold green]Inizializzazione agente..."):
            agent = UrbanComplianceAgent()
    return agent


def get_vector_store() -> MultiLevelVectorStore:
    """Ottiene istanza vector store."""
    global vector_store
    if vector_store is None:
        with console.status("[bold green]Inizializzazione vector store..."):
            vector_store = MultiLevelVectorStore()
    return vector_store


@app.command()
def ask(
    question: str = typer.Argument(..., help="Domanda sulle normative"),
    municipality: Optional[str] = typer.Option(None, "--comune", "-c", help="Comune"),
    region: str = typer.Option("Lazio", "--regione", "-r", help="Regione")
):
    """
    Fai una domanda sulle normative urbanistiche.
    """
    console.print(f"\n[bold cyan]Domanda:[/bold cyan] {question}\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        progress.add_task(description="Ricerca normative...", total=None)
        
        agent_instance = get_agent()
        answer = agent_instance.ask_question(question, municipality, region)
    
    console.print(Panel(answer, title="[bold green]Risposta", border_style="green"))


@app.command()
def analyze(
    municipality: str = typer.Option(..., "--comune", "-c", help="Comune"),
    region: str = typer.Option("Lazio", "--regione", "-r", help="Regione"),
    planimetria: Optional[Path] = typer.Option(None, "--planimetria", "-p", help="Path planimetria catastale"),
    progetto: Optional[Path] = typer.Option(None, "--progetto", "-P", help="Path progetto urbanistico"),
    foto: Optional[List[Path]] = typer.Option(None, "--foto", "-f", help="Path foto immobile")
):
    """
    Analizza un immobile per verificare la conformità urbanistica.
    """
    console.print(f"\n[bold cyan]Analisi immobile - {municipality}, {region}[/bold cyan]\n")
    
    # Verifica file
    if planimetria and not planimetria.exists():
        console.print(f"[bold red]Errore:[/bold red] Planimetria non trovata: {planimetria}")
        raise typer.Exit(1)
    
    if progetto and not progetto.exists():
        console.print(f"[bold red]Errore:[/bold red] Progetto non trovato: {progetto}")
        raise typer.Exit(1)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(description="Analisi in corso...", total=None)
        
        agent_instance = get_agent()
        result = agent_instance.analyze_property(
            municipality=municipality,
            region=region,
            planimetria_catastale=planimetria,
            progetto_urbanistico=progetto,
            foto_immobile=list(foto) if foto else None
        )
    
    # Mostra risultati
    console.print("\n[bold green]✓ Analisi completata[/bold green]\n")
    
    # Tabella difformità
    if result["compliance_result"]["difformita"]:
        table = Table(title="Difformità Rilevate")
        table.add_column("Tipo", style="cyan")
        table.add_column("Gravità", style="yellow")
        table.add_column("Descrizione", style="white")
        
        for diff in result["compliance_result"]["difformita"][:10]:  # Max 10
            table.add_row(
                diff.get("tipo", "N/A"),
                diff.get("gravita", "N/A"),
                diff.get("descrizione", "N/A")[:100] + "..."
            )
        
        console.print(table)
    else:
        console.print("[bold green]Nessuna difformità rilevata[/bold green]")
    
    # Salva report
    report_path = Path(f"report_{municipality.lower().replace(' ', '_')}.md")
    report_path.write_text(result["report"]["content"], encoding="utf-8")
    console.print(f"\n[bold blue]Report salvato:[/bold blue] {report_path}")


@app.command()
def update_norms():
    """
    Aggiorna le normative scaricando le ultime versioni.
    """
    console.print("\n[bold cyan]Aggiornamento normative[/bold cyan]\n")
    
    scrapers = [
        ("Testo Unico Edilizia", TestoUnicoScraper()),
        ("Regione Lazio", RegioneLazioScraper()),
        ("Comune Tarquinia", create_tarquinia_scraper()),
        ("Comune Montalto di Castro", create_montalto_scraper())
    ]
    
    total_files = 0
    
    with Progress(console=console) as progress:
        task = progress.add_task("[cyan]Download normative...", total=len(scrapers))
        
        for name, scraper in scrapers:
            try:
                console.print(f"[yellow]Scaricando {name}...[/yellow]")
                files = scraper.scrape()
                total_files += len(files)
                console.print(f"[green]✓ {name}: {len(files)} file[/green]")
            except Exception as e:
                console.print(f"[red]✗ {name}: {e}[/red]")
            
            progress.advance(task)
    
    console.print(f"\n[bold green]✓ Scaricati {total_files} file totali[/bold green]")


@app.command()
def index_norms(
    directory: Path = typer.Argument(..., help="Directory con normative da indicizzare"),
    level: str = typer.Option(..., "--level", "-l", help="Livello (nazionale/regionale/comunale)"),
    region: Optional[str] = typer.Option(None, "--regione", "-r", help="Regione"),
    municipality: Optional[str] = typer.Option(None, "--comune", "-c", help="Comune")
):
    """
    Indicizza normative nel vector database.
    """
    if not directory.exists():
        console.print(f"[bold red]Errore:[/bold red] Directory non trovata: {directory}")
        raise typer.Exit(1)
    
    console.print(f"\n[bold cyan]Indicizzazione normative da {directory}[/bold cyan]\n")
    
    with Progress(console=console) as progress:
        task = progress.add_task("[cyan]Processing documenti...", total=None)
        
        # Processa documenti
        processor = NormativeDocumentProcessor()
        chunks = processor.process_directory(
            directory,
            level,
            region,
            municipality
        )
        
        progress.update(task, description="[cyan]Indicizzazione...")
        
        # Indicizza
        vs = get_vector_store()
        vs.add_documents(chunks, level)
    
    console.print(f"\n[bold green]✓ Indicizzati {len(chunks)} chunk[/bold green]")


@app.command()
def stats():
    """
    Mostra statistiche sul database normative.
    """
    console.print("\n[bold cyan]Statistiche Database Normative[/bold cyan]\n")
    
    vs = get_vector_store()
    
    table = Table(title="Statistiche per Livello")
    table.add_column("Livello", style="cyan")
    table.add_column("Documenti", style="green")
    table.add_column("Modello Embedding", style="yellow")
    
    total = 0
    for level, store in vs.stores.items():
        stats = store.get_collection_stats()
        table.add_row(
            level.capitalize(),
            str(stats["total_documents"]),
            stats["embedding_model"]
        )
        total += stats["total_documents"]
    
    console.print(table)
    console.print(f"\n[bold green]Totale documenti: {total}[/bold green]")


@app.command()
def chat():
    """
    Modalità chat interattiva.
    """
    console.print(Panel(
        "[bold cyan]Urbanistica AI Agent - Chat Interattiva[/bold cyan]\n"
        "Fai domande sulle normative urbanistiche.\n"
        "Digita 'exit' o 'quit' per uscire.",
        border_style="cyan"
    ))
    
    agent_instance = get_agent()
    
    while True:
        try:
            question = console.input("\n[bold green]Tu:[/bold green] ")
            
            if question.lower() in ["exit", "quit", "esci"]:
                console.print("[bold yellow]Arrivederci![/bold yellow]")
                break
            
            if not question.strip():
                continue
            
            with console.status("[bold green]Pensando..."):
                answer = agent_instance.chat(question)
            
            console.print(f"\n[bold cyan]Agente:[/bold cyan] {answer}")
            
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Arrivederci![/bold yellow]")
            break
        except Exception as e:
            console.print(f"[bold red]Errore:[/bold red] {e}")


if __name__ == "__main__":
    app()
